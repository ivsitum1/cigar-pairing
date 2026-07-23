#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assistant Learning Script
Enables the AI assistant to learn from its own work and improve over time.

Tracks:
- Tasks completed by assistant
- Approaches that worked/failed
- Code patterns learned
- User preferences discovered
- Tool usage patterns
- Error patterns and resolutions
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
from uuid import uuid4

# Paths
SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "assistant_learning_log.json"
BEHAVIOR_RULES_DIR = SCRIPT_DIR.parent

# Task types
TASK_TYPES = [
    "file_creation",
    "file_editing",
    "file_deletion",
    "code_generation",
    "code_refactoring",
    "analysis",
    "documentation",
    "bug_fix",
    "feature_implementation",
    "system_maintenance",
    "other"
]


def load_log() -> Dict:
    """Load assistant learning log from JSON file."""
    if not LOG_FILE.exists():
        return initialize_log()
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading log: {e}", file=sys.stderr)
        return initialize_log()


def initialize_log() -> Dict:
    """Initialize empty assistant learning log structure."""
    return {
        "metadata": {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_tasks": 0,
            "total_sessions": 0
        },
        "sessions": [],
        "patterns": {
            "successful_approaches": [],
            "common_errors": [],
            "user_preferences": [],
            "tool_usage_patterns": {},
            "code_patterns": [],
            "file_operation_patterns": {
                "files_created": {},
                "files_modified": {},
                "files_deleted": {}
            }
        },
        "learnings": {
            "what_works_well": [],
            "what_fails": [],
            "insights": [],
            "best_practices": []
        }
    }


def save_log(data: Dict) -> None:
    """Save assistant learning log to JSON file."""
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving log: {e}", file=sys.stderr)
        sys.exit(1)


def log_task(
    task_type: str,
    status: str,
    description: str = "",
    files_created: List[str] = None,
    files_modified: List[str] = None,
    files_deleted: List[str] = None,
    approach: str = "",
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    user_feedback: str = "none",
    iterations: int = 1,
    time_estimate: Optional[float] = None,
    what_worked: List[str] = None,
    what_failed: List[str] = None,
    insights: List[str] = None,
    code_patterns: List[str] = None,
    user_preferences: List[str] = None
) -> None:
    """Log a task execution to the assistant learning log."""
    log_data = load_log()
    
    # Get or create current session
    session_id = f"{datetime.now().strftime('%Y-%m-%d')}-{str(uuid4())[:8]}"
    
    # Create task entry
    task_entry = {
        "task_id": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "task_type": task_type,
        "description": description,
        "files_created": files_created or [],
        "files_modified": files_modified or [],
        "files_deleted": files_deleted or [],
        "approach": approach,
        "outcome": {
            "status": status,
            "user_feedback": user_feedback,
            "iterations": iterations,
            "time_estimate": time_estimate,
            "error_occurred": error_type is not None,
            "error_type": error_type,
            "error_message": error_message
        },
        "learnings": {
            "what_worked": what_worked or [],
            "what_failed": what_failed or [],
            "insights": insights or [],
            "code_patterns": code_patterns or [],
            "user_preferences": user_preferences or []
        }
    }
    
    # Add to current session or create new one
    today = datetime.now().strftime('%Y-%m-%d')
    current_session = None
    for session in log_data["sessions"]:
        if session["session_id"].startswith(today):
            current_session = session
            break
    
    if not current_session:
        current_session = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "tasks": [],
            "summary": {
                "total_tasks": 0,
                "successful": 0,
                "failed": 0,
                "partial": 0,
                "errors": 0
            }
        }
        log_data["sessions"].append(current_session)
    
    current_session["tasks"].append(task_entry)
    
    # Update session summary
    current_session["summary"]["total_tasks"] += 1
    if status == "success":
        current_session["summary"]["successful"] += 1
    elif status == "failure":
        current_session["summary"]["failed"] += 1
    elif status == "partial":
        current_session["summary"]["partial"] += 1
    if error_type:
        current_session["summary"]["errors"] += 1
    
    # Update patterns
    if what_worked:
        log_data["patterns"]["successful_approaches"].extend(what_worked)
    if what_failed:
        log_data["patterns"]["common_errors"].extend(what_failed)
    if user_preferences:
        log_data["patterns"]["user_preferences"].extend(user_preferences)
    if code_patterns:
        log_data["patterns"]["code_patterns"].extend(code_patterns)
    
    # Update file operation patterns
    for file in files_created or []:
        log_data["patterns"]["file_operation_patterns"]["files_created"][file] = \
            log_data["patterns"]["file_operation_patterns"]["files_created"].get(file, 0) + 1
    for file in files_modified or []:
        log_data["patterns"]["file_operation_patterns"]["files_modified"][file] = \
            log_data["patterns"]["file_operation_patterns"]["files_modified"].get(file, 0) + 1
    for file in files_deleted or []:
        log_data["patterns"]["file_operation_patterns"]["files_deleted"][file] = \
            log_data["patterns"]["file_operation_patterns"]["files_deleted"].get(file, 0) + 1
    
    # Update learnings
    if what_worked:
        log_data["learnings"]["what_works_well"].extend(what_worked)
    if what_failed:
        log_data["learnings"]["what_fails"].extend(what_failed)
    if insights:
        log_data["learnings"]["insights"].extend(insights)
    
    # Update metadata
    log_data["metadata"]["total_tasks"] += 1
    log_data["metadata"]["total_sessions"] = len(log_data["sessions"])
    
    save_log(log_data)
    print(f"[OK] Task logged: {task_type} - {status}")


