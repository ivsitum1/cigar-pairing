"""Resolve Paddle inference device (auto GPU/CPU).

Upstream framework: https://github.com/PaddlePaddle/Paddle
Install wheels (do not vendor the full repo): https://www.paddlepaddle.org.cn/install/quick
"""

from __future__ import annotations

import os

# Pin: 3.3.x breaks CPU inference with oneDNN/PIR (Paddle #77340); 3.2.2 works with enable_mkldnn=False.
PADDLEPADDLE_VERSION = "3.2.2"
# PP-StructureV3 needs paddlex[ocr], not only paddlex[ocr-core] from paddleocr's base deps.
PADDLEX_OCR_EXTRA_VERSION = "3.5.2"


def resolve_paddle_device() -> str:
    """
    Return 'gpu' or 'cpu'.

    Env PADDLE_OCR_DEVICE: auto | gpu | cpu (default auto).
    """
    mode = os.environ.get("PADDLE_OCR_DEVICE", "auto").strip().lower()
    if mode == "cpu":
        return "cpu"
    if mode == "gpu":
        return "gpu"

    try:
        import paddle

        if paddle.device.is_compiled_with_cuda():
            count = paddle.device.cuda.device_count()
            if count and count > 0:
                return "gpu"
    except Exception:
        pass
    return "cpu"


def paddlepaddle_pip_spec(device: str) -> tuple[str, list[str]]:
    """Return (package spec, extra pip args) for official PaddlePaddle wheels."""
    index_cpu = "https://www.paddlepaddle.org.cn/packages/stable/cpu/"
    if device == "gpu":
        # CUDA 11.8 wheel; install script logs fallback if GPU install fails
        return (
            f"paddlepaddle-gpu=={PADDLEPADDLE_VERSION}",
            ["-i", "https://www.paddlepaddle.org.cn/packages/stable/cu118/"],
        )
    return (f"paddlepaddle=={PADDLEPADDLE_VERSION}", ["-i", index_cpu])


def paddlex_ocr_pip_spec() -> str:
    """Full OCR extra required by PP-StructureV3 (see PaddleX deps error if missing)."""
    return f"paddlex[ocr]=={PADDLEX_OCR_EXTRA_VERSION}"
