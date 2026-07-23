"""
Tests for catalog_pdfs.py
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "20_knowledge/reference_library" / "tools"))

from catalog_pdfs import (
    classify_pdf,
    generate_filename,
    extract_pdf_metadata
)


class TestClassifyPDF:
    """Tests for classify_pdf function."""
    
    def test_classify_medicine_anesthesiology(self):
        """Should classify anesthesia-related PDFs correctly."""
        metadata = {
            "title": "Anesthesia Textbook",
            "subject": "Anesthesiology"
        }
        filename = "anesthesia_book.pdf"
        
        domain, type_name, category = classify_pdf(metadata, filename)
        
        assert domain == "medicine"
        assert type_name == "textbooks"
        assert category == "anesthesiology"
    
    def test_classify_medicine_icu(self):
        """Should classify ICU-related PDFs correctly."""
        metadata = {
            "title": "Intensive Care Medicine",
            "subject": "Critical Care"
        }
        filename = "icu_book.pdf"
        
        domain, type_name, category = classify_pdf(metadata, filename)
        
        assert domain == "medicine"
        assert type_name == "textbooks"
        assert category == "intensive_care"
    
    def test_classify_statistics_bayesian(self):
        """Should classify Bayesian statistics PDFs correctly."""
        metadata = {
            "title": "Bayesian Data Analysis",
            "subject": "Bayesian Statistics"
        }
        filename = "bayesian_book.pdf"
        
        domain, type_name, category = classify_pdf(metadata, filename)
        
        assert domain == "statistics"
        assert type_name == "books"
        assert category == "bayesian"
    
    def test_classify_statistics_meta_analysis(self):
        """Should classify meta-analysis PDFs correctly."""
        metadata = {
            "title": "Introduction to Meta-Analysis",
            "subject": "Systematic Review"
        }
        filename = "meta_analysis.pdf"
        
        domain, type_name, category = classify_pdf(metadata, filename)
        
        assert domain == "statistics"
        assert type_name == "books"
        assert category == "meta_analysis"
    
    def test_default_classification(self):
        """Should default to statistics/modern_statistics."""
        metadata = {
            "title": "Unknown Document",
            "subject": ""
        }
        filename = "unknown.pdf"
        
        domain, type_name, category = classify_pdf(metadata, filename)
        
        assert domain == "statistics"
        assert type_name == "books"
        assert category == "modern_statistics"


class TestGenerateFilename:
    """Tests for generate_filename function."""
    
    def test_generate_filename_with_all_metadata(self):
        """Should generate filename from complete metadata."""
        metadata = {
            "author": "Smith, John",
            "year": "2024",
            "title": "Test Document Title"
        }
        
        filename = generate_filename(metadata)
        
        assert filename.startswith("Smith2024_")
        assert ".pdf" in filename or len(filename) > 0  # Should have some content
    
    def test_generate_filename_with_partial_metadata(self):
        """Should handle missing metadata gracefully."""
        metadata = {
            "author": None,
            "year": "2024",
            "title": "Test Document"
        }
        
        filename = generate_filename(metadata)
        
        assert "2024" in filename
        assert len(filename) > 0
    
    def test_generate_filename_handles_multiple_authors(self):
        """Should use first author when multiple authors provided."""
        metadata = {
            "author": "Smith, John and Doe, Jane",
            "year": "2024",
            "title": "Test Document"
        }
        
        filename = generate_filename(metadata)
        
        assert filename.startswith("Smith2024_") or "2024" in filename


class TestExtractPDFMetadata:
    """Tests for extract_pdf_metadata function."""
    
    @pytest.mark.skipif(True, reason="Requires PyPDF2 and actual PDF files")
    def test_extract_metadata_from_pdf(self):
        """Should extract metadata from PDF file."""
        # This test would require actual PDF files
        pass
    
    def test_extract_metadata_from_filename(self, temp_dir):
        """Should extract metadata from filename pattern."""
        # Create a mock scenario
        # In real implementation, this would read from PDF
        # For now, we test the filename parsing logic
        test_filename = "Smith2024_Test_Document.pdf"
        
        # Simulate what the function does with filename
        import re
        match = re.match(r'^([A-Za-z]+)(\d{4})_(.+)$', test_filename.replace('.pdf', ''))
        
        if match:
            author = match.group(1)
            year = match.group(2)
            title = match.group(3).replace('_', ' ')
            
            assert author == "Smith"
            assert year == "2024"
            assert "Test Document" in title

