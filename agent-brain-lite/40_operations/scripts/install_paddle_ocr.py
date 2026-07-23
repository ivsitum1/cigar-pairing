#!/usr/bin/env python3
"""Install PaddleOCR vendor, PaddlePaddle (GPU/CPU auto), and OCR extras."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
VENDOR = WORKSPACE / "40_operations" / "vendor" / "PaddleOCR"
BOOTSTRAP = WORKSPACE / "40_operations" / "scripts" / "bootstrap_paddleocr_vendor.py"
REQ_OCR = WORKSPACE / "40_operations" / "requirements-ocr.txt"
PY_ROOT = WORKSPACE / "40_operations" / "python"

sys.path.insert(0, str(PY_ROOT))
from pdf_extraction.device import (  # noqa: E402
    PADDLEPADDLE_VERSION,
    paddlex_ocr_pip_spec,
    paddlepaddle_pip_spec,
)


def _run(cmd: list[str], *, cwd: Path) -> None:
    print(">", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd), check=True)


def _check_python_version() -> int | None:
    """PaddlePaddle wheels: typically Python 3.8–3.12 (see PaddleOCR docs)."""
    v = sys.version_info
    if v.major == 3 and 8 <= v.minor <= 12:
        return None
    print(
        f"ERROR: Python {v.major}.{v.minor} is not supported by PaddlePaddle wheels.\n"
        "Install Python 3.11 or 3.12 (e.g. py install 3.12) and re-run with that interpreter.\n"
        "See 40_operations/vendor/README.md",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    if (code := _check_python_version()) is not None:
        return code

    parser = argparse.ArgumentParser(description="Install PaddleOCR stack for PDF extraction.")
    parser.add_argument("--skip-bootstrap", action="store_true", help="Skip vendor zip extraction")
    parser.add_argument("--cpu-only", action="store_true", help="Force CPU PaddlePaddle")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip import smoke test")
    args = parser.parse_args()

    if not args.skip_bootstrap:
        if not (VENDOR / "pyproject.toml").is_file():
            print("=== bootstrap vendor ===", flush=True)
            _run([sys.executable, str(BOOTSTRAP)], cwd=WORKSPACE)
        else:
            print(f"Vendor present: {VENDOR}", flush=True)

    device = "cpu" if args.cpu_only else "gpu"  # auto: try GPU wheel first, fallback below

    pkg, extra_args = paddlepaddle_pip_spec(device)
    print(f"=== install PaddlePaddle ({device}) ===", flush=True)
    try:
        _run([sys.executable, "-m", "pip", "install", pkg, *extra_args], cwd=WORKSPACE)
    except subprocess.CalledProcessError:
        if device == "gpu":
            print("GPU install failed; falling back to CPU.", flush=True)
            pkg, extra_args = paddlepaddle_pip_spec("cpu")
            _run([sys.executable, "-m", "pip", "install", pkg, *extra_args], cwd=WORKSPACE)
        else:
            raise

    print("=== install paddleocr ===", flush=True)
    env = os.environ.copy()
    env["SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PADDLEOCR"] = "3.5.0"
    if (VENDOR / ".git").is_dir():
        _run([sys.executable, "-m", "pip", "install", "-e", str(VENDOR)], cwd=WORKSPACE)
    else:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", str(VENDOR)],
                cwd=str(WORKSPACE),
                check=True,
                env=env,
            )
        except subprocess.CalledProcessError:
            print("Editable vendor failed; installing paddleocr from PyPI.", flush=True)
            _run(
                [sys.executable, "-m", "pip", "install", "paddleocr>=3.5.0,<3.6.0"],
                cwd=WORKSPACE,
            )

    print("=== install OCR extras ===", flush=True)
    _run([sys.executable, "-m", "pip", "install", "-r", str(REQ_OCR)], cwd=WORKSPACE)

    print(
        f"=== install paddlex OCR pipeline deps ({paddlex_ocr_pip_spec()}) ===",
        flush=True,
    )
    _run([sys.executable, "-m", "pip", "install", paddlex_ocr_pip_spec()], cwd=WORKSPACE)

    link = WORKSPACE / "40_operations" / "scripts" / "link_ocr_venv_path.py"
    print("=== link pdf_extraction into venv ===", flush=True)
    _run([sys.executable, str(link)], cwd=WORKSPACE)

    if args.skip_smoke:
        print("Skip smoke test.", flush=True)
        return 0

    print(
        f"=== smoke: paddle {PADDLEPADDLE_VERSION} + PPStructureV3 ===",
        flush=True,
    )
    from pdf_extraction.paddle_ppstructure import is_paddle_available

    if not is_paddle_available():
        print("ERROR: paddleocr import failed.", file=sys.stderr)
        return 1
    try:
        import paddle

        print(f"PaddlePaddle {getattr(paddle, '__version__', '?')} OK", flush=True)
        from paddleocr import PPStructureV3  # noqa: F401

        # Pipeline init downloads models; import-only check is enough for install smoke.
        print("PPStructureV3 import OK", flush=True)
    except Exception as e:
        print(f"ERROR: smoke failed: {e}", file=sys.stderr)
        return 1
    print("OK: PaddleOCR ready (framework: github.com/PaddlePaddle/Paddle).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