def analyze_patterns(period: str = "weekly") -> Dict:
    """Analyze patterns in the assistant learning log."""
    log_data = load_log()
    
    if not log_data["sessions"]:
        print("No data to analyze.")
        return {}
    
    # Determine date range
    now = datetime.now()
    if period == "daily":
        cutoff = now - timedelta(days=1)
    elif period == "weekly":
        cutoff = now - timedelta(weeks=1)
    elif period == "monthly":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = datetime.min
    
    # Collect tasks from period
    all_tasks = []
    for session in log_data["sessions"]:
        session_date = datetime.fromisoformat(session["timestamp"])
        if session_date >= cutoff:
            all_tasks.extend(session["tasks"])
    
    if not all_tasks:
        print(f"No tasks found for period: {period}")
        return {}
    
    # Analyze patterns
    analysis = {
        "period": period,
        "total_tasks": len(all_tasks),
        "success_rate": sum(1 for t in all_tasks if t["outcome"]["status"] == "success") / len(all_tasks),
        "error_rate": sum(1 for t in all_tasks if t["outcome"]["error_occurred"]) / len(all_tasks),
        "task_type_distribution": {},
        "most_common_approaches": [],
        "most_common_errors": [],
        "file_operation_stats": {},
        "user_preferences": []
    }
    
    # Task type distribution
    task_types = [t["task_type"] for t in all_tasks]
    analysis["task_type_distribution"] = dict(Counter(task_types))
    
    # Successful approaches
    successful_approaches = []
    for task in all_tasks:
        if task["outcome"]["status"] == "success" and task["learnings"]["what_worked"]:
            successful_approaches.extend(task["learnings"]["what_worked"])
    analysis["most_common_approaches"] = [
        {"approach": approach, "count": count}
        for approach, count in Counter(successful_approaches).most_common(10)
    ]
    
    # Common errors
    errors = []
    for task in all_tasks:
        if task["outcome"]["error_occurred"]:
            errors.append(task["outcome"]["error_type"] or "unknown")
    analysis["most_common_errors"] = [
        {"error": error, "count": count}
        for error, count in Counter(errors).most_common(10)
    ]
    
    # File operation stats
    all_created = []
    all_modified = []
    for task in all_tasks:
        all_created.extend(task.get("files_created", []))
        all_modified.extend(task.get("files_modified", []))
    analysis["file_operation_stats"] = {
        "files_created": len(set(all_created)),
        "files_modified": len(set(all_modified)),
        "most_created": dict(Counter(all_created).most_common(5)),
        "most_modified": dict(Counter(all_modified).most_common(5))
    }
    
    # User preferences
    preferences = []
    for task in all_tasks:
        preferences.extend(task["learnings"].get("user_preferences", []))
    analysis["user_preferences"] = [
        {"preference": pref, "count": count}
        for pref, count in Counter(preferences).most_common(10)
    ]
    
    return analysis


def get_recommendations() -> List[Dict]:
    """Get improvement recommendations based on analysis."""
    analysis = analyze_patterns("weekly")
    
    if not analysis:
        return []
    
    recommendations = []
    
    # Check error rate
    if analysis["error_rate"] > 0.1:
        recommendations.append({
            "type": "error_reduction",
            "priority": "high",
            "issue": f"High error rate: {analysis['error_rate']:.1%}",
            "suggestion": "Review common errors and implement preventive measures",
            "action": "Analyze most_common_errors and update approaches"
        })
    
    # Check success rate
    if analysis["success_rate"] < 0.8:
        recommendations.append({
            "type": "success_improvement",
            "priority": "high",
            "issue": f"Low success rate: {analysis['success_rate']:.1%}",
            "suggestion": "Focus on approaches that work well",
            "action": "Review most_common_approaches and apply more frequently"
        })
    
    # Suggest using successful approaches more
    if analysis["most_common_approaches"]:
        top_approach = analysis["most_common_approaches"][0]
        recommendations.append({
            "type": "strategy_adoption",
            "priority": "medium",
            "issue": f"Successful approach used {top_approach['count']} times",
            "suggestion": f"Consider using '{top_approach['approach']}' as default for similar tasks",
            "action": f"Document '{top_approach['approach']}' as best practice"
        })
    
    return recommendations


