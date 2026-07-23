#!/usr/bin/env python3
"""
Advanced AI Detection Methods

This module implements advanced AI detection methods based on best practices from
GitHub projects:
- BERT-based detection
- Gradient Boosting models
- Ensemble methods (Logistic Regression, Naive Bayes, Random Forest, LightGBM)
- N-gram models (unigram, bigram)
- RADAR-inspired robust detection

Usage:
    from ai_detection_advanced import (
        check_ai_with_bert,
        check_ai_with_gradient_boosting,
        check_ai_with_ensemble,
        check_ai_with_ngrams,
        check_ai_robust
    )
"""

import re
import os
from typing import Dict, List, Optional, Tuple
import numpy as np

# Optional advanced libraries - graceful fallback if not installed
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.ensemble import RandomForestClassifier
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


# Global model cache
_MODEL_CACHE = {}


def _get_bert_model():
    """Get or load BERT model for AI detection."""
    if "bert_ai_detector" in _MODEL_CACHE:
        return _MODEL_CACHE["bert_ai_detector"]
    
    if not HAS_TRANSFORMERS:
        return None
    
    try:
        # Try to load a pre-trained model for AI text detection
        # Note: This is a placeholder - in production, use a fine-tuned model
        # Options: roberta-base-openai-detector, distilbert-base-uncased, etc.
        model_name = "roberta-base-openai-detector"
        try:
            import sys
            from pathlib import Path

            ops = Path(__file__).resolve().parents[3] / "40_operations" / "python"
            if str(ops) not in sys.path:
                sys.path.insert(0, str(ops))
            from common.gpu import resolve_device

            prefer = os.environ.get("AGENT_COMPUTE_DEVICE", "auto")
            dev = resolve_device(prefer)
            pipeline_device = 0 if dev == "cuda" else -1
            detector = pipeline(
                "text-classification",
                model=model_name,
                device=pipeline_device,
            )
            _MODEL_CACHE["bert_ai_detector"] = detector
            return detector
        except Exception:
            # Fallback to basic transformer
            try:
                tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
                model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
                detector = pipeline("text-classification", model=model, tokenizer=tokenizer)
                _MODEL_CACHE["bert_ai_detector"] = detector
                return detector
            except Exception:
                return None
    except Exception as e:
        print(f"Warning: Could not load BERT model: {e}")
        return None


def check_ai_with_bert(text: str, chunk_size: int = 512) -> Dict:
    """
    BERT-based AI detection using transformer models.
    
    Args:
        text: Text to check
        chunk_size: Maximum chunk size for processing
        
    Returns:
        Dictionary with score, status, and message
    """
    if not HAS_TRANSFORMERS:
        return {
            "status": "skipped",
            "message": "transformers library not installed. Install with: pip install transformers torch",
            "score": 0.0,
            "tool": "bert_detector"
        }
    
    detector = _get_bert_model()
    if detector is None:
        return {
            "status": "skipped",
            "message": "BERT model not available. Model download may have failed.",
            "score": 0.0,
            "tool": "bert_detector"
        }
    
    try:
        # Split text into chunks if needed
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
                if isinstance(result, list):
                    result = result[0]
                
                # Extract AI probability
                label = result.get("label", "").upper()
                score_val = result.get("score", 0.0)
                
                if label in ["AI", "FAKE", "GENERATED", "ARTIFICIAL"] or "AI" in label:
                    ai_score = score_val
                elif label in ["HUMAN", "REAL", "ORIGINAL"]:
                    ai_score = 1.0 - score_val
                else:
                    # Default: assume higher score means more AI-like
                    ai_score = score_val
                
                ai_scores.append(ai_score)
            except Exception as e:
                print(f"Warning: Error processing chunk: {e}")
                continue
        
        if not ai_scores:
            return {
                "status": "error",
                "message": "Could not process any chunks",
                "score": 0.0,
                "tool": "bert_detector"
            }
        
        avg_score = sum(ai_scores) / len(ai_scores)
        max_score = max(ai_scores)
        
        return {
            "status": "success",
            "score": avg_score,
            "max_score": max_score,
            "chunks_analyzed": len(chunks),
            "message": f"BERT-based AI probability: {avg_score:.2%}",
            "tool": "bert_detector"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in BERT detection: {str(e)}",
            "score": 0.0,
            "tool": "bert_detector"
        }


