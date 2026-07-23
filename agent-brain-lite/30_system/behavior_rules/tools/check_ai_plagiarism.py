#!/usr/bin/env python3
"""
AI Writing Detection and Plagiarism Checker

This script checks manuscript for:
1. AI writing detection (whether text is AI-generated)
2. Plagiarism detection (similarity with other works)

Usage:
    python check_ai_plagiarism.py <input_file> [--output-dir <dir>] [--tools <tool1,tool2>]

Examples:
    python check_ai_plagiarism.py manuscript.txt
    python check_ai_plagiarism.py manuscript.txt --output-dir results --tools gptzero,copyleaks
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from urllib.parse import quote

# Optional advanced libraries - graceful fallback if not installed
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

try:
    from transformers import pipeline
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from googletrans import Translator
    HAS_GOOGLETRANS = True
except ImportError:
    HAS_GOOGLETRANS = False

try:
    import langdetect
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

try:
    from ai_pattern_scan import pattern_score, scan_text
    HAS_PATTERN_SCAN = True
except ImportError:
    HAS_PATTERN_SCAN = False

# ============================================================================
# API Configuration (add your API keys if needed)
# ============================================================================

API_CONFIG = {
    "gptzero": {
        "api_key": os.getenv("GPTZERO_API_KEY", ""),
        "api_url": "https://api.gptzero.me/v2/predict",
        "requires_key": False  # GPTZero has free version without API key
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "api_url": "https://api.openai.com/v1/classifications",
        "requires_key": True
    },
    "copyleaks": {
        "api_key": os.getenv("COPYLEAKS_API_KEY", ""),
        "api_url": "https://api.copyleaks.com/v3",
        "requires_key": True
    }
}

# ============================================================================
# Helper Functions
# ============================================================================

def read_file(file_path: str) -> str:
    """Reads text from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def detect_language(text: str) -> str:
    """
    Detects language of text.
    Returns language code (e.g., 'hr' for Croatian, 'en' for English).
    """
    if HAS_LANGDETECT:
        try:
            from langdetect import detect
            return detect(text)
        except:
            pass
    
    # Fallback: simple heuristic based on common Croatian words
    croatian_indicators = ['je', 'su', 'na', 'u', 'za', 'od', 'do', 'sa', 'ili', 'ali', 
                          'koji', 'koja', 'koje', 'što', 'kada', 'gdje', 'kako', 'zašto']
    text_lower = text.lower()
    croatian_count = sum(1 for word in croatian_indicators if word in text_lower)
    
    # If many Croatian indicators found, likely Croatian
    if croatian_count > 5:
        return 'hr'
    
    return 'en'  # Default to English

def translate_croatian_to_english(text: str) -> Tuple[str, Dict]:
    """
    Translates Croatian text to English.
    Uses Google Translate API (googletrans) if available, otherwise returns original.
    
    Returns:
        Tuple of (translated_text, translation_info)
    """
    translation_info = {
        "method": "none",
        "original_language": "unknown",
        "translation_successful": False
    }
    
    # Detect language first
    detected_lang = detect_language(text)
    translation_info["original_language"] = detected_lang
    
    if detected_lang != 'hr':
        # Not Croatian, return original
        translation_info["message"] = f"Text appears to be {detected_lang}, not Croatian. Returning original."
        return text, translation_info
    
    # Try Google Translate
    if HAS_GOOGLETRANS:
        try:
            translator = Translator()
            result = translator.translate(text, src='hr', dest='en')
            translation_info["method"] = "googletrans"
            translation_info["translation_successful"] = True
            translation_info["message"] = "Translation successful using googletrans"
            return result.text, translation_info
        except Exception as e:
            translation_info["message"] = f"Translation failed: {str(e)}"
            print(f"Warning: Translation failed: {e}")
            print("  Returning original text. Install googletrans for translation: pip install googletrans==4.0.0rc1")
    
    # Try OpenAI API if available
    openai_key = API_CONFIG["openai"]["api_key"]
    if openai_key:
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            # Use OpenAI for translation
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a translator. Translate Croatian academic text to English, maintaining academic style and third-person/passive voice. Translate directly and simply."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.3
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                translated = result["choices"][0]["message"]["content"].strip()
                translation_info["method"] = "openai"
                translation_info["translation_successful"] = True
                translation_info["message"] = "Translation successful using OpenAI API"
                return translated, translation_info
        except Exception as e:
            translation_info["message"] = f"OpenAI translation failed: {str(e)}"
            print(f"Warning: OpenAI translation failed: {e}")
    
    # Fallback: return original with warning
    translation_info["message"] = "No translation method available. Install googletrans: pip install googletrans==4.0.0rc1"
    print("Warning: No translation method available.")
    print("  Install googletrans for translation: pip install googletrans==4.0.0rc1")
    print("  Or set OPENAI_API_KEY for OpenAI translation")
    return text, translation_info

