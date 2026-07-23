#!/usr/bin/env python3
"""
Integrated Writing Workflow with AI Score Check

This module implements the complete writing workflow:
Write → Real-time Check → AI Score Check → Auto-Revise → Re-check
Automatically iterates until AI score falls below 20% or max iterations reached.

Usage:
    from writing_workflow import write_with_ai_check
    
    result = write_with_ai_check(
        initial_text="Your text here",
        target_ai_score=0.20,
        max_iterations=5
    )
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from writing_realtime_check import check_all_issues, format_issues_for_display
from writing_auto_revise import auto_revise_text, identify_ai_issues
from writing_feedback import provide_realtime_feedback, display_feedback

# Import check_ai_score_only from check_ai_plagiarism
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "30_system/behavior_rules" / "tools"))
    from check_ai_plagiarism import check_ai_score_only
except ImportError:
    print("Warning: Could not import check_ai_score_only. Using fallback.")
    def check_ai_score_only(text, fast_mode=True):
        return {"score": 0.0, "status": "error", "message": "check_ai_plagiarism not available"}


def write_with_ai_check(
    initial_text: str,
    target_ai_score: float = 0.20,
    max_iterations: int = 5,
    fast_mode: bool = True,
    show_progress: bool = True
) -> Dict:
    """
    Complete writing workflow with automatic AI score checking and revision.
    
    Args:
        initial_text: Initial text to process
        target_ai_score: Target AI score threshold (default: 0.20 = 20%)
        max_iterations: Maximum number of revision iterations
        fast_mode: Use fast AI detection methods
        show_progress: Display progress messages
        
    Returns:
        Dictionary with:
        - final_text: Revised text
        - final_score: Final AI score
        - iterations: Number of iterations performed
        - revision_history: List of revisions with scores
        - success: Whether target score was achieved
    """
    current_text = initial_text
    revision_history = []
    
    if show_progress:
        print("=" * 60)
        print("INTEGRATED WRITING WORKFLOW")
        print("=" * 60)
        print(f"Target AI Score: < {target_ai_score:.0%}")
        print(f"Max Iterations: {max_iterations}")
        print()
    
    # Step 1: Real-time check for banned words and AI phrases
    if show_progress:
        print("Step 1: Real-time banned words and AI phrase check...")
    
    realtime_issues = check_all_issues(current_text)
    if any(realtime_issues.values()):
        if show_progress:
            print("⚠️  Issues detected during real-time check:")
            print(format_issues_for_display(
                realtime_issues["banned_words"] + 
                realtime_issues["ai_phrases"] + 
                realtime_issues["sentence_patterns"]
            ))
    else:
        if show_progress:
            print("✓ No issues detected in real-time check.")
    print()
    
    # Step 2: Initial AI score check
    if show_progress:
        print("Step 2: Initial AI score check...")
    
    ai_result = check_ai_score_only(current_text, fast_mode=fast_mode)
    current_score = ai_result.get("score", 1.0)
    
    revision_history.append({
        "iteration": 0,
        "score": current_score,
        "text": current_text,
        "changes": "Initial text"
    })
    
    if show_progress:
        print(f"Initial AI Score: {current_score:.1%}")
        print()
    
    # Check if already below target
    if current_score < target_ai_score:
        if show_progress:
            print(f"✓ Target achieved! AI score ({current_score:.1%}) is below threshold ({target_ai_score:.0%})")
        return {
            "final_text": current_text,
            "final_score": current_score,
            "iterations": 0,
            "revision_history": revision_history,
            "success": True
        }
    
    # Step 3: Iterative revision
    if show_progress:
        print("Step 3: Starting iterative revision...")
        print()
    
    for iteration in range(1, max_iterations + 1):
        if show_progress:
            print(f"Iteration {iteration}/{max_iterations}:")
            print(f"  Current AI Score: {current_score:.1%}")
        
        # Identify issues
        issues = identify_ai_issues(current_text)
        
        # Auto-revise
        revised_text, revision_info = auto_revise_text(
            current_text,
            ai_score=current_score,
            max_iterations=1  # One iteration per cycle
        )
        
        if revised_text == current_text:
            if show_progress:
                print("  No more changes possible. Stopping.")
            break
        
        # Re-check AI score
        ai_result = check_ai_score_only(revised_text, fast_mode=fast_mode)
        new_score = ai_result.get("score", current_score)
        
        revision_history.append({
            "iteration": iteration,
            "score": new_score,
            "text": revised_text,
            "changes": revision_info["changes_made"]
        })
        
        if show_progress:
            print(f"  New AI Score: {new_score:.1%}")
            if new_score < current_score:
                improvement = current_score - new_score
                print(f"  ✓ Improved by {improvement:.1%}")
            elif new_score > current_score:
                degradation = new_score - current_score
                print(f"  ⚠️  Worsened by {degradation:.1%}")
            else:
                print(f"  → No change")
            print()
        
        current_text = revised_text
        current_score = new_score
        
        # Check if target achieved
        if current_score < target_ai_score:
            if show_progress:
                print(f"✓ Target achieved! AI score ({current_score:.1%}) is below threshold ({target_ai_score:.0%})")
            return {
                "final_text": current_text,
                "final_score": current_score,
                "iterations": iteration,
                "revision_history": revision_history,
                "success": True
            }
    
    # Max iterations reached
    if show_progress:
        print(f"⚠️  Max iterations reached. Final AI Score: {current_score:.1%}")
        if current_score >= target_ai_score:
            print(f"   Target ({target_ai_score:.0%}) not achieved, but improvements were made.")
    
    return {
        "final_text": current_text,
        "final_score": current_score,
        "iterations": max_iterations,
        "revision_history": revision_history,
        "success": current_score < target_ai_score
    }


def display_workflow_summary(result: Dict) -> None:
    """
    Display a summary of the workflow results.
    
    Args:
        result: Result dictionary from write_with_ai_check()
    """
    print("=" * 60)
    print("WORKFLOW SUMMARY")
    print("=" * 60)
    print(f"Final AI Score: {result['final_score']:.1%}")
    print(f"Iterations: {result['iterations']}")
    print(f"Success: {'✓ Yes' if result['success'] else '✗ No'}")
    print()
    
    if result['revision_history']:
        print("Revision History:")
        for entry in result['revision_history']:
            print(f"  Iteration {entry['iteration']}: {entry['score']:.1%}")
            if entry['changes'] and isinstance(entry['changes'], list) and len(entry['changes']) > 0:
                print(f"    Changes: {len(entry['changes'])} modification(s)")
    print("=" * 60)


if __name__ == "__main__":
    # Example usage
    sample_text = """
    This article will discuss the intricate complexities of the research.
    It is important to note that we delved into the realm of comprehensive analysis.
    The findings aren't just significant, they're pivotal to understanding the landscape.
    The comprehensive study showcases the multifaceted nature of the problem.
    """
    
    result = write_with_ai_check(
        initial_text=sample_text,
        target_ai_score=0.20,
        max_iterations=5,
        fast_mode=True,
        show_progress=True
    )
    
    print()
    display_workflow_summary(result)
