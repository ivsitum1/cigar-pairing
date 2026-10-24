"""Pytest: migrate_v1.py is idempotent (byte-identical second run)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
V1 = ROOT / "src" / "data" / "v1"


def _load_migrate():
    path = SCRIPTS / "migrate_v1.py"
    spec = importlib.util.spec_from_file_location("migrate_v1", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["migrate_v1"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def migrate():
    return _load_migrate()


def test_migrate_idempotent(migrate, tmp_path, monkeypatch):
    # Run against real DATA paths (module constants); compare bytes before/after second run.
    migrate.run()
    before = {p.name: p.read_bytes() for p in sorted(V1.glob("*.json"))}
    assert before, "expected v1 json files after migrate"
    migrate.run()
    after = {p.name: p.read_bytes() for p in sorted(V1.glob("*.json"))}
    assert before.keys() == after.keys()
    for name in before:
        assert before[name] == after[name], f"{name} changed on second migrate"


def test_offer_keys_unique(migrate):
    migrate.run()
    offers = __import__("json").loads((V1 / "offers.json").read_text(encoding="utf-8"))
    keys = set()
    for o in offers:
        k = (o["shopId"], o["productId"], o.get("vitolaId") or "", o.get("url") or "")
        assert k not in keys, k
        keys.add(k)
    assert len(keys) == len(offers)


def test_walkin_offers_have_no_url(migrate):
    import json

    migrate.run()
    shops = {s["id"]: s for s in json.loads((V1 / "shops.json").read_text(encoding="utf-8"))}
    offers = json.loads((V1 / "offers.json").read_text(encoding="utf-8"))
    for o in offers:
        if shops[o["shopId"]]["type"] == "walkIn":
            assert not o.get("url"), o["id"]
