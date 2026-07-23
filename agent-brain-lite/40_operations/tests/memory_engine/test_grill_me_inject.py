"""Tests for Grill-me conditional injection heuristics."""
from __future__ import annotations

import json

from memory_engine.grill_me_inject import (
    build_injection_query,
    extract_conversation_id,
    extract_user_prompt,
    prompt_matches_grill_me,
)


def test_prompt_matches_grill_me_registry_phrases() -> None:
    assert prompt_matches_grill_me("Grill-me before we implement")
    assert prompt_matches_grill_me("grill me on architecture")
    assert prompt_matches_grill_me("Need shared understanding of the API")
    assert prompt_matches_grill_me("research grill-me for my thesis")
    assert prompt_matches_grill_me("opisujem zadatak za meta-analizu")
    assert not prompt_matches_grill_me("fix the typo in README")
    assert not prompt_matches_grill_me("")


def test_extract_user_prompt_top_level() -> None:
    hook: dict = {"prompt": "  clarify requirements for auth  "}
    assert extract_user_prompt(hook, {}) == "clarify requirements for auth"


def test_extract_user_prompt_raw_input_json() -> None:
    inner = {"prompt": "design tree for checkout flow", "conversation_id": "c1"}
    hook = {"raw_input": json.dumps(inner)}
    assert extract_user_prompt(hook, {}) == "design tree for checkout flow"


def test_extract_conversation_id() -> None:
    hook = {"conversation_id": "abc-123"}
    assert extract_conversation_id(hook, {}) == "abc-123"
    assert extract_conversation_id({}, {"conversationId": "x"}) == "x"


def test_build_injection_query_truncates() -> None:
    long = "word " * 200
    q = build_injection_query(long)
    assert "memory alignment" in q
    assert len(q) < len(long) + 100