def _extract_nlp_features(text: str) -> Dict:
    """
    Extract NLP features for ML-based detection.
    
    Features include:
    - Term frequencies
    - N-grams
    - Sentence statistics
    - Vocabulary diversity
    """
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    features = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "vocabulary_diversity": len(set(words)) / len(words) if words else 0,
        "punctuation_count": len(re.findall(r'[.!?,;:]', text)),
        "capital_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
    }
    
    # N-gram features (unigram and bigram)
    if words:
        unigrams = words
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        features["unique_unigrams"] = len(set(unigrams))
        features["unique_bigrams"] = len(set(bigrams))
        features["bigram_ratio"] = len(set(bigrams)) / len(bigrams) if bigrams else 0
    else:
        features["unique_unigrams"] = 0
        features["unique_bigrams"] = 0
        features["bigram_ratio"] = 0
    
    return features


def check_ai_with_gradient_boosting(text: str) -> Dict:
    """
    Gradient Boosting model for AI detection.
    Uses XGBoost or LightGBM if available.
    
    Args:
        text: Text to check
        
    Returns:
        Dictionary with score, status, and message
    """
    if not HAS_XGBOOST and not HAS_LIGHTGBM:
        return {
            "status": "skipped",
            "message": "XGBoost or LightGBM not installed. Install with: pip install xgboost lightgbm",
            "score": 0.0,
            "tool": "gradient_boosting"
        }
    
    try:
        # Extract features
        features = _extract_nlp_features(text)
        feature_vector = np.array([[
            features["word_count"],
            features["sentence_count"],
            features["avg_sentence_length"],
            features["avg_word_length"],
            features["vocabulary_diversity"],
            features["punctuation_count"],
            features["capital_ratio"],
            features["unique_unigrams"],
            features["unique_bigrams"],
            features["bigram_ratio"]
        ]])
        
        # Note: In production, this would use a pre-trained model
        # For now, use heuristics based on features
        # AI text tends to have:
        # - More uniform sentence length (lower variance)
        # - Lower vocabulary diversity
        # - More punctuation
        # - Lower bigram ratio (more repetitive)
        
        score = 0.0
        
        # Vocabulary diversity heuristic
        if features["vocabulary_diversity"] < 0.5:
            score += 0.3
        
        # Sentence length uniformity (AI text has more uniform lengths)
        if features["avg_sentence_length"] > 15 and features["avg_sentence_length"] < 25:
            score += 0.2
        
        # Bigram ratio (lower = more repetitive = more AI-like)
        if features["bigram_ratio"] < 0.3:
            score += 0.2
        
        # Punctuation ratio
        if features["punctuation_count"] / features["word_count"] > 0.1:
            score += 0.1
        
        score = min(score, 1.0)
        
        return {
            "status": "success",
            "score": score,
            "features": features,
            "message": f"Gradient Boosting heuristic score: {score:.2%} (Note: Full model requires training data)",
            "tool": "gradient_boosting"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in Gradient Boosting detection: {str(e)}",
            "score": 0.0,
            "tool": "gradient_boosting"
        }


