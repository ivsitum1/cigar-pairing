#!/usr/bin/env python3
"""
Real-Time Feedback System for Writing

This module provides real-time feedback during writing, including:
- Formatting warnings and suggestions
- Displaying issues in a user-friendly format
- Providing actionable recommendations

Usage:
    from writing_feedback import provide_realtime_feedback, format_warnings, format_suggestions
    
    feedback = provide_realtime_feedback(text)
    print(format_warnings(feedback))
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from writing_realtime_check import check_all_issues, Issue, IssueType


def format_warnings(issues: Dict[str, List[Issue]]) -> str:
    """
    Format warnings for display to the user.
    
    Args:
        issues: Dictionary of issues from check_all_issues()
        
    Returns:
        Formatted string with warnings
    """
    if not any(issues.values()):
        return "✓ No issues detected. Text looks good!"
    
    output = []
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    
    output.append(f"⚠️  {total_issues} issue(s) detected:\n")
    
    # Banned words
    if issues.get("banned_words"):
        output.append("📝 BANNED WORDS:")
        for issue in issues["banned_words"]:
            line_num, pos = issue.location
            output.append(f"  ⚠️  Line {line_num}, position {pos}: \"{issue.text}\"")
            output.append(f"     → {issue.suggestion}")
        output.append("")
    
    # AI phrases
    if issues.get("ai_phrases"):
        output.append("💬 AI PHRASES:")
        for issue in issues["ai_phrases"]:
            line_num, pos = issue.location
            output.append(f"  ⚠️  Line {line_num}, position {pos}: \"{issue.text}\"")
            output.append(f"     → {issue.suggestion}")
        output.append("")
    
    # Sentence patterns
    if issues.get("sentence_patterns"):
        output.append("📐 SENTENCE PATTERNS:")
        for issue in issues["sentence_patterns"]:
            line_num, pos = issue.location
            output.append(f"  ⚠️  Line {line_num}, position {pos}: {issue.text}")
            output.append(f"     → {issue.suggestion}")
        output.append("")
    
    return "\n".join(output)


def format_suggestions(issues: Dict[str, List[Issue]], max_suggestions: int = 5) -> str:
    """
    Format suggestions for improvement.
    
    Args:
        issues: Dictionary of issues from check_all_issues()
        max_suggestions: Maximum number of suggestions to show
        
    Returns:
        Formatted string with suggestions
    """
    if not any(issues.values()):
        return "No suggestions needed. Text is already well-written!"
    
    suggestions = []
    
    # Prioritize high-severity issues
    all_issues = []
    for issue_list in issues.values():
        all_issues.extend(issue_list)
    
    # Sort by severity (high > medium > low)
    severity_order = {"high": 3, "medium": 2, "low": 1}
    all_issues.sort(key=lambda x: severity_order.get(x.severity, 0), reverse=True)
    
    # Get top suggestions
    top_issues = all_issues[:max_suggestions]
    
    output = ["💡 TOP SUGGESTIONS FOR IMPROVEMENT:\n"]
    
    for i, issue in enumerate(top_issues, 1):
        line_num, pos = issue.location
        output.append(f"{i}. {issue.text} (Line {line_num})")
        output.append(f"   → {issue.suggestion}")
        output.append("")
    
    if len(all_issues) > max_suggestions:
        output.append(f"... and {len(all_issues) - max_suggestions} more issue(s)")
    
    return "\n".join(output)


def provide_realtime_feedback(text: str) -> Dict:
    """
    Provide real-time feedback on the text.
    
    Args:
        text: Text to check
        
    Returns:
        Dictionary with issues, warnings, and suggestions
    """
    issues = check_all_issues(text)
    
    warnings = format_warnings(issues)
    suggestions = format_suggestions(issues)
    
    # Calculate summary statistics
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    high_severity = sum(
        1 for issue_list in issues.values()
        for issue in issue_list
        if issue.severity == "high"
    )
    medium_severity = sum(
        1 for issue_list in issues.values()
        for issue in issue_list
        if issue.severity == "medium"
    )
    low_severity = sum(
        1 for issue_list in issues.values()
        for issue in issue_list
        if issue.severity == "low"
    )
    
    return {
        "issues": issues,
        "warnings": warnings,
        "suggestions": suggestions,
        "summary": {
            "total_issues": total_issues,
            "high_severity": high_severity,
            "medium_severity": medium_severity,
            "low_severity": low_severity
        }
    }


def display_feedback(feedback: Dict, show_summary: bool = True) -> None:
    """
    Display feedback in a formatted way.
    
    Args:
        feedback: Feedback dictionary from provide_realtime_feedback()
        show_summary: Whether to show summary statistics
    """
    print("=" * 60)
    print("REAL-TIME WRITING FEEDBACK")
    print("=" * 60)
    print()
    
    if show_summary:
        summary = feedback["summary"]
        print(f"Total Issues: {summary['total_issues']}")
        print(f"  - High severity: {summary['high_severity']}")
        print(f"  - Medium severity: {summary['medium_severity']}")
        print(f"  - Low severity: {summary['low_severity']}")
        print()
    
    print(feedback["warnings"])
    print()
    print(feedback["suggestions"])
    print("=" * 60)


if __name__ == "__main__":
    # Example usage
    sample_text = """
    This article will discuss the intricate complexities of the research.
    It is important to note that we delved into the realm of comprehensive analysis.
    The findings aren't just significant, they're pivotal to understanding the landscape.
    """
    
    feedback = provide_realtime_feedback(sample_text)
    display_feedback(feedback)
