"""Smoke tests for 40_operations/scripts/run_pipeline.py."""
import sys
from io import StringIO
from unittest.mock import patch

import run_pipeline


def test_all_pipelines_defined():
    """All 6 pipelines must be in the PIPELINES dict."""
    for num in ["1", "2", "3", "4", "5", "6"]:
        assert num in run_pipeline.PIPELINES, f"Pipeline {num} missing"


def test_pipeline_structure():
    """Each pipeline must have (name, subagents, keywords) tuple."""
    for key, val in run_pipeline.PIPELINES.items():
        assert len(val) == 3, f"Pipeline {key} has {len(val)} elements, expected 3"
        name, subagents, keywords = val
        assert isinstance(name, str) and name
        assert isinstance(subagents, str) and subagents
        assert isinstance(keywords, str) and keywords


def test_main_generates_prompt():
    """Pipeline 1 should produce a valid prompt string."""
    captured = StringIO()
    with patch("sys.argv", ["run_pipeline.py", "--pipeline", "1"]):
        with patch("sys.stdout", captured):
            run_pipeline.main()
    output = captured.getvalue()
    assert "Pipeline 1" in output
    assert "Analysis -> Manuscript" in output


def test_pipeline6_output():
    """Pipeline 6 should produce lifecycle prompt."""
    captured = StringIO()
    with patch("sys.argv", ["run_pipeline.py", "--pipeline", "6"]):
        with patch("sys.stdout", captured):
            run_pipeline.main()
    output = captured.getvalue()
    assert "Pipeline 6" in output
    assert "Full Research Lifecycle" in output


def test_context_appended():
    """--context flag should add context to prompt."""
    captured = StringIO()
    with patch("sys.argv", ["run_pipeline.py", "--pipeline", "3", "--context", "BRMS study"]):
        with patch("sys.stdout", captured):
            run_pipeline.main()
    output = captured.getvalue()
    assert "BRMS study" in output