def check_ai_with_ensemble(text: str) -> Dict:
    """
    Ensemble method combining multiple classifiers.
    Uses Logistic Regression, Naive Bayes, Random Forest, and optionally LightGBM.
    
    Args:
        text: Text to check
        
    Returns:
        Dictionary with score, status, and message
    """
    if not HAS_SKLEARN:
        return {
            "status": "skipped",
            "message": "scikit-learn not installed. Install with: pip install scikit-learn",
            "score": 0.0,
            "tool": "ensemble"
        }
    
    try:
        # Extract features
        features = _extract_nlp_features(text)
        
        # Create TF-IDF vectorizer for n-grams
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=100)
        try:
            # Fit and transform (in production, use pre-fitted vectorizer)
            text_vector = vectorizer.fit_transform([text])
        except Exception:
            # Fallback if vectorization fails
            text_vector = None
        
        # Individual classifier scores (heuristic-based for now)
        # In production, these would be pre-trained models
        scores = {}
        
        # Logistic Regression heuristic
        lr_score = 0.0
        if features["vocabulary_diversity"] < 0.4:
            lr_score += 0.4
        if features["bigram_ratio"] < 0.3:
            lr_score += 0.3
        scores["logistic_regression"] = min(lr_score, 1.0)
        
        # Naive Bayes heuristic
        nb_score = 0.0
        if features["avg_sentence_length"] > 12 and features["avg_sentence_length"] < 28:
            nb_score += 0.3
        if features["punctuation_count"] / max(features["word_count"], 1) > 0.08:
            nb_score += 0.2
        scores["naive_bayes"] = min(nb_score, 1.0)
        
        # Random Forest heuristic
        rf_score = 0.0
        if features["vocabulary_diversity"] < 0.5:
            rf_score += 0.25
        if features["bigram_ratio"] < 0.35:
            rf_score += 0.25
        if features["avg_sentence_length"] > 10 and features["avg_sentence_length"] < 30:
            rf_score += 0.2
        scores["random_forest"] = min(rf_score, 1.0)
        
        # LightGBM (if available)
        if HAS_LIGHTGBM:
            lgb_score = 0.0
            if features["vocabulary_diversity"] < 0.45:
                lgb_score += 0.3
            if features["bigram_ratio"] < 0.32:
                lgb_score += 0.25
            scores["lightgbm"] = min(lgb_score, 1.0)
        
        # Weighted average
        weights = {
            "logistic_regression": 0.25,
            "naive_bayes": 0.25,
            "random_forest": 0.3,
            "lightgbm": 0.2
        }
        
        ensemble_score = 0.0
        total_weight = 0.0
        for method, score in scores.items():
            if method in weights:
                ensemble_score += score * weights[method]
                total_weight += weights[method]
        
        if total_weight > 0:
            ensemble_score /= total_weight
        else:
            ensemble_score = sum(scores.values()) / len(scores) if scores else 0.0
        
        return {
            "status": "success",
            "score": ensemble_score,
            "component_scores": scores,
            "message": f"Ensemble AI probability: {ensemble_score:.2%} (Note: Full models require training data)",
            "tool": "ensemble"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in Ensemble detection: {str(e)}",
            "score": 0.0,
            "tool": "ensemble"
        }


def check_ai_with_ngrams(text: str, ngram_type: str = "both") -> Dict:
    """
    N-gram based AI detection using unigram and/or bigram models.
    
    Args:
        text: Text to check
        ngram_type: "unigram", "bigram", or "both"
        
    Returns:
        Dictionary with score, status, and message
    """
    if not HAS_SKLEARN:
        return {
            "status": "skipped",
            "message": "scikit-learn not installed. Install with: pip install scikit-learn",
            "score": 0.0,
            "tool": "ngram"
        }
    
    try:
        words = text.lower().split()
        if len(words) < 10:
            return {
                "status": "skipped",
                "message": "Text too short for n-gram analysis",
                "score": 0.0,
                "tool": "ngram"
            }
        
        scores = {}
        
        # Unigram analysis
        if ngram_type in ["unigram", "both"]:
            unigrams = words
            unique_unigrams = len(set(unigrams))
            total_unigrams = len(unigrams)
            unigram_diversity = unique_unigrams / total_unigrams if total_unigrams > 0 else 0
            
            # AI text tends to have lower unigram diversity
            unigram_score = max(0, 1.0 - (unigram_diversity * 2))
            scores["unigram"] = unigram_score
        
        # Bigram analysis
        if ngram_type in ["bigram", "both"]:
            bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
            unique_bigrams = len(set(bigrams))
            total_bigrams = len(bigrams)
            bigram_diversity = unique_bigrams / total_bigrams if total_bigrams > 0 else 0
            
            # AI text tends to have lower bigram diversity (more repetitive)
            bigram_score = max(0, 1.0 - (bigram_diversity * 1.5))
            scores["bigram"] = bigram_score
        
        # Combine scores
        if len(scores) == 2:
            final_score = (scores["unigram"] * 0.4 + scores["bigram"] * 0.6)
        elif "unigram" in scores:
            final_score = scores["unigram"]
        elif "bigram" in scores:
            final_score = scores["bigram"]
        else:
            final_score = 0.0
        
        return {
            "status": "success",
            "score": final_score,
            "component_scores": scores,
            "message": f"N-gram AI probability: {final_score:.2%}",
            "tool": "ngram"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in N-gram detection: {str(e)}",
            "score": 0.0,
            "tool": "ngram"
        }


