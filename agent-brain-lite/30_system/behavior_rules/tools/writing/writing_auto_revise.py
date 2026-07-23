#!/usr/bin/env python3
"""
Auto-Revision Engine for AI-Generated Text

This module automatically revises text to reduce AI detection scores by:
- Replacing banned words with suggestions
- Varying sentence beginnings and lengths
- Eliminating AI phrases
- Improving paragraph structure

Usage:
    from writing_auto_revise import auto_revise_text, identify_ai_issues, apply_fixes
    
    revised_text = auto_revise_text(text, ai_score=0.75)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from writing_realtime_check import (
    check_banned_words_realtime,
    check_ai_phrases,
    analyze_sentence_patterns,
    BANNED_WORDS,
    AI_PHRASES,
    suggest_replacements
)


def identify_ai_issues(text: str) -> Dict[str, List]:
    """
    Identify all AI-related issues in the text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with categorized issues
    """
    issues = {
        "banned_words": check_banned_words_realtime(text),
        "ai_phrases": check_ai_phrases(text),
        "sentence_patterns": analyze_sentence_patterns(text)
    }
    
    return issues


def apply_fixes(text: str, issues: Dict[str, List]) -> str:
    """
    Apply fixes to the text based on identified issues.
    
    Args:
        text: Original text
        issues: Dictionary of issues from identify_ai_issues()
        
    Returns:
        Revised text with fixes applied
    """
    revised_text = text
    lines = revised_text.split('\n')
    
    # Track changes to avoid double-processing
    changes_made = []
    
    # Fix banned words
    for issue in issues.get("banned_words", []):
        line_num, word_pos = issue.location
        if line_num <= len(lines):
            line = lines[line_num - 1]
            word = issue.text
            
            # Get replacement suggestions
            replacements = suggest_replacements(word)
            if replacements:
                # Use first suggestion
                replacement = replacements[0]
                
                # Replace word (case-insensitive, whole word only)
                pattern = r'\b' + re.escape(word) + r'\b'
                if re.search(pattern, line, re.IGNORECASE):
                    lines[line_num - 1] = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                    changes_made.append(f"Replaced '{word}' with '{replacement}'")
    
    # Fix AI phrases
    for issue in issues.get("ai_phrases", []):
        line_num, pos = issue.location
        if line_num <= len(lines):
            line = lines[line_num - 1]
            phrase = issue.text
            suggestion = issue.suggestion
            
            # Remove or replace phrase
            if "remove" in suggestion.lower() or "state directly" in suggestion.lower():
                # Remove the phrase
                pattern = re.escape(phrase)
                lines[line_num - 1] = re.sub(pattern, "", line, flags=re.IGNORECASE)
                changes_made.append(f"Removed phrase: '{phrase}'")
            else:
                # Replace with suggestion
                pattern = re.escape(phrase)
                replacement = suggestion.split(" or ")[0]  # Use first option
                lines[line_num - 1] = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                changes_made.append(f"Replaced phrase '{phrase}' with '{replacement}'")
    
    # Fix sentence patterns
    for issue in issues.get("sentence_patterns", []):
        line_num, pos = issue.location
        if line_num <= len(lines):
            line = lines[line_num - 1]
            suggestion = issue.suggestion
            
            # Handle different pattern types
            if "negation reframe" in issue.text.lower():
                # Split negation reframe: "X isn't just Y, it's Z" -> "X is Y. It also includes Z."
                pattern = r"(.+?)\s+isn't\s+just\s+(.+?),\s+it's\s+(.+?)"
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    x, y, z = match.groups()
                    new_line = f"{x} is {y}. It also includes {z}."
                    lines[line_num - 1] = new_line
                    changes_made.append("Fixed negation reframe pattern")
            
            elif "generic intro" in issue.text.lower():
                # Remove generic intro: "This article will discuss..." -> direct statement
                pattern = r"this\s+article\s+will\s+discuss\s*"
                lines[line_num - 1] = re.sub(pattern, "", line, flags=re.IGNORECASE)
                changes_made.append("Removed generic intro pattern")
            
            elif "generic sign-off" in issue.text.lower():
                # Remove generic sign-off: "In conclusion, this article shows..." -> direct conclusion
                pattern = r"in\s+conclusion,\s+this\s+article\s+shows\s*"
                lines[line_num - 1] = re.sub(pattern, "", line, flags=re.IGNORECASE)
                changes_made.append("Removed generic sign-off pattern")
            
            elif "excessive participial" in issue.text.lower():
                # Split participial clauses into simpler sentences
                # This is complex, so we'll just note it
                changes_made.append("Noted: Excessive participial clauses (manual review recommended)")
            
            elif "nominalization" in issue.text.lower():
                # Fix nominalizations: "lead to an increase in" -> "increase"
                pattern = r"lead\s+to\s+an\s+increase\s+in"
                lines[line_num - 1] = re.sub(pattern, "increase", line, flags=re.IGNORECASE)
                pattern = r"result\s+in\s+a\s+decrease\s+in"
                lines[line_num - 1] = re.sub(pattern, "decrease", line, flags=re.IGNORECASE)
                changes_made.append("Fixed nominalization")
    
    revised_text = '\n'.join(lines)
    
    return revised_text, changes_made


def vary_sentence_beginnings(text: str) -> str:
    """
    Vary sentence beginnings to avoid repetitive patterns.
    
    Args:
        text: Text to revise
        
    Returns:
        Text with varied sentence beginnings
    """
    sentences = re.split(r'([.!?]\s+)', text)
    revised_sentences = []
    
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            revised_sentences.append(sentence)
            continue
        
        # Check if sentence starts with "The [adjective] [noun]"
        pattern = r'^(The\s+\w+\s+\w+\s+(?:was|is|are))'
        match = re.match(pattern, sentence, re.IGNORECASE)
        if match and i > 0:
            # Vary the beginning occasionally
            if i % 3 == 0:  # Every third sentence
                # Try to start with a different pattern
                # For now, just note it (full implementation would require more context)
                pass
        
        revised_sentences.append(sentence)
    
    return ''.join(revised_sentences)


def vary_sentence_lengths(text: str) -> str:
    """
    Vary sentence lengths to avoid uniform mid-length sentences.
    
    Args:
        text: Text to revise
        
    Returns:
        Text with varied sentence lengths
    """
    sentences = re.split(r'([.!?]\s+)', text)
    revised_sentences = []
    
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            revised_sentences.append(sentence)
            continue
        
        words = sentence.split()
        word_count = len(words)
        
        # If sentence is mid-length (15-25 words) and we've had several similar, vary it
        if 15 <= word_count <= 25 and i > 2:
            # Check if previous sentences were similar length
            prev_lengths = []
            for j in range(max(0, i-3), i):
                if j < len(sentences) and sentences[j].strip():
                    prev_words = sentences[j].split()
                    prev_lengths.append(len(prev_words))
            
            if prev_lengths and all(15 <= pl <= 25 for pl in prev_lengths):
                # Split long sentence or combine short ones
                if word_count > 20:
                    # Split into two shorter sentences
                    mid_point = word_count // 2
                    first_part = ' '.join(words[:mid_point])
                    second_part = ' '.join(words[mid_point:])
                    revised_sentences.append(first_part + '. ')
                    revised_sentences.append(second_part.capitalize())
                else:
                    revised_sentences.append(sentence)
            else:
                revised_sentences.append(sentence)
        else:
            revised_sentences.append(sentence)
    
    return ''.join(revised_sentences)


def improve_paragraph_structure(text: str) -> str:
    """
    Improve paragraph structure by varying paragraph lengths.
    
    Args:
        text: Text to revise
        
    Returns:
        Text with improved paragraph structure
    """
    paragraphs = text.split('\n\n')
    revised_paragraphs = []
    
    for para in paragraphs:
        if not para.strip():
            revised_paragraphs.append(para)
            continue
        
        sentences = re.split(r'([.!?]\s+)', para)
        sentence_count = len([s for s in sentences if s.strip() and not re.match(r'^[.!?]\s*$', s)])
        
        # If paragraph is too uniform, add variation
        # For now, just return as-is (full implementation would require more analysis)
        revised_paragraphs.append(para)
    
    return '\n\n'.join(revised_paragraphs)


def auto_revise_text(text: str, ai_score: Optional[float] = None, max_iterations: int = 3) -> Tuple[str, Dict]:
    """
    Automatically revise text to reduce AI detection score.
    
    Args:
        text: Text to revise
        ai_score: Current AI score (if known)
        max_iterations: Maximum number of revision iterations
        
    Returns:
        Tuple of (revised_text, revision_info)
    """
    revision_info = {
        "iterations": 0,
        "changes_made": [],
        "final_score": None
    }
    
    current_text = text
    
    for iteration in range(max_iterations):
        revision_info["iterations"] = iteration + 1
        
        # Identify issues
        issues = identify_ai_issues(current_text)
        
        # Apply fixes
        revised_text, changes = apply_fixes(current_text, issues)
        revision_info["changes_made"].extend(changes)
        
        # Apply additional improvements
        revised_text = vary_sentence_beginnings(revised_text)
        revised_text = vary_sentence_lengths(revised_text)
        revised_text = improve_paragraph_structure(revised_text)
        
        # Check if we made progress
        if revised_text == current_text:
            # No more changes possible
            break
        
        current_text = revised_text
    
    revision_info["final_text"] = current_text
    
    return current_text, revision_info


if __name__ == "__main__":
    # Example usage
    sample_text = """
    This article will discuss the intricate complexities of the research.
    It is important to note that we delved into the realm of comprehensive analysis.
    The findings aren't just significant, they're pivotal to understanding the landscape.
    The comprehensive study showcases the multifaceted nature of the problem.
    """
    
    print("Original text:")
    print(sample_text)
    print("\n" + "=" * 60)
    
    revised_text, info = auto_revise_text(sample_text, ai_score=0.75)
    
    print("\nRevised text:")
    print(revised_text)
    print("\n" + "=" * 60)
    print(f"\nRevision info:")
    print(f"  Iterations: {info['iterations']}")
    print(f"  Changes made: {len(info['changes_made'])}")
    for change in info['changes_made']:
        print(f"    - {change}")
