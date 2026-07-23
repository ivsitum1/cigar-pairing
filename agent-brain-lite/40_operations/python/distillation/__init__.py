"""Distillation trace capture — Phase 0 of the Fable → md-file-system plan.

Captures full Context → Reasoning → Action → Outcome traces (the notebook's
step 1) and cleans them (step 2) so they can be authored into behavior_rules
and SKILLS (step 3, Phase 1). This is a *content-bearing* layer, distinct from
the PHI-free ``trajectory_rl`` RL-event layer — raw traces stay local
(gitignored) until PHI-reviewed and promoted to the corpus.

See 30_system/docs/DISTILLATION_TRACE_PROTOCOL.md.
"""
from __future__ import annotations

from .clean import clean_text, scrub_phi
from .emit import Action, CaptureRecord, capture, resolve_raw_dir
from .enrich import enrich_skeleton
from .promote import list_raw_traces, promote_trace, suggest_distills_to, trace_to_card_markdown
from .session import append_action, flush_skeleton, reset_session

__all__ = [
    "Action",
    "CaptureRecord",
    "append_action",
    "capture",
    "clean_text",
    "enrich_skeleton",
    "flush_skeleton",
    "list_raw_traces",
    "promote_trace",
    "reset_session",
    "resolve_raw_dir",
    "scrub_phi",
    "suggest_distills_to",
    "trace_to_card_markdown",
]
