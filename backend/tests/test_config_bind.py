"""Bind/token guard for LAN exposure."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_TMP = tempfile.mkdtemp()
os.environ.setdefault("BAND_REFS_DIR", str(Path(_TMP) / "band_refs"))

from app.config import is_loopback_host, require_token_for_lan  # noqa: E402


class BindGuardTests(unittest.TestCase):
    def test_loopback_hosts(self) -> None:
        for h in ("127.0.0.1", "localhost", "::1", "LOCALHOST"):
            self.assertTrue(is_loopback_host(h))

    def test_non_loopback_without_token_exits(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            require_token_for_lan(host="0.0.0.0", token="")
        self.assertIn("OCR_API_TOKEN", str(ctx.exception))

    def test_non_loopback_with_token_ok(self) -> None:
        require_token_for_lan(host="0.0.0.0", token="secret")

    def test_loopback_without_token_ok(self) -> None:
        require_token_for_lan(host="127.0.0.1", token="")


if __name__ == "__main__":
    unittest.main()