def generate_report(period: str = "monthly") -> str:
    """Generate a learning report."""
    analysis = analyze_patterns(period)
    
    if not analysis:
        return "No data available for report generation."
    
    report_lines = [
        "=" * 80,
        f"ASSISTANT LEARNING REPORT - {period.upper()}",
        "=" * 80,
        "",
        f"Period: {period}",
        f"Total Tasks: {analysis['total_tasks']}",
        f"Success Rate: {analysis['success_rate']:.1%}",
        f"Error Rate: {analysis['error_rate']:.1%}",
        "",
        "TASK TYPE DISTRIBUTION:",
        "-" * 80,
    ]
    
    for task_type, count in sorted(analysis["task_type_distribution"].items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"  {task_type}: {count}")
    
    if analysis["most_common_approaches"]:
        report_lines.extend([
            "",
            "TOP SUCCESSFUL APPROACHES:",
            "-" * 80
        ])
        for item in analysis["most_common_approaches"][:5]:
            report_lines.append(f"  {item['approach']}: {item['count']} times")
    
    if analysis["most_common_errors"]:
        report_lines.extend([
            "",
            "MOST COMMON ERRORS:",
            "-" * 80
        ])
        for item in analysis["most_common_errors"][:5]:
            report_lines.append(f"  {item['error']}: {item['count']} occurrences")
    
    if analysis["file_operation_stats"]:
        stats = analysis["file_operation_stats"]
        report_lines.extend([
            "",
            "FILE OPERATIONS:",
            "-" * 80,
            f"  Files Created: {stats['files_created']}",
            f"  Files Modified: {stats['files_modified']}"
        ])
    
    if analysis["user_preferences"]:
        report_lines.extend([
            "",
            "USER PREFERENCES:",
            "-" * 80
        ])
        for item in analysis["user_preferences"][:5]:
            report_lines.append(f"  {item['preference']}: {item['count']} times")
    
    report_lines.extend([
        "",
        "=" * 80,
        f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80
    ])
    
    return "\n".join(report_lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Assistant Learning - Track and learn from assistant's work",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Log a task execution')
    log_parser.add_argument('--task-type', required=True, choices=TASK_TYPES, help='Task type')
    log_parser.add_argument('--status', required=True, choices=['success', 'partial', 'failure'],
                          help='Task status')
    log_parser.add_argument('--description', default='', help='Task description')
    log_parser.add_argument('--files-created', nargs='+', help='Files created')
    log_parser.add_argument('--files-modified', nargs='+', help='Files modified')
    log_parser.add_argument('--files-deleted', nargs='+', help='Files deleted')
    log_parser.add_argument('--approach', default='', help='Approach taken')
    log_parser.add_argument('--error-type', help='Error type if occurred')
    log_parser.add_argument('--error-message', help='Error message')
    log_parser.add_argument('--feedback', default='none',
                          choices=['positive', 'neutral', 'negative', 'none'],
                          help='User feedback')
    log_parser.add_argument('--iterations', type=int, default=1, help='Number of iterations')
    log_parser.add_argument('--time', type=float, help='Time estimate in seconds')
    log_parser.add_argument('--worked', nargs='+', help='What worked')
    log_parser.add_argument('--failed', nargs='+', help='What failed')
    log_parser.add_argument('--insights', nargs='+', help='Insights')
    log_parser.add_argument('--code-patterns', nargs='+', help='Code patterns')
    log_parser.add_argument('--preferences', nargs='+', help='User preferences')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze patterns')
    analyze_parser.add_argument('--period', default='weekly',
                              choices=['daily', 'weekly', 'monthly', 'all'],
                              help='Time period to analyze')
    
    # Recommend command
    subparsers.add_parser('recommend', help='Get improvement recommendations')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate learning report')
    report_parser.add_argument('--period', default='monthly',
                             choices=['daily', 'weekly', 'monthly', 'all'],
                             help='Time period for report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'log':
        log_task(
            task_type=args.task_type,
            status=args.status,
            description=args.description,
            files_created=args.files_created,
            files_modified=args.files_modified,
            files_deleted=args.files_deleted,
            approach=args.approach,
            error_type=args.error_type,
            error_message=args.error_message,
            user_feedback=args.feedback,
            iterations=args.iterations,
            time_estimate=args.time,
            what_worked=args.worked,
            what_failed=args.failed,
            insights=args.insights,
            code_patterns=args.code_patterns,
            user_preferences=args.preferences
        )
    
    elif args.command == 'analyze':
        analysis = analyze_patterns(args.period)
        if analysis:
            print(json.dumps(analysis, indent=2))
        else:
            print("No data to analyze.")
    
    elif args.command == 'recommend':
        recommendations = get_recommendations()
        if recommendations:
            print("\nIMPROVEMENT RECOMMENDATIONS:\n")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec['priority'].upper()}] {rec['type']}")
                print(f"   Issue: {rec['issue']}")
                print(f"   Suggestion: {rec['suggestion']}")
                print(f"   Action: {rec['action']}")
                print()
        else:
            print("No recommendations at this time.")
    
    elif args.command == 'report':
        report = generate_report(args.period)
        print(report)


if __name__ == "__main__":
    main()



