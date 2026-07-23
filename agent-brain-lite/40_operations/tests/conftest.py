"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
from pathlib import Path
import tempfile
import shutil

# Repo root (parent of 40_operations/), not 40_operations/ alone
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "30_system" / "behavior_rules" / "tools"))
sys.path.insert(0, str(REPO_ROOT / "20_knowledge" / "reference_library" / "tools"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample text for testing purposes.
    It contains multiple sentences with varying lengths.
    Some sentences are short. Others are much longer and contain
    more complex structures with additional clauses and phrases.
    The text includes numbers like 42 and dates like 2024.
    """


@pytest.fixture
def sample_pdf_metadata():
    """Sample PDF metadata for testing."""
    return {
        "title": "Test Document",
        "author": "Test Author",
        "year": "2024",
        "subject": "Testing"
    }

