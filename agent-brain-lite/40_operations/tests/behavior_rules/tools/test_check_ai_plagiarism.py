"""
Tests for check_ai_plagiarism.py
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add module to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "30_system" / "behavior_rules" / "tools"))

from check_ai_plagiarism import (
    calculate_basic_ai_score,
    generate_recommendations,
    check_local_similarity,
    read_file,
    save_results,
    check_ai_score_only,
)

try:
    from ai_pattern_scan import scan_text, pattern_score
    HAS_PATTERN_SCAN = True
except ImportError:
    HAS_PATTERN_SCAN = False


class TestCalculateBasicAIScore:
    """Tests for calculate_basic_ai_score function."""
    
    def test_short_text_returns_zero(self):
        """Short text should return 0.0."""
        text = "Short text."
        assert calculate_basic_ai_score(text) == 0.0
    
    def test_uniform_sentence_length_increases_score(self):
        """Text with uniform sentence length should have higher AI score."""
        uniform_text = "This is sentence one. This is sentence two. This is sentence three. " * 10
        varied_text = "Short. This is a much longer sentence with more words and complexity. " * 5
        
        uniform_score = calculate_basic_ai_score(uniform_text)
        varied_score = calculate_basic_ai_score(varied_text)
        
        # Uniform text should have higher AI score
        assert uniform_score >= varied_score
    
    def test_perfect_words_increase_score(self):
        """Text with 'perfect' transition words should have higher score."""
        text_with_perfect = "Furthermore, this is important. Moreover, it is significant. Additionally, it matters. " * 20
        text_normal = "This is important. It is significant. It matters. " * 20
        
        perfect_score = calculate_basic_ai_score(text_with_perfect)
        normal_score = calculate_basic_ai_score(text_normal)
        
        assert perfect_score >= normal_score
    
    def test_score_is_bounded(self):
        """Score should be between 0 and 1."""
        text = "This is a test. " * 100
        score = calculate_basic_ai_score(text)
        assert 0.0 <= score <= 1.0


class TestGenerateRecommendations:
    """Tests for generate_recommendations function."""
    
    def test_high_ai_score_recommendation(self):
        """High AI score should generate appropriate recommendation."""
        results = {
            "ai_detection": {
                "gptzero": {"score": 0.8},
                "openai": {"score": 0.75}
            },
            "plagiarism_detection": {}
        }
        
        recommendations = generate_recommendations(results)
        
        assert len(recommendations) > 0
        assert any("HIGH AI SCORE" in rec for rec in recommendations)
    
    def test_low_ai_score_recommendation(self):
        """Low AI score should generate positive recommendation."""
        results = {
            "ai_detection": {
                "gptzero": {"score": 0.1}
            },
            "plagiarism_detection": {}
        }
        
        recommendations = generate_recommendations(results)
        
        assert len(recommendations) > 0
        assert any("LOW AI SCORE" in rec for rec in recommendations)
    
    def test_high_plagiarism_score_recommendation(self):
        """High plagiarism score should generate warning."""
        results = {
            "ai_detection": {},
            "plagiarism_detection": {
                "copyleaks": {"similarity_score": 0.5}
            }
        }
        
        recommendations = generate_recommendations(results)
        
        assert len(recommendations) > 0
        assert any("HIGH SIMILARITY" in rec or "MANDATORY REVISION" in rec for rec in recommendations)
    
    def test_no_results_generates_default(self):
        """Empty results should generate default recommendation."""
        results = {
            "ai_detection": {},
            "plagiarism_detection": {}
        }
        
        recommendations = generate_recommendations(results)
        
        assert len(recommendations) > 0
        assert any("No specific recommendations" in rec for rec in recommendations)


class TestCheckLocalSimilarity:
    """Tests for check_local_similarity function."""
    
    def test_no_reference_texts_returns_skipped(self):
        """Should return skipped status when no reference texts provided."""
        result = check_local_similarity("Test text", None)
        
        assert result["status"] == "skipped"
        assert "No reference texts" in result["message"]
    
    def test_high_similarity_detection(self):
        """Should detect high similarity with reference text."""
        text = "This is a test document with some content."
        reference = "This is a test document with some content."
        
        result = check_local_similarity(text, [reference])
        
        assert result["status"] == "success"
        assert result["similarity_score"] > 0.9
        assert result["matches"] > 0
    
    def test_low_similarity_detection(self):
        """Should detect low similarity with different text."""
        text = (
            "Quantum chromodynamics describes quark-gluon interactions at high energy scales "
            "with non-abelian gauge symmetry."
        )
        reference = "This is a test document with some content about unrelated methodology."

        result = check_local_similarity(text, [reference])

        assert result["status"] == "success"
        assert result["similarity_score"] < 0.5


class TestReadFile:
    """Tests for read_file function."""
    
    def test_read_existing_file(self, tmp_path):
        """Should read content from existing file."""
        test_file = tmp_path / "test.txt"
        test_content = "Test content"
        test_file.write_text(test_content, encoding='utf-8')
        
        content = read_file(str(test_file))
        assert content == test_content
    
    def test_read_nonexistent_file(self):
        """Should exit on nonexistent file."""
        with pytest.raises(SystemExit):
            read_file("nonexistent_file.txt")


class TestSaveResults:
    """Tests for save_results function."""
    
    def test_saves_json_and_text(self, tmp_path):
        """Should save both JSON and text format."""
        results = {
            "timestamp": "2024-01-01T00:00:00",
            "file_path": "test.txt",
            "text_length": 100,
            "ai_detection": {},
            "plagiarism_detection": {},
            "recommendations": []
        }
        
        save_results(results, tmp_path)
        
        json_path = tmp_path / "ai_plagiarism_report.json"
        txt_path = tmp_path / "ai_plagiarism_report.txt"
        
        assert json_path.exists()
        assert txt_path.exists()
        
        # Verify JSON content
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded == results
        
        # Verify text content
        text_content = txt_path.read_text(encoding='utf-8')
        assert "AI WRITING DETECTION" in text_content
        assert "PLAGIARISM DETECTION" in text_content


@pytest.mark.skipif(not HAS_PATTERN_SCAN, reason="ai_pattern_scan not importable")
class TestPatternScan:
    """Tests for local AI pattern scanner."""

    AI_SAMPLE = (
        "It is important to note that this groundbreaking study delves into the "
        "intricate tapestry of perioperative care. Furthermore, the clinic "
        "serves as a testament to vibrant innovation. In conclusion, outcomes "
        "were lightweight, flexible, and low-cost."
    )

    HUMANISH_SAMPLE = (
        "We enrolled 120 adults with septic shock. Norepinephrine was titrated "
        "to MAP 65 mmHg. Mortality at 28 days was 34% (95% CI 26-43%)."
    )

    def test_ai_sample_scores_higher_than_humanish(self):
        ai = pattern_score(self.AI_SAMPLE)
        human = pattern_score(self.HUMANISH_SAMPLE)
        assert ai > human

    def test_citation_bug_raises_score(self):
        text = "Results improved :contentReference[oaicite:0]{index=0} significantly."
        result = scan_text(text)
        assert result.score >= 0.5
        assert any(c.name == "citation_bugs" for c in result.categories)

    def test_check_ai_score_only_includes_pattern_scan(self):
        result = check_ai_score_only(self.AI_SAMPLE, fast_mode=True)
        assert "pattern_scan" in result.get("component_scores", {})
        assert result["score"] > 0.2

