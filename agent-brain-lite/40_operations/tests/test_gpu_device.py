"""Tests for shared GPU device helper."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

OPS = Path(__file__).resolve().parents[1] / "python"
if str(OPS) not in sys.path:
    sys.path.insert(0, str(OPS))

from common.gpu import resolve_device  # noqa: E402


def test_resolve_device_cpu_forced(monkeypatch):
    monkeypatch.setenv("AGENT_COMPUTE_DEVICE", "cpu")
    assert resolve_device() == "cpu"


def test_resolve_device_auto_returns_cpu_or_cuda(monkeypatch):
    monkeypatch.setenv("AGENT_COMPUTE_DEVICE", "auto")
    assert resolve_device() in {"cpu", "cuda"}
