from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_CSV = ROOT / "30_system" / "docs" / "local_source_classified.csv"
TARGET_ROOT = ROOT / "20_knowledge" / "reference_library"
REPORT_PATH = ROOT / "30_system" / "docs" / "added_local_sources.json"
TARGET_PER_DOMAIN = 50

DOMAIN_DIRS = {
    "anesthesiology": TARGET_ROOT / "medicine" / "anesthesiology",
    "emergency": TARGET_ROOT / "medicine" / "emergency",
    "intensive_care": TARGET_ROOT / "medicine" / "intensive_care",
    "statistics": TARGET_ROOT / "statistics" / "books" / "local_collection",
    "scientific_writing": TARGET_ROOT / "writing" / "books_and_guides",
}

EXT_PRIORITY = {".pdf": 0, ".epub": 1, ".docx": 2, ".txt": 3}
INVALID_NAME = re.compile(r"^~\$")


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")
    return cleaned[:180] or "file"


def file_hash(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()[:12]


def main() -> None:
    for d in DOMAIN_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)

    rows = []
    with SOURCE_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            src = Path(row["path"])
            if not src.exists() or not src.is_file():
                continue
            if INVALID_NAME.search(src.name):
                continue
            ext = src.suffix.lower()
            if ext not in EXT_PRIORITY:
                continue
            row["_ext_rank"] = EXT_PRIORITY[ext]
            rows.append(row)

    rows.sort(key=lambda r: (r["_ext_rank"], r.get("name", "").lower()))

    selected: dict[str, list[dict[str, str]]] = {k: [] for k in DOMAIN_DIRS}
    seen_src: set[str] = set()
    for row in rows:
        for domain in row["domains"].split(";"):
            if domain not in DOMAIN_DIRS:
                continue
            if len(selected[domain]) >= TARGET_PER_DOMAIN:
                continue
            src = row["path"]
            key = f"{domain}:{src}"
            if key in seen_src:
                continue
            seen_src.add(key)
            selected[domain].append(row)

    copied = {k: [] for k in DOMAIN_DIRS}
    for domain, domain_rows in selected.items():
        target_dir = DOMAIN_DIRS[domain]
        for row in domain_rows:
            src = Path(row["path"])
            try:
                hash_suffix = file_hash(src)
            except OSError:
                continue
            dst_name = f"{safe_name(src.stem)}__{hash_suffix}{src.suffix.lower()}"
            dst = target_dir / dst_name
            if not dst.exists():
                try:
                    shutil.copy2(src, dst)
                except OSError:
                    continue
            copied[domain].append({"src": str(src), "dst": str(dst.relative_to(ROOT))})

    REPORT_PATH.write_text(json.dumps(copied, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: len(v) for k, v in copied.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
