"""Band reference storage + visual matching (CLIP when available, phash fallback)."""
from __future__ import annotations

import io
import json
import logging
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .config import BAND_DIR

log = logging.getLogger("band")

_SAFE_ID = re.compile(r"^[\w.@+-]+$")

_clip_model: Any | None = None
_clip_preprocess: Any | None = None
_clip_tried = False


@dataclass
class BandHit:
    cigar_id: str
    score: float
    ref_id: str


def _cigar_dir(cigar_id: str) -> Path:
    if not _SAFE_ID.match(cigar_id):
        raise ValueError("invalid cigar_id")
    d = BAND_DIR / cigar_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _meta_path(cigar_id: str) -> Path:
    return _cigar_dir(cigar_id) / "meta.json"


def _load_meta(cigar_id: str) -> dict[str, Any]:
    p = _meta_path(cigar_id)
    if not p.exists():
        return {"refs": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _save_meta(cigar_id: str, meta: dict[str, Any]) -> None:
    _meta_path(cigar_id).write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _try_load_clip() -> bool:
    global _clip_model, _clip_preprocess, _clip_tried
    if _clip_tried:
        return _clip_model is not None
    _clip_tried = True
    try:
        import open_clip  # type: ignore
        import torch  # type: ignore

        model, _, preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="openai"
        )
        model.eval()
        _clip_model = (model, torch)
        _clip_preprocess = preprocess
        log.info("open_clip loaded for band embeddings")
        return True
    except Exception as e:  # noqa: BLE001
        log.warning("open_clip unavailable (%s); using perceptual hash", e)
        _clip_model = None
        return False


def _embed_phash(image: Image.Image) -> np.ndarray:
    import imagehash

    h = imagehash.phash(image, hash_size=16)
    bits = np.array(h.hash, dtype=np.float32).flatten()
    # append coarse color histogram for foil/cream bands
    small = image.convert("RGB").resize((32, 32))
    hist = np.array(small.histogram(), dtype=np.float32)
    hist = hist / (hist.sum() + 1e-6)
    vec = np.concatenate([bits, hist])
    n = np.linalg.norm(vec) + 1e-9
    return vec / n


def _embed_clip(image: Image.Image) -> np.ndarray:
    model, torch = _clip_model
    preprocess = _clip_preprocess
    with torch.no_grad():
        t = preprocess(image).unsqueeze(0)
        feat = model.encode_image(t)
        feat = feat / feat.norm(dim=-1, keepdim=True)
        return feat.cpu().numpy().astype(np.float32).flatten()


def embed_image(image: Image.Image) -> tuple[np.ndarray, str]:
    if _try_load_clip():
        return _embed_clip(image.convert("RGB")), "clip"
    return _embed_phash(image.convert("RGB")), "phash"


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9))


def add_reference(cigar_id: str, data: bytes) -> dict[str, Any]:
    image = Image.open(io.BytesIO(data)).convert("RGB")
    vec, method = embed_image(image)
    ref_id = uuid.uuid4().hex[:12]
    folder = _cigar_dir(cigar_id)
    img_path = folder / f"{ref_id}.jpg"
    emb_path = folder / f"{ref_id}.npy"
    image.save(img_path, format="JPEG", quality=88)
    np.save(emb_path, vec)
    meta = _load_meta(cigar_id)
    meta["refs"].append({"id": ref_id, "method": method, "file": img_path.name})
    _save_meta(cigar_id, meta)
    return {"cigar_id": cigar_id, "ref_id": ref_id, "method": method}


def list_references(cigar_id: str | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if cigar_id:
        ids = [cigar_id] if (_SAFE_ID.match(cigar_id) and (_cigar_dir(cigar_id)).exists()) else []
    else:
        ids = [p.name for p in BAND_DIR.iterdir() if p.is_dir()]
    for cid in ids:
        meta = _load_meta(cid)
        for r in meta.get("refs", []):
            out.append({"cigar_id": cid, **r})
    return out


def match_image(data: bytes, top_k: int = 5) -> list[BandHit]:
    image = Image.open(io.BytesIO(data)).convert("RGB")
    query, _method = embed_image(image)
    hits: list[BandHit] = []
    for cid_dir in BAND_DIR.iterdir():
        if not cid_dir.is_dir():
            continue
        for npy in cid_dir.glob("*.npy"):
            ref_vec = np.load(npy)
            # align dims if clip vs phash mix
            if ref_vec.shape != query.shape:
                continue
            score = cosine(query, ref_vec)
            hits.append(BandHit(cigar_id=cid_dir.name, score=score, ref_id=npy.stem))
    hits.sort(key=lambda h: h.score, reverse=True)
    # collapse to best per cigar_id
    best: dict[str, BandHit] = {}
    for h in hits:
        if h.cigar_id not in best:
            best[h.cigar_id] = h
    ranked = sorted(best.values(), key=lambda h: h.score, reverse=True)
    return ranked[:top_k]


def band_status() -> dict[str, Any]:
    clip = _try_load_clip()
    n_refs = len(list_references())
    return {
        "clip": clip,
        "method": "clip" if clip else "phash",
        "references": n_refs,
    }