def save_results(results: Dict, output_dir: Path):
    """Saves results in JSON and text format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON format
    json_path = output_dir / "ai_plagiarism_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Text format (human-readable)
    txt_path = output_dir / "ai_plagiarism_report.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("AI WRITING DETECTION & PLAGIARISM CHECK REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Check date: {results['timestamp']}\n")
        f.write(f"File: {results['file_path']}\n")
        f.write(f"Text size: {results['text_length']} characters\n")
        
        # Translation info
        if results.get('translation'):
            trans_info = results['translation']
            f.write(f"Translation: {trans_info.get('message', 'N/A')}\n")
            if trans_info.get('translation_successful'):
                f.write(f"  Method: {trans_info.get('method', 'unknown')}\n")
                f.write(f"  Original language: {trans_info.get('original_language', 'unknown')}\n")
        f.write("\n")
        
        # AI Detection results
        f.write("-" * 80 + "\n")
        f.write("AI WRITING DETECTION RESULTS\n")
        f.write("-" * 80 + "\n\n")
        
        if results['ai_detection']:
            for tool, result in results['ai_detection'].items():
                f.write(f"Tool: {tool.upper()}\n")
                f.write(f"  Status: {result.get('status', 'N/A')}\n")
                if 'score' in result:
                    f.write(f"  AI Score: {result['score']:.2%}\n")
                if 'max_score' in result:
                    f.write(f"  Max Score (chunks): {result['max_score']:.2%}\n")
                if 'component_scores' in result:
                    f.write(f"  Component Scores: {result['component_scores']}\n")
                if 'statistics' in result:
                    stats = result['statistics']
                    f.write(f"  Statistics:\n")
                    if 'flesch_reading_ease' in stats:
                        f.write(f"    Readability (Flesch): {stats['flesch_reading_ease']:.1f}\n")
                    if 'flesch_kincaid_grade' in stats:
                        f.write(f"    Grade Level: {stats['flesch_kincaid_grade']:.1f}\n")
                    if 'avg_sentence_length' in stats:
                        f.write(f"    Avg Sentence Length: {stats['avg_sentence_length']:.1f}\n")
                if 'probability' in result:
                    f.write(f"  Probability: {result['probability']:.2%}\n")
                if 'classification' in result:
                    f.write(f"  Classification: {result['classification']}\n")
                if 'message' in result:
                    f.write(f"  Message: {result['message']}\n")
                f.write("\n")
        else:
            f.write("No AI detection check results.\n\n")
        
        # Plagiarism Detection results
        f.write("-" * 80 + "\n")
        f.write("PLAGIARISM DETECTION RESULTS\n")
        f.write("-" * 80 + "\n\n")
        
        if results['plagiarism_detection']:
            for tool, result in results['plagiarism_detection'].items():
                f.write(f"Tool: {tool.upper()}\n")
                f.write(f"  Status: {result.get('status', 'N/A')}\n")
                if 'similarity_score' in result:
                    f.write(f"  Similarity Score: {result['similarity_score']:.2%}\n")
                if 'tfidf_score' in result:
                    f.write(f"  TF-IDF Score: {result['tfidf_score']:.2%}\n")
                if 'semantic_score' in result:
                    f.write(f"  Semantic Score: {result['semantic_score']:.2%}\n")
                if 'matches' in result:
                    f.write(f"  Matches Found: {result['matches']}\n")
                if 'message' in result:
                    f.write(f"  Message: {result['message']}\n")
                f.write("\n")
        else:
            f.write("No plagiarism detection check results.\n\n")
        
        # Recommendations
        f.write("-" * 80 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 80 + "\n\n")
        
        for recommendation in results.get('recommendations', []):
            f.write(f"- {recommendation}\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print(f"\n✓ Results saved to:")
    print(f"  - {json_path}")
    print(f"  - {txt_path}")

def generate_recommendations(results: Dict) -> List[str]:
    """Generates recommendations based on results."""
    recommendations = []
    
    # AI Detection recommendations
    ai_scores = []
    for tool, result in results.get('ai_detection', {}).items():
        if 'score' in result:
            ai_scores.append(result['score'])
        elif 'probability' in result:
            ai_scores.append(result['probability'])
    
    if ai_scores:
        avg_ai_score = sum(ai_scores) / len(ai_scores)
        if avg_ai_score > 0.5:
            recommendations.append(
                f"HIGH AI SCORE ({avg_ai_score:.1%}): Text revision recommended. "
                "Add your own style, specific details and personal insights."
            )
        elif avg_ai_score > 0.2:
            recommendations.append(
                f"MODERATE AI SCORE ({avg_ai_score:.1%}): Consider revising sections with "
                "high scores to sound more natural."
            )
        else:
            recommendations.append(
                f"LOW AI SCORE ({avg_ai_score:.1%}): Text sounds natural. "
                "Keep up the good work!"
            )
    
    # Plagiarism Detection recommendations
    plagiarism_scores = []
    for tool, result in results.get('plagiarism_detection', {}).items():
        if 'similarity_score' in result:
            plagiarism_scores.append(result['similarity_score'])
    
    if plagiarism_scores:
        avg_plagiarism_score = sum(plagiarism_scores) / len(plagiarism_scores)
        if avg_plagiarism_score > 0.25:
            recommendations.append(
                f"HIGH SIMILARITY SCORE ({avg_plagiarism_score:.1%}): "
                "MANDATORY REVISION! Verify that all sources are properly cited."
            )
        elif avg_plagiarism_score > 0.15:
            recommendations.append(
                f"MODERATE SIMILARITY SCORE ({avg_plagiarism_score:.1%}): "
                "Check citations and ensure you use your own formulations."
            )
        else:
            recommendations.append(
                f"LOW SIMILARITY SCORE ({avg_plagiarism_score:.1%}): "
                "Text is original. Keep up the good work!"
            )
    
    if not recommendations:
        recommendations.append(
            "No specific recommendations. Check results manually."
        )
    
    return recommendations

# ============================================================================
# AI Writing Detection Functions
# ============================================================================

def check_gptzero(text: str) -> Dict:
    """
    Checks AI writing using GPTZero API.
    GPTZero has a free version that doesn't require API key.
    """
    try:
        # GPTZero web API (free version)
        # Note: This is an example - actual API may differ
        # Check https://gptzero.me/ for latest information
        
        # Alternatively: use web scraping or local method
        # For now return simulated result
        return {
            "status": "success",
            "score": calculate_basic_ai_score(text),  # Fallback method
            "message": "GPTZero check (fallback method - add API for real check)",
            "tool": "gptzero"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in GPTZero check: {str(e)}",
            "tool": "gptzero"
        }

def check_openai_classifier(text: str) -> Dict:
    """
    Checks AI writing using OpenAI AI Text Classifier.
    Requires OpenAI API key.
    """
    api_key = API_CONFIG["openai"]["api_key"]
    
    if not api_key:
        return {
            "status": "skipped",
            "message": "OpenAI API key not set. Set OPENAI_API_KEY environment variable.",
            "tool": "openai"
        }
    
    try:
        # OpenAI AI Text Classifier API
        # Note: OpenAI has discontinued AI Text Classifier, but we can use GPT-4 for analysis
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Alternatively: use GPT-4 for text analysis
        # For now return simulated result
        return {
            "status": "success",
            "score": calculate_basic_ai_score(text),
            "message": "OpenAI check (fallback method - OpenAI AI Text Classifier is discontinued)",
            "tool": "openai"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in OpenAI check: {str(e)}",
            "tool": "openai"
        }

def calculate_basic_ai_score(text: str) -> float:
    """
    Enhanced method for estimating AI score based on statistical characteristics.
    Detects patterns identified by independent AI checkers:
    - Mechanical precision
    - Formulaic organization
    - Robotic formality
    - Mechanical transitions
    - Predictable syntax
    - Over-sophisticated clarity
    
    This is a fallback method when API is not available.
    """
    if len(text) < 100:
        return 0.0
    
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    words = text.split()
    
    if not sentences or not words:
        return 0.0
    
    # Basic statistics
    sentence_lengths = [len(s.split()) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / len(sentences) if sentences else 0
    sentence_length_variance = sum((l - avg_sentence_length) ** 2 for l in sentence_lengths) / len(sentences) if sentences else 0
    
    # Heuristics for AI detection
    score = 0.0
    
    # 1. Uniform sentence length suggests AI (mechanical precision)
    if sentence_length_variance < 50:
        score += 0.15
    
    # 2. Too many "perfect" transition words (mechanical transitions)
    perfect_transitions = ['furthermore', 'moreover', 'additionally', 'consequently', 'therefore', 
                          'nevertheless', 'subsequently', 'accordingly', 'hence', 'thus']
    perfect_count = sum(1 for word in words if word.lower() in perfect_transitions)
    if perfect_count / len(words) > 0.015:  # More than 1.5% of words are perfect transitions
        score += 0.2
    
    # 3. Predictable sentence beginnings (formulaic organization)
    sentence_starters = [s.split()[0].lower() if s.split() else '' for s in sentences[:20]]  # First 20 sentences
    common_starters = ['the', 'it', 'this', 'these', 'that', 'there']
    starter_variety = len(set(sentence_starters))
    if starter_variety < 5 and len(sentence_starters) >= 10:  # Low variety in sentence starts
        score += 0.15
    
    # 4. Over-sophisticated vocabulary (sophisticated clarity)
    sophisticated_words = ['utilize', 'facilitate', 'demonstrate', 'substantiate', 'elucidate',
                           'ascertain', 'endeavor', 'implement', 'substantial', 'comprehensive']
    sophisticated_count = sum(1 for word in words if word.lower() in sophisticated_words)
    if sophisticated_count / len(words) > 0.02:  # More than 2% sophisticated words
        score += 0.15
    
    # 5. Fewer specific numbers/details (mechanical precision)
    numbers = sum(1 for char in text if char.isdigit())
    if numbers / len(text) < 0.01:
        score += 0.1
    
    # 6. Less punctuation variety (robotic formality)
    punctuation_variety = len(set(c for c in text if not c.isalnum() and c != ' '))
    if punctuation_variety < 5:
        score += 0.1
    
    # 7. Predictable syntax patterns (predictable syntax)
    # Check for repetitive sentence structures (subject-verb-object pattern)
    if len(sentences) >= 10:
        # Simple heuristic: check if sentences start similarly
        first_words = [s.split()[0].lower() if s.split() else '' for s in sentences[:15]]
        if len(set(first_words)) < 6:  # Low variety in first words
            score += 0.1
    
    # 8. Overly formal constructions (robotic formality)
    formal_phrases = ['it was observed that', 'it should be noted that', 'it is important to',
                     'it is worth noting that', 'it can be seen that', 'it has been shown that']
    formal_count = sum(1 for phrase in formal_phrases if phrase in text.lower())
    if formal_count > 3:  # More than 3 formal phrases
        score += 0.15
    
    # 9. Lack of sentence length variation (mechanical precision)
    if len(sentence_lengths) >= 10:
        length_range = max(sentence_lengths) - min(sentence_lengths)
        if length_range < 15:  # Very little variation in sentence length
            score += 0.1
    
    # 10. Formulaic hedging patterns (robotic formality)
    hedging_phrases = ['appears to', 'seems to', 'may be', 'might be', 'could be', 
                      'it is possible that', 'it is likely that', 'it is suggested that']
    hedging_count = sum(1 for phrase in hedging_phrases if phrase in text.lower())
    if hedging_count > 5:  # Excessive hedging
        score += 0.1
    
    return min(score, 1.0)

def analyze_text_statistics(text: str) -> Dict:
    """
    Analyze text statistics and readability for AI detection using textstat.
    """
    if not HAS_TEXTSTAT:
        return {
            "status": "skipped",
            "message": "textstat not installed. Install with: pip install textstat",
            "tool": "text_statistics"
        }
    
    if not HAS_NUMPY:
        return {
            "status": "skipped",
            "message": "numpy not installed. Install with: pip install numpy",
            "tool": "text_statistics"
        }
    
    try:
        stats = {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "smog_index": textstat.smog_index(text),
            "lexicon_count": textstat.lexicon_count(text),
            "avg_sentence_length": textstat.avg_sentence_length(text),
            "avg_syllables_per_word": textstat.avg_syllables_per_word(text),
            "difficult_words": textstat.difficult_words(text),
        }
        
        # Heuristics for AI detection based on statistics
        ai_indicators = 0.0
        
        # AI texts often have uniform readability (middle range)
        if 20 < stats["flesch_reading_ease"] < 60:
            ai_indicators += 0.1
        
        # Less variation in sentence length
        sentences = text.split('.')
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            length_std = float(np.std(sentence_lengths))
            if length_std < 10:  # Low variation
                ai_indicators += 0.2
        
        # Fewer difficult words
        if stats["lexicon_count"] > 0:
            difficult_ratio = stats["difficult_words"] / stats["lexicon_count"]
            if difficult_ratio < 0.1:
                ai_indicators += 0.1
        
        # Uniform grade level
        if 8 < stats["flesch_kincaid_grade"] < 12:
            ai_indicators += 0.1
        
        return {
            "status": "success",
            "statistics": stats,
            "score": min(ai_indicators, 1.0),
            "message": f"Text statistics analysis completed (AI indicators: {min(ai_indicators, 1.0):.2%})",
            "tool": "text_statistics"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in text statistics: {str(e)}",
            "tool": "text_statistics"
        }

# Global variable for lazy loading AI detector
_ai_detector = None

def get_ai_detector():
    """Lazy loading of AI detector model."""
    global _ai_detector
    if not HAS_TRANSFORMERS:
        return None
    
    if _ai_detector is None:
        try:
            import sys
            from pathlib import Path

            ops = Path(__file__).resolve().parents[3] / "40_operations" / "python"
            if str(ops) not in sys.path:
                sys.path.insert(0, str(ops))
            from common.gpu import resolve_device

            prefer = os.environ.get("AGENT_COMPUTE_DEVICE", "auto")
            dev = resolve_device(prefer)
            device = 0 if dev == "cuda" else -1
            _ai_detector = pipeline(
                "text-classification",
                model="roberta-base-openai-detector",
                device=device,
            )
        except Exception as e:
            print(f"Warning: Could not load AI detector model: {e}")
            print("  You can install with: pip install transformers torch")
            return None
    return _ai_detector

def check_ai_with_transformers(text: str, chunk_size: int = 512) -> Dict:
    """
    AI detection using transformers model (roberta-base-openai-detector).
    """
    detector = get_ai_detector()
    
    if detector is None:
        return {
            "status": "skipped",
            "message": "AI detector model not available. Install transformers and torch, or model download failed.",
            "tool": "transformers_ai_detector"
        }
    
    try:
        # Model works better with shorter texts, split if needed
        words = text.split()
        if len(words) > chunk_size:
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunks.append(' '.join(words[i:i+chunk_size]))
        else:
            chunks = [text]
        
        # Check each chunk
        ai_scores = []
        for chunk in chunks:
            try:
                result = detector(chunk, truncation=True, max_length=512)
                # Model returns label and score
                if isinstance(result, list):
                    result = result[0]
                
                # Convert to AI probability
                label = result.get("label", "").upper()
                score_val = result.get("score", 0.0)
                
                if label in ["AI", "FAKE", "GENERATED"] or "AI" in label:
                    ai_score = score_val
                else:
                    ai_score = 1.0 - score_val
                
                ai_scores.append(ai_score)
            except Exception as e:
                print(f"Warning: Error processing chunk: {e}")
                continue
        
        if not ai_scores:
            return {
                "status": "error",
                "message": "Could not process any chunks",
                "tool": "transformers_ai_detector"
            }
        
        avg_score = sum(ai_scores) / len(ai_scores)
        max_score = max(ai_scores)
        
        return {
            "status": "success",
            "score": avg_score,
            "max_score": max_score,
            "chunks_analyzed": len(chunks),
            "message": f"Average AI probability: {avg_score:.2%}",
            "tool": "transformers_ai_detector"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in transformers AI detection: {str(e)}",
            "tool": "transformers_ai_detector"
        }

def check_ai_combined(text: str) -> Dict:
    """
    Combines multiple methods for AI detection.
    """
    results = {}
    
    # 1. Transformers model (if available)
    transformer_result = check_ai_with_transformers(text)
    if transformer_result["status"] == "success":
        results["transformers"] = transformer_result["score"]
    
    # 2. Text statistics
    stats_result = analyze_text_statistics(text)
    if stats_result["status"] == "success":
        results["statistics"] = stats_result["score"]
    
    # 3. Basic heuristics (always available)
    basic_score = calculate_basic_ai_score(text)
    results["basic"] = basic_score
    
    # Combine results (weighted)
    weights = {
        "transformers": 0.6,
        "statistics": 0.25,
        "basic": 0.15
    }
    
    combined_score = 0.0
    total_weight = 0.0
    
    for method, score in results.items():
        if method in weights:
            combined_score += score * weights[method]
            total_weight += weights[method]
    
    if total_weight > 0:
        combined_score /= total_weight
    else:
        combined_score = basic_score  # Fallback
    
    component_message = ", ".join([f"{k}: {v:.2%}" for k, v in results.items()])
    
    return {
        "status": "success",
        "score": combined_score,
        "component_scores": results,
        "message": f"Combined AI probability: {combined_score:.2%} ({component_message})",
        "tool": "combined_ai_detector"
    }

def check_ai_score_only(text: str, fast_mode: bool = True) -> Dict:
    """
    Fast AI score check without plagiarism detection.
    Optimized for real-time checks during writing.
    
    Args:
        text: Text to check
        fast_mode: If True, uses only fast methods (basic_ai, text_statistics)
                  If False, includes transformers (slower but more accurate)
    
    Returns:
        Dictionary with:
        - score: AI probability (0-1)
        - recommendations: List of recommendations
        - method: Detection method used
    """
    if len(text) < 100:
        return {
            "score": 0.0,
            "recommendations": ["Text too short for reliable AI detection"],
            "method": "too_short",
            "status": "skipped"
        }
    
    results = {}
    
    # Always use basic heuristics (fastest)
    basic_score = calculate_basic_ai_score(text)
    results["basic"] = basic_score

    pattern_detail = None
    if HAS_PATTERN_SCAN:
        pattern_detail = scan_text(text)
        results["pattern_scan"] = pattern_detail.score
    
    # Use text statistics if available (fast)
    if HAS_TEXTSTAT and HAS_NUMPY:
        stats_result = analyze_text_statistics(text)
        if stats_result["status"] == "success" and "score" in stats_result:
            results["statistics"] = stats_result["score"]
    
    # Optionally use transformers (slower but more accurate)
    if not fast_mode and HAS_TRANSFORMERS:
        transformer_result = check_ai_with_transformers(text)
        if transformer_result["status"] == "success":
            results["transformers"] = transformer_result["score"]
    
    # Calculate weighted average (pattern_scan weighted when available)
    if "pattern_scan" in results and "statistics" in results:
        final_score = (
            results["basic"] * 0.2
            + results["pattern_scan"] * 0.45
            + results["statistics"] * 0.35
        )
        method = "basic_pattern_statistics"
    elif "pattern_scan" in results:
        final_score = results["basic"] * 0.35 + results["pattern_scan"] * 0.65
        method = "basic_pattern"
    elif len(results) == 1:
        final_score = basic_score
        method = "basic_only"
    elif len(results) == 2:
        final_score = results["basic"] * 0.4 + results["statistics"] * 0.6
        method = "basic_statistics"
    else:
        final_score = (
            results.get("basic", 0) * 0.2
            + results.get("statistics", 0) * 0.3
            + results.get("transformers", 0) * 0.5
        )
        method = "combined"
    
    # Generate recommendations based on score
    recommendations = []
    if final_score >= 0.8:
        recommendations.append("High AI probability detected. Significant revision needed.")
    elif final_score >= 0.5:
        recommendations.append("Moderate AI probability. Consider revising to sound more natural.")
    elif final_score >= 0.2:
        recommendations.append("Low AI probability. Minor revisions may help.")
    else:
        recommendations.append("Low AI probability. Text appears natural.")

    if pattern_detail:
        for rec in pattern_detail.recommendations[:5]:
            if rec not in recommendations:
                recommendations.append(rec)
    
    payload = {
        "score": final_score,
        "recommendations": recommendations,
        "method": method,
        "component_scores": results,
        "status": "success",
    }
    if pattern_detail:
        payload["pattern_scan"] = pattern_detail.to_dict()
    return payload

# ============================================================================
# Plagiarism Detection Functions
# ============================================================================

def check_copyleaks_plagiarism(text: str, file_path: Optional[str] = None) -> Dict:
    """
    Checks plagiarism using Copyleaks API.
    Requires Copyleaks API key.
    """
    api_key = API_CONFIG["copyleaks"]["api_key"]
    
    if not api_key:
        return {
            "status": "skipped",
            "message": "Copyleaks API key not set. Set COPYLEAKS_API_KEY environment variable.",
            "tool": "copyleaks"
        }
    
    try:
        # Copyleaks API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # For now return simulated result
        # Actual implementation would use Copyleaks API
        return {
            "status": "success",
            "similarity_score": 0.0,  # Placeholder
            "matches": 0,
            "message": "Copyleaks check (add actual API call)",
            "tool": "copyleaks"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in Copyleaks check: {str(e)}",
            "tool": "copyleaks"
        }

def check_local_similarity(text: str, reference_texts: List[str] = None) -> Dict:
    """
    Local similarity check with reference texts.
    Uses basic methods for text comparison (SequenceMatcher).
    """
    if not reference_texts:
        return {
            "status": "skipped",
            "message": "No reference texts for comparison",
            "tool": "local_similarity"
        }
    
    try:
        from difflib import SequenceMatcher
        
        max_similarity = 0.0
        matches = []
        
        for i, ref_text in enumerate(reference_texts):
            similarity = SequenceMatcher(None, text.lower(), ref_text.lower()).ratio()
            if similarity > max_similarity:
                max_similarity = similarity
            if similarity > 0.3:  # Threshold for "match"
                matches.append({
                    "reference": i,
                    "similarity": similarity
                })
        
        return {
            "status": "success",
            "similarity_score": max_similarity,
            "matches": len(matches),
            "message": f"Found {len(matches)} similar sections",
            "tool": "local_similarity"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in local check: {str(e)}",
            "tool": "local_similarity"
        }

def check_tfidf_similarity(text: str, reference_texts: List[str] = None) -> Dict:
    """
    TF-IDF based similarity check - better than SequenceMatcher for larger documents.
    Detects paraphrasing and partial matches using n-grams.
    """
    if not HAS_SKLEARN:
        return {
            "status": "skipped",
            "message": "scikit-learn not installed. Install with: pip install scikit-learn",
            "tool": "tfidf_similarity"
        }
    
    if not reference_texts:
        return {
            "status": "skipped",
            "message": "No reference texts for comparison",
            "tool": "tfidf_similarity"
        }
    
    try:
        # Use 1-3 grams for better paraphrasing detection
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            stop_words='english'  # Can be customized per language
        )
        
        # Vectorize all texts together
        all_texts = [text] + reference_texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Compare first text with all others
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        max_similarity = float(np.max(similarities))
        matches = [(i, float(sim)) for i, sim in enumerate(similarities) if sim > 0.3]
        
        return {
            "status": "success",
            "similarity_score": max_similarity,
            "matches": len(matches),
            "match_details": matches[:10],  # Top 10
            "message": f"Found {len(matches)} similar sections using TF-IDF",
            "tool": "tfidf_similarity"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in TF-IDF check: {str(e)}",
            "tool": "tfidf_similarity"
        }

# Global variable for lazy loading sentence transformer model
_embedding_model = None

def get_embedding_model():
    """Lazy loading of sentence transformer model - loads only once."""
    global _embedding_model
    if _embedding_model is None:
        try:
            # Use small fast model - can be replaced with larger for better accuracy
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            return None
    return _embedding_model

def check_semantic_similarity(text: str, reference_texts: List[str] = None, 
                              chunk_size: int = 512) -> Dict:
    """
    Semantic similarity check - detects similar meaning even if text is differently worded.
    Uses sentence-transformers for embeddings.
    """
    if not HAS_SENTENCE_TRANSFORMERS:
        return {
            "status": "skipped",
            "message": "sentence-transformers not installed. Install with: pip install sentence-transformers",
            "tool": "semantic_similarity"
        }
    
    if not reference_texts:
        return {
            "status": "skipped",
            "message": "No reference texts for comparison",
            "tool": "semantic_similarity"
        }
    
    try:
        model = get_embedding_model()
        if model is None:
            return {
                "status": "error",
                "message": "Could not load embedding model",
                "tool": "semantic_similarity"
            }
        
        # Split text into chunks if too long
        def chunk_text(txt, size=chunk_size):
            words = txt.split()
            chunks = []
            for i in range(0, len(words), size):
                chunks.append(' '.join(words[i:i+size]))
            return chunks if chunks else [txt]
        
        text_chunks = chunk_text(text)
        all_ref_chunks = []
        chunk_to_ref = []  # Mapping chunk -> reference index
        
        for ref_idx, ref_text in enumerate(reference_texts):
            chunks = chunk_text(ref_text)
            all_ref_chunks.extend(chunks)
            chunk_to_ref.extend([ref_idx] * len(chunks))
        
        if not all_ref_chunks:
            return {
                "status": "error",
                "message": "No reference chunks generated",
                "tool": "semantic_similarity"
            }
        
        # Generate embeddings
        text_embeddings = model.encode(text_chunks, show_progress_bar=False, convert_to_numpy=True)
        ref_embeddings = model.encode(all_ref_chunks, show_progress_bar=False, convert_to_numpy=True)
        
        # Find maximum similarity between any two chunks
        max_similarity = 0.0
        matches = []
        
        for text_emb in text_embeddings:
            similarities = cosine_similarity([text_emb], ref_embeddings).flatten()
            max_idx = np.argmax(similarities)
            max_sim = float(similarities[max_idx])
            
            if max_sim > max_similarity:
                max_similarity = max_sim
            
            if max_sim > 0.7:  # Threshold for semantic similarity
                matches.append({
                    "reference_index": chunk_to_ref[max_idx],
                    "similarity": max_sim
                })
        
        return {
            "status": "success",
            "similarity_score": max_similarity,
            "matches": len(matches),
            "match_details": matches[:10],
            "message": f"Found {len(matches)} semantically similar sections",
            "tool": "semantic_similarity"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in semantic similarity check: {str(e)}",
            "tool": "semantic_similarity"
        }

def check_combined_similarity(text: str, reference_texts: List[str] = None,
                              tfidf_weight: float = 0.6,
                              semantic_weight: float = 0.4) -> Dict:
    """
    Combines TF-IDF and semantic similarity for best results.
    """
    tfidf_result = check_tfidf_similarity(text, reference_texts)
    semantic_result = check_semantic_similarity(text, reference_texts)
    
    # Fallback to whichever works
    if tfidf_result["status"] != "success" and semantic_result["status"] != "success":
        return {
            "status": "error",
            "message": "Both TF-IDF and semantic similarity checks failed",
            "tool": "combined_similarity"
        }
    
    if tfidf_result["status"] != "success":
        return {**semantic_result, "tool": "combined_similarity", 
                "message": semantic_result["message"] + " (semantic only)"}
    
    if semantic_result["status"] != "success":
        return {**tfidf_result, "tool": "combined_similarity",
                "message": tfidf_result["message"] + " (TF-IDF only)"}
    
    # Combine results
    combined_score = (
        tfidf_result["similarity_score"] * tfidf_weight +
        semantic_result["similarity_score"] * semantic_weight
    )
    
    return {
        "status": "success",
        "similarity_score": combined_score,
        "tfidf_score": tfidf_result["similarity_score"],
        "semantic_score": semantic_result["similarity_score"],
        "matches": max(tfidf_result.get("matches", 0), semantic_result.get("matches", 0)),
        "message": f"Combined: TF-IDF {tfidf_result['similarity_score']:.2%}, "
                  f"Semantic {semantic_result['similarity_score']:.2%}",
        "tool": "combined_similarity"
    }

# ============================================================================
# Main Function
# ============================================================================

def check_ai_plagiarism(
    file_path: str,
    output_dir: Optional[str] = None,
    tools: Optional[List[str]] = None,
    translate_from_croatian: bool = False,
    save_translation: bool = False
) -> Dict:
    """
    Main function for checking AI writing and plagiarism.
    
    Args:
        file_path: Path to text file to check
        output_dir: Directory for saving results
        tools: List of tools to use (None = auto-select)
        translate_from_croatian: If True, translate Croatian text to English first
        save_translation: If True, save translated text to file
    """
    # Load text
    original_text = read_file(file_path)
    text = original_text
    text_length = len(text)
    
    # Translation workflow: Croatian -> English
    translation_info = None
    if translate_from_croatian:
        print("Detecting language and translating if needed...")
        detected_lang = detect_language(text)
        print(f"  Detected language: {detected_lang}")
        
        if detected_lang == 'hr':
            print("  Translating Croatian to English...")
            text, translation_info = translate_croatian_to_english(text)
            if translation_info.get("translation_successful"):
                print(f"  ✓ Translation successful (method: {translation_info['method']})")
                if save_translation:
                    translation_path = Path(file_path).parent / f"{Path(file_path).stem}_translated.txt"
                    with open(translation_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"  ✓ Translation saved to: {translation_path}")
            else:
                print(f"  ⚠ Translation failed: {translation_info.get('message', 'Unknown error')}")
                print("  Continuing with original text...")
        else:
            print(f"  Text is not Croatian ({detected_lang}), skipping translation")
    
    # Default output directory
    if not output_dir:
        output_dir = Path(file_path).parent / "ai_plagiarism_check"
    else:
        output_dir = Path(output_dir)
    
    # Default tools (improved defaults with new methods)
    if not tools:
        # Try to use advanced methods if available, fallback to basic
        tools = ["basic_ai", "local_similarity"]
        if HAS_SKLEARN:
            tools.append("tfidf_similarity")
        if HAS_SENTENCE_TRANSFORMERS:
            tools.append("semantic_similarity")
        if HAS_TEXTSTAT:
            tools.append("text_statistics")
    
    print(f"Checking: {file_path}")
    print(f"Text size: {text_length:,} characters")
    print(f"Tools: {', '.join(tools)}\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "file_path": file_path,
        "text_length": text_length,
        "tools_used": tools,
        "ai_detection": {},
        "plagiarism_detection": {},
        "recommendations": [],
        "translation": translation_info if translation_info else None
    }
    
    # Load reference texts once (used by multiple plagiarism checks)
    ref_dir = Path(file_path).parent / "references"
    reference_texts = []
    if ref_dir.exists():
        for ref_file in ref_dir.glob("*.txt"):
            try:
                with open(ref_file, 'r', encoding='utf-8') as f:
                    reference_texts.append(f.read())
            except:
                pass
    
    # AI Writing Detection
    print("Checking AI writing...")
    if "basic_ai" in tools or "gptzero" in tools:
        tool_name = "basic_ai" if "basic_ai" in tools else "gptzero"
        print(f"  - Basic AI detection...")
        results["ai_detection"][tool_name] = check_gptzero(text)
    
    if "openai" in tools:
        print("  - OpenAI classifier...")
        results["ai_detection"]["openai"] = check_openai_classifier(text)
    
    if "text_statistics" in tools:
        print("  - Text statistics (readability/stylometry)...")
        results["ai_detection"]["text_statistics"] = analyze_text_statistics(text)
    
    if "transformers_ai" in tools:
        print("  - Transformers AI detector (this may take a while on first run)...")
        results["ai_detection"]["transformers_ai"] = check_ai_with_transformers(text)
    
    if "combined_ai" in tools:
        print("  - Combined AI detection...")
        results["ai_detection"]["combined_ai"] = check_ai_combined(text)
    
    # Advanced detection methods
    if "bert" in tools:
        print("  - BERT-based detection...")
        try:
            from ai_detection_advanced import check_ai_with_bert
            results["ai_detection"]["bert"] = check_ai_with_bert(text)
        except ImportError:
            results["ai_detection"]["bert"] = {
                "status": "skipped",
                "message": "ai_detection_advanced module not found",
                "tool": "bert"
            }
    
    if "gradient_boosting" in tools:
        print("  - Gradient Boosting detection...")
        try:
            from ai_detection_advanced import check_ai_with_gradient_boosting
            results["ai_detection"]["gradient_boosting"] = check_ai_with_gradient_boosting(text)
        except ImportError:
            results["ai_detection"]["gradient_boosting"] = {
                "status": "skipped",
                "message": "ai_detection_advanced module not found",
                "tool": "gradient_boosting"
            }
    
    if "ensemble" in tools:
        print("  - Ensemble detection...")
        try:
            from ai_detection_advanced import check_ai_with_ensemble
            results["ai_detection"]["ensemble"] = check_ai_with_ensemble(text)
        except ImportError:
            results["ai_detection"]["ensemble"] = {
                "status": "skipped",
                "message": "ai_detection_advanced module not found",
                "tool": "ensemble"
            }
    
    if "ngram" in tools:
        print("  - N-gram detection...")
        try:
            from ai_detection_advanced import check_ai_with_ngrams
            results["ai_detection"]["ngram"] = check_ai_with_ngrams(text, ngram_type="both")
        except ImportError:
            results["ai_detection"]["ngram"] = {
                "status": "skipped",
                "message": "ai_detection_advanced module not found",
                "tool": "ngram"
            }
    
    if "robust" in tools:
        print("  - Robust (RADAR-inspired) detection...")
        try:
            from ai_detection_advanced import check_ai_robust
            results["ai_detection"]["robust"] = check_ai_robust(text)
        except ImportError:
            results["ai_detection"]["robust"] = {
                "status": "skipped",
                "message": "ai_detection_advanced module not found",
                "tool": "robust"
            }
    
    if "combined_advanced" in tools:
        print("  - Combined advanced detection...")
        try:
            from ai_detection_advanced import check_ai_combined_advanced
            results["ai_detection"]["combined_advanced"] = check_ai_combined_advanced(text)
        except ImportError:
            results["ai_detection"]["combined_advanced"] = {
                "status": "skipped",
                "message": "ai_detection_advanced module not found",
                "tool": "combined_advanced"
            }
    
    # Plagiarism Detection
    print("\nChecking plagiarism...")
    if "copyleaks" in tools:
        print("  - Copyleaks...")
        results["plagiarism_detection"]["copyleaks"] = check_copyleaks_plagiarism(text, file_path)
    
    if "local_similarity" in tools:
        print("  - Local similarity (SequenceMatcher)...")
        results["plagiarism_detection"]["local_similarity"] = check_local_similarity(
            text, reference_texts if reference_texts else None
        )
    
    if "tfidf_similarity" in tools:
        print("  - TF-IDF similarity (n-grams)...")
        results["plagiarism_detection"]["tfidf_similarity"] = check_tfidf_similarity(
            text, reference_texts if reference_texts else None
        )
    
    if "semantic_similarity" in tools:
        print("  - Semantic similarity (embeddings - this may take a while)...")
        results["plagiarism_detection"]["semantic_similarity"] = check_semantic_similarity(
            text, reference_texts if reference_texts else None
        )
    
    if "combined_similarity" in tools:
        print("  - Combined similarity (TF-IDF + Semantic)...")
        results["plagiarism_detection"]["combined_similarity"] = check_combined_similarity(
            text, reference_texts if reference_texts else None
        )
    
    # Generate recommendations
    print("\nGenerating recommendations...")
    results["recommendations"] = generate_recommendations(results)
    
    # Save results
    save_results(results, output_dir)
    
    # Show summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    # AI Detection summary
    if results["ai_detection"]:
        print("\nAI Writing Detection:")
        for tool, result in results["ai_detection"].items():
            if "score" in result:
                print(f"  {tool}: {result['score']:.1%}")
            elif "probability" in result:
                print(f"  {tool}: {result['probability']:.1%}")
    
    # Plagiarism Detection summary
    if results["plagiarism_detection"]:
        print("\nPlagiarism Detection:")
        for tool, result in results["plagiarism_detection"].items():
            if "similarity_score" in result:
                print(f"  {tool}: {result['similarity_score']:.1%}")
    
    # Recommendations
    if results["recommendations"]:
        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")
    
    print("\n" + "=" * 80)
    
    return results

# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="AI Writing Detection and Plagiarism Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_ai_plagiarism.py manuscript.txt
  python check_ai_plagiarism.py manuscript.txt --output-dir results
  python check_ai_plagiarism.py manuscript.txt --tools basic_ai,tfidf_similarity
  python check_ai_plagiarism.py manuscript.txt --tools combined_ai,combined_similarity
  python check_ai_plagiarism.py manuscript_hr.txt --translate-from-croatian
  python check_ai_plagiarism.py manuscript_hr.txt --translate-from-croatian --save-translation

Available Tools:
  AI Detection:
    - basic_ai: Basic heuristic-based AI detection (always available)
    - text_statistics: Stylometric analysis (requires: pip install textstat numpy)
    - transformers_ai: ML-based AI detection (requires: pip install transformers torch)
    - combined_ai: Combines all available AI detection methods
  
  Plagiarism Detection:
    - local_similarity: Basic SequenceMatcher (always available)
    - tfidf_similarity: TF-IDF with n-grams (requires: pip install scikit-learn)
    - semantic_similarity: Semantic embeddings (requires: pip install sentence-transformers)
    - combined_similarity: Combines TF-IDF and semantic methods

Note: Script automatically selects best available tools based on installed libraries.
      Place reference texts in 'references/' folder next to input file.

Translation (Croatian -> English workflow):
  --translate-from-croatian: Translate Croatian text to English before checking.
                             This workflow (write in Croatian, translate, check) can help
                             reduce AI detection scores by using natural translation patterns.
  --save-translation: Save translated text to file.

Translation requires one of:
  - googletrans: pip install googletrans==4.0.0rc1
  - OpenAI API key: export OPENAI_API_KEY="your_key"

API Keys (optional, for external services):
  export GPTZERO_API_KEY="your_key"
  export OPENAI_API_KEY="your_key"
  export COPYLEAKS_API_KEY="your_key"
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to file to check"
    )
    
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Directory for saving results (default: ai_plagiarism_check/)"
    )
    
    parser.add_argument(
        "--tools",
        "-t",
        help="Comma-separated list of tools. "
             "AI detection: basic_ai, text_statistics, transformers_ai, combined_ai. "
             "Plagiarism: local_similarity, tfidf_similarity, semantic_similarity, combined_similarity. "
             "(default: auto-selects based on available libraries)",
        default=None
    )
    
    parser.add_argument(
        "--translate-from-croatian",
        "-tr",
        action="store_true",
        help="Translate Croatian text to English before checking. "
             "Workflow: Write in Croatian (direct and simple) -> Translate to English -> Check AI score. "
             "This can help reduce AI detection scores by using natural translation patterns."
    )
    
    parser.add_argument(
        "--save-translation",
        "-st",
        action="store_true",
        help="Save translated text to file (only if --translate-from-croatian is used). "
             "Saves as <original_filename>_translated.txt"
    )
    
    args = parser.parse_args()
    
    # Check that file exists
    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' does not exist!")
        sys.exit(1)
    
    # Parse tools
    if args.tools:
        tools = [t.strip() for t in args.tools.split(",")]
    else:
        tools = None  # Will use smart defaults in check_ai_plagiarism
    
    # Run check
    try:
        check_ai_plagiarism(
            file_path=args.input_file,
            output_dir=args.output_dir,
            tools=tools,
            translate_from_croatian=args.translate_from_croatian,
            save_translation=args.save_translation
        )
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

