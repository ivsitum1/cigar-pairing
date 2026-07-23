"""
Tests for track_versions.py
"""
import pytest
import sys
import re
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "30_system/behavior_rules" / "tools"))

from track_versions import (
    extract_version_from_file,
    VERSION_PATTERN,
    DATE_PATTERN,
    categorize_files
)


class TestVersionPattern:
    """Tests for version pattern matching."""
    
    def test_version_pattern_matches_bold(self):
        """Should match **Version:** X.Y format."""
        text = "**Version:** 1.2"
        match = VERSION_PATTERN.search(text)
        assert match is not None
        assert match.group(1) == "1.2"
    
    def test_version_pattern_matches_plain(self):
        """Should match Version: X.Y format."""
        text = "Version: 2.3"
        match = VERSION_PATTERN.search(text)
        assert match is not None
        assert match.group(1) == "2.3"
    
    def test_version_pattern_matches_semantic_version(self):
        """Should match semantic versioning (X.Y.Z)."""
        text = "**Version:** 1.2.3"
        match = VERSION_PATTERN.search(text)
        assert match is not None
        assert match.group(1) == "1.2.3"
    
    def test_version_pattern_case_insensitive(self):
        """Should be case insensitive."""
        text = "version: 1.0"
        match = VERSION_PATTERN.search(text)
        assert match is not None


class TestDatePattern:
    """Tests for date pattern matching."""
    
    def test_date_pattern_matches_last_updated(self):
        """Should match Last updated: YYYY-MM-DD format."""
        text = "Last updated: 2024-01-15"
        match = DATE_PATTERN.search(text)
        assert match is not None
        assert match.group(1) == "2024-01-15"
    
    def test_date_pattern_matches_created(self):
        """Should match Created: YYYY-MM-DD format."""
        text = "Created: 2024-01-15"
        match = DATE_PATTERN.search(text)
        assert match is not None
        assert match.group(1) == "2024-01-15"
    
    def test_date_pattern_case_insensitive(self):
        """Should be case insensitive."""
        text = "last updated: 2024-01-15"
        match = DATE_PATTERN.search(text)
        assert match is not None


class TestExtractVersionFromFile:
    """Tests for extract_version_from_file function."""
    
    def test_extract_version_with_date(self, temp_dir):
        """Should extract version and date from file."""
        test_file = temp_dir / "test.md"
        content = """
        # Test Document
        
        **Version:** 1.5
        Last updated: 2024-01-15
        """
        test_file.write_text(content, encoding='utf-8')
        
        result = extract_version_from_file(test_file)
        
        assert result is not None
        version, date = result
        assert version == "1.5"
        assert date == "2024-01-15"
    
    def test_extract_version_without_date(self, temp_dir):
        """Should extract version even without date."""
        test_file = temp_dir / "test.md"
        content = """
        # Test Document
        
        **Version:** 2.0
        """
        test_file.write_text(content, encoding='utf-8')
        
        result = extract_version_from_file(test_file)
        
        assert result is not None
        version, date = result
        assert version == "2.0"
        assert date is None
    
    def test_no_version_returns_none(self, temp_dir):
        """Should return None if no version found."""
        test_file = temp_dir / "test.md"
        content = "# Test Document\nNo version here."
        test_file.write_text(content, encoding='utf-8')
        
        result = extract_version_from_file(test_file, verbose=False)
        assert result is None


class TestCategorizeFiles:
    """Tests for categorize_files function."""
    
    def test_categorize_agent_files(self):
        """Should categorize agent files correctly."""
        versions = {
            "agents/01_test.md": {"version": "1.0", "date": "2024-01-01", "path": "agents/01_test.md"}
        }
        
        categories = categorize_files(versions)
        
        assert "agents" in categories
        assert len(categories["agents"]) == 1
        assert categories["agents"][0][0] == "agents/01_test.md"
    
    def test_categorize_tools_files(self):
        """Should categorize tools files correctly."""
        versions = {
            "tools/README_tools.md": {"version": "1.0", "date": "2024-01-01", "path": "tools/README_tools.md"}
        }
        
        categories = categorize_files(versions)
        
        assert "tools" in categories
        assert len(categories["tools"]) == 1
    
    def test_categorize_core_files(self):
        """Should categorize core rule files correctly."""
        versions = {
            "01_general_rules.md": {"version": "1.0", "date": "2024-01-01", "path": "01_general_rules.md"}
        }
        
        categories = categorize_files(versions)
        
        assert "core" in categories
        assert len(categories["core"]) == 1

