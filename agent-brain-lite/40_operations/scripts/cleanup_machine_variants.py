#!/usr/bin/env python3
"""Remove OneDrive machine-conflict duplicates when canonical copy exists and matches."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "40_operations" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from hostname_conflict_files import (  # noqa: E402
    canonical_name_for_conflict,
    is_hostname_conflict_filename,
)

SKIP_DIR_PARTS = {".git", "node_modules", "90_archive", ".claude", "agent-transcripts"}


@dataclass
class VariantAction:
    variant_path: str
    canonical_path: str
    action: str
    reason: str


def file_hash(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def is_machine_variant(name: str) -> bool:
    return is_hostname_conflict_filename(name)


def canonical_path_for(variant: pathlib.Path) -> pathlib.Path | None:
    canonical_name = canonical_name_for_conflict(variant.name)
    if not canonical_name or canonical_name == variant.name:
        return None
    return variant.with_name(canonical_name)


def should_skip_dir(path: pathlib.Path) -> bool:
    return any(part in SKIP_DIR_PARTS for part in path.parts)


def collect_variants(root: pathlib.Path) -> list[pathlib.Path]:
    variants: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_dir(path.relative_to(root)):
            continue
        if is_machine_variant(path.name):
            variants.append(path)
    return sorted(variants)


def evaluate(root: pathlib.Path) -> list[VariantAction]:
    actions: list[VariantAction] = []
    for variant in collect_variants(root):
        rel_variant = variant.relative_to(root).as_posix()
        canonical = canonical_path_for(variant)
        if canonical is None:
            actions.append(
                VariantAction(rel_variant, "", "skip", "could not derive canonical name")
            )
            continue
        rel_canonical = canonical.relative_to(root).as_posix()
        if not canonical.exists():
            actions.append(
                VariantAction(rel_variant, rel_canonical, "skip", "canonical missing")
            )
            continue
        if file_hash(variant) != file_hash(canonical):
            actions.append(
                VariantAction(rel_variant, rel_canonical, "skip", "hash mismatch with canonical")
            )
            continue
        actions.append(VariantAction(rel_variant, rel_canonical, "delete", "duplicate of canonical"))
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup hostname-conflict duplicate files.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    actions = evaluate(root)
    to_delete = [a for a in actions if a.action == "delete"]

    if args.json:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "actions": [asdict(a) for a in actions],
            "delete_count": len(to_delete),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Hostname conflict variants: {len(actions)} evaluated, {len(to_delete)} deletable")
        for a in actions[:20]:
            print(f"  [{a.action}] {a.variant_path} -> {a.canonical_path or '?'} ({a.reason})")
        if len(actions) > 20:
            print(f"  ... and {len(actions) - 20} more")

    if args.delete:
        if not args.yes and not args.dry_run:
            print("Refusing delete without --yes")
            return 1
        if args.dry_run:
            print("Dry run: no files deleted")
            return 0
        for a in to_delete:
            (root / a.variant_path).unlink(missing_ok=True)
        print(f"Deleted {len(to_delete)} duplicate file(s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