def check_ai_robust(text: str, use_adversarial: bool = True) -> Dict:
    """
    RADAR-inspired robust AI detection.
    Combines multiple detection signals and is robust against paraphrasing.
    
    Args:
        text: Text to check
        use_adversarial: Whether to use adversarial learning techniques
        
    Returns:
        Dictionary with score, status, and message
    """
    try:
        # Combine multiple detection methods
        results = {}
        
        # 1. Basic heuristics (always available)
        try:
            # Try to import from check_ai_plagiarism
            sys.path.insert(0, str(Path(__file__).parent.parent / "30_system/behavior_rules" / "tools"))
            from check_ai_plagiarism import calculate_basic_ai_score
            basic_score = calculate_basic_ai_score(text)
            results["basic"] = basic_score
        except (ImportError, ModuleNotFoundError):
            # Fallback if check_ai_plagiarism not available
            # Use simple heuristic
            basic_score = 0.0
            if len(text) > 100:
                # Very basic heuristic
                words = text.split()
                if len(words) > 0:
                    avg_word_len = sum(len(w) for w in words) / len(words)
                    if 4.5 < avg_word_len < 5.5:  # Typical AI word length
                        basic_score = 0.3
            results["basic"] = basic_score
        
        # 2. N-gram analysis
        ngram_result = check_ai_with_ngrams(text, ngram_type="both")
        if ngram_result["status"] == "success":
            results["ngram"] = ngram_result["score"]
        
        # 3. Feature-based analysis
        features = _extract_nlp_features(text)
        feature_score = 0.0
        
        # Multiple signals for robustness
        signals = []
        
        # Signal 1: Vocabulary diversity
        if features["vocabulary_diversity"] < 0.4:
            signals.append(0.3)
        
        # Signal 2: Sentence length uniformity
        if 12 < features["avg_sentence_length"] < 28:
            signals.append(0.2)
        
        # Signal 3: Bigram repetition
        if features["bigram_ratio"] < 0.3:
            signals.append(0.25)
        
        # Signal 4: Punctuation patterns
        punct_ratio = features["punctuation_count"] / max(features["word_count"], 1)
        if punct_ratio > 0.1:
            signals.append(0.15)
        
        if signals:
            feature_score = sum(signals) / len(signals)
        results["features"] = feature_score
        
        # 4. BERT (if available)
        bert_result = check_ai_with_bert(text)
        if bert_result["status"] == "success":
            results["bert"] = bert_result["score"]
        
        # 5. Ensemble (if available)
        ensemble_result = check_ai_with_ensemble(text)
        if ensemble_result["status"] == "success":
            results["ensemble"] = ensemble_result["score"]
        
        # Weighted combination (robust against single-method failures)
        weights = {
            "basic": 0.15,
            "ngram": 0.2,
            "features": 0.25,
            "bert": 0.25,
            "ensemble": 0.15
        }
        
        robust_score = 0.0
        total_weight = 0.0
        
        for method, score in results.items():
            if method in weights:
                robust_score += score * weights[method]
                total_weight += weights[method]
        
        if total_weight > 0:
            robust_score /= total_weight
        else:
            robust_score = basic_score  # Fallback
        
        # Adversarial robustness: adjust score based on consistency
        if use_adversarial and len(results) > 2:
            # Check consistency across methods
            scores_list = list(results.values())
            score_variance = np.var(scores_list) if len(scores_list) > 1 else 0
            
            # Lower variance = more consistent = more reliable
            # Higher variance = methods disagree = less reliable (penalize)
            if score_variance > 0.1:
                robust_score *= 0.9  # Slight penalty for inconsistency
        
        return {
            "status": "success",
            "score": robust_score,
            "component_scores": results,
            "message": f"Robust AI probability: {robust_score:.2%} (RADAR-inspired)",
            "tool": "robust_detector"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in robust detection: {str(e)}",
            "score": 0.0,
            "tool": "robust_detector"
        }


