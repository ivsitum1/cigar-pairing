#!/usr/bin/env python3
"""Extract PaddleOCR-main.zip into 40_operations/vendor/PaddleOCR/."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
VENDOR_DIR = WORKSPACE / "40_operations" / "vendor" / "PaddleOCR"
DEFAULT_ZIP = Path(os.environ.get("USERPROFILE", "")) / "Downloads" / "PaddleOCR-main.zip"
ZIP_PREFIX = "PaddleOCR-main/"


def extract_vendor(zip_path: Path, dest: Path, *, force: bool) -> None:
    if not zip_path.is_file():
        raise FileNotFoundError(f"Zip not found: {zip_path}")

    marker = dest / "pyproject.toml"
    if marker.is_file() and not force:
        print(f"Vendor already present: {dest}", flush=True)
        return

    if dest.exists() and force:
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        members = [n for n in zf.namelist() if n.startswith(ZIP_PREFIX) and not n.endswith("/")]
        total = len(members)
        for i, name in enumerate(members, 1):
            rel = name[len(ZIP_PREFIX) :]
            if not rel:
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
            if i % 500 == 0 or i == total:
                print(f"  extracted {i}/{total}", flush=True)

    if not marker.is_file():
        raise RuntimeError(f"Extraction incomplete: missing {marker}")
    print(f"OK — vendor at {dest}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap PaddleOCR vendor from zip.")
    parser.add_argument(
        "--zip",
        type=Path,
        default=Path(os.environ.get("PADDLEOCR_ZIP", str(DEFAULT_ZIP))),
        help="Path to PaddleOCR-main.zip",
    )
    parser.add_argument("--force", action="store_true", help="Re-extract even if vendor exists")
    args = parser.parse_args()

    try:
        extract_vendor(args.zip.resolve(), VENDOR_DIR, force=args.force)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
