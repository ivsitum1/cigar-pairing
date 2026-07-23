#!/usr/bin/env python3
"""Seed codebooks and ensure main.md lists data contract paths (study project root)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from codebook_seed import seed_codebooks  # noqa: E402

DATA_CONTRACTS_BLOCK = """
## Data contracts (codebooks)

- **Extraction codebook (SR/MA):** `01_input/data_extraction/codebook.md`
- **Dataset codebook (own CSV):** `01_input/codebook/dataset_codebook.md`
"""


def patch_main_md(project_root: Path) -> bool:
    """Append Data contracts section to context/main.md if missing. Returns True if patched."""
    candidates = [
        project_root / "30_system/04_documentation/context/main.md",
        project_root / "04_documentation/context/main.md",
    ]
    for main_path in candidates:
        if not main_path.is_file():
            continue
        text = main_path.read_text(encoding="utf-8")
        if "Data contracts" in text or "extraction_codebook" in text.lower():
            return False
        if not text.endswith("\n"):
            text += "\n"
        main_path.write_text(text + DATA_CONTRACTS_BLOCK.strip() + "\n", encoding="utf-8")
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare study project codebook layout")
    parser.add_argument("--root", type=str, required=True, help="Study project root")
    parser.add_argument(
        "--agent-rules",
        type=str,
        default=None,
        help="Path to agent-rules (default: parent of 40_operations/scripts)",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    rules = Path(args.agent_rules).resolve() if args.agent_rules else None

    created = seed_codebooks(root, rules)
    for rel in created:
        print(f"Created {rel}")
    if patch_main_md(root):
        print("Patched context main.md with Data contracts section")
    else:
        print("main.md already has Data contracts or not found (skip patch)")
    print("\nNext: migrate variable rows from your legacy extraction doc into")
    print("  01_input/data_extraction/codebook.md")
    print("Guide: 30_system/docs/study_data/CODEBOOK_MIGRATION.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