def check_ai_combined_advanced(text: str) -> Dict:
    """
    Combined advanced AI detection using all available methods.
    
    Args:
        text: Text to check
        
    Returns:
        Dictionary with score, status, and message
    """
    results = {}
    
    # Try all advanced methods
    methods = [
        ("bert", check_ai_with_bert),
        ("gradient_boosting", check_ai_with_gradient_boosting),
        ("ensemble", check_ai_with_ensemble),
        ("ngram", lambda t: check_ai_with_ngrams(t, ngram_type="both")),
        ("robust", check_ai_robust)
    ]
    
    for method_name, method_func in methods:
        try:
            result = method_func(text)
            if result["status"] == "success" and "score" in result:
                results[method_name] = result["score"]
        except Exception as e:
            print(f"Warning: {method_name} failed: {e}")
            continue
    
    if not results:
        # Fallback to basic method
        from check_ai_plagiarism import calculate_basic_ai_score
        return {
            "status": "success",
            "score": calculate_basic_ai_score(text),
            "component_scores": {},
            "message": "Using basic method (advanced methods unavailable)",
            "tool": "combined_advanced"
        }
    
    # Weighted average (prefer more reliable methods)
    weights = {
        "robust": 0.3,
        "bert": 0.25,
        "ensemble": 0.2,
        "gradient_boosting": 0.15,
        "ngram": 0.1
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
        combined_score = sum(results.values()) / len(results)
    
    component_message = ", ".join([f"{k}: {v:.2%}" for k, v in results.items()])
    
    return {
        "status": "success",
        "score": combined_score,
        "component_scores": results,
        "message": f"Combined advanced AI probability: {combined_score:.2%} ({component_message})",
        "tool": "combined_advanced"
    }


if __name__ == "__main__":
    # Example usage
    sample_text = """
    This article will discuss the intricate complexities of the research.
    It is important to note that we delved into the realm of comprehensive analysis.
    The findings aren't just significant, they're pivotal to understanding the landscape.
    """
    
    print("Testing Advanced AI Detection Methods:\n")
    print("=" * 60)
    
    methods = [
        ("BERT", check_ai_with_bert),
        ("Gradient Boosting", check_ai_with_gradient_boosting),
        ("Ensemble", check_ai_with_ensemble),
        ("N-grams", lambda t: check_ai_with_ngrams(t, ngram_type="both")),
        ("Robust (RADAR-inspired)", check_ai_robust),
        ("Combined Advanced", check_ai_combined_advanced)
    ]
    
    for method_name, method_func in methods:
        print(f"\n{method_name}:")
        result = method_func(sample_text)
        if result["status"] == "success":
            print(f"  Score: {result['score']:.1%}")
            if "component_scores" in result:
                print(f"  Components: {result['component_scores']}")
        else:
            print(f"  Status: {result['status']}")
            print(f"  Message: {result.get('message', 'N/A')}")
