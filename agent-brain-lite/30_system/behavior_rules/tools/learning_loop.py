#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Loop Script — DEPRECATED for error learning.
Error learning is unified in .cursor/40_operations/scripts/error_ops.py and .cursor/errors/error_log.jsonl.
This script remains for writing/domain-specific learning log analysis only.
Enables AI agents to learn from interactions, especially in statistics, medicine, and decision-making.

Provides:
- Automatic logging of interactions
- Pattern analysis (with focus on statistics, medicine, decisions)
- Adaptation recommendations
- Performance tracking
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
LOG_FILE = SCRIPT_DIR / "learning_log.json"
BEHAVIOR_RULES_DIR = SCRIPT_DIR.parent

# Knowledge domains to track
KNOWLEDGE_DOMAINS = ["statistics", "medicine", "decisions", "general"]

# Agent-specific learning domains
AGENT_DOMAINS = {
    "clinical_decision_support": [
        "clinical_reasoning", "guidelines", "risk_assessment", 
        "differential_diagnosis", "protocol_application"
    ],
    "clinical_research_methodologist": [
        "study_design", "protocols", "reporting", 
        "sample_size", "critical_appraisal"
    ],
    "code_quality_assurance": [
        "code_review", "reproducibility", "best_practices",
        "statistical_correctness", "error_patterns"
    ],
    "medical_data_science_coder": [
        "r_programming", "python_programming", "data_manipulation",
        "visualization", "performance_optimization"
    ],
    "prompt_engineering_specialist": [
        "prompt_design", "ai_interaction", "optimization",
        "template_effectiveness", "token_efficiency"
    ],
    "rules_roles_maintainer": [
        "consistency", "conflicts", "optimization",
        "system_health", "documentation"
    ],
    "statistical_analysis_expert": [
        "statistical_methods", "assumptions", "interpretation",
        "bayesian_analysis", "survival_analysis"
    ],
    "setup_workflow": [
        "project_setup", "study_type_detection", "structure_creation",
        "template_generation", "validation", "error_recovery",
        "user_preferences", "setup_patterns"
    ]
}


def load_log() -> Dict:
    """Load learning log from JSON file."""
    if not LOG_FILE.exists():
        return initialize_log()
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading log: {e}", file=sys.stderr)
        return initialize_log()


def initialize_log() -> Dict:
    """Initialize empty learning log structure."""
    return {
        "metadata": {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_tasks": 0
        },
        "sessions": [],
        "patterns": {
            "recurring_errors": [],
            "successful_strategies": [],
            "user_preferences": [],
            "knowledge_domain_performance": {
                "statistics": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "medicine": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "decisions": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "general": {"success_rate": 0.0, "task_count": 0, "common_errors": []}
            },
            "agent_performance": {
                "clinical_decision_support": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "clinical_research_methodologist": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "code_quality_assurance": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "medical_data_science_coder": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "prompt_engineering_specialist": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "rules_roles_maintainer": {"success_rate": 0.0, "task_count": 0, "common_errors": []},
                "statistical_analysis_expert": {"success_rate": 0.0, "task_count": 0, "common_errors": []}
            }
        },
        "adaptations": []
    }


def save_log(data: Dict) -> None:
    """Save learning log to JSON file."""
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving log: {e}", file=sys.stderr)
        sys.exit(1)


def detect_knowledge_domain(task_description: str, files_modified: List[str] = None) -> str:
    """Detect which knowledge domain a task belongs to."""
    task_lower = task_description.lower()
    
    # Statistics keywords
    stats_keywords = [
        "statistic", "regression", "analysis", "model", "hypothesis", "test",
        "p-value", "confidence", "interval", "meta-analysis", "bayesian",
        "clinical trial", "sample size", "power", "effect size"
    ]
    
    # Medicine keywords
    medicine_keywords = [
        "patient", "clinical", "diagnosis", "treatment", "therapy", "drug",
        "disease", "symptom", "anesthesia", "intensive care", "guideline",
        "medical", "healthcare", "outcome", "mortality", "morbidity"
    ]
    
    # Decision-making keywords
    decision_keywords = [
        "decision", "choice", "recommendation", "strategy", "approach",
        "select", "choose", "evaluate", "compare", "option", "alternative",
        "judgment", "conclusion", "interpretation"
    ]
    
    # Check statistics
    if any(kw in task_lower for kw in stats_keywords):
        return "statistics"
    
    # Check medicine
    if any(kw in task_lower for kw in medicine_keywords):
        return "medicine"
    
    # Check decisions
    if any(kw in task_lower for kw in decision_keywords):
        return "decisions"
    
    # Check file paths for domain indicators
    if files_modified:
        file_str = " ".join(files_modified).lower()
        if any(kw in file_str for kw in stats_keywords):
            return "statistics"
        if any(kw in file_str for kw in medicine_keywords):
            return "medicine"
    
    return "general"


def log_task(
    task_type: str,
    status: str,
    description: str = "",
    files_modified: List[str] = None,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    self_assessment_score: Optional[float] = None,
    user_feedback: str = "none",
    time_seconds: Optional[float] = None,
    what_worked: List[str] = None,
    what_failed: List[str] = None,
    insights: List[str] = None
) -> None:
    """Log a task execution to the learning log."""
    log_data = load_log()
    
    # Get or create current session
    session_id = f"{datetime.now().strftime('%Y-%m-%d')}-{str(uuid4())[:8]}"
    
    # Detect knowledge domain
    knowledge_domain = detect_knowledge_domain(description, files_modified or [])
    
    # Create task entry
    task_entry = {
        "task_id": str(uuid4()),
        "timestamp": datetime.now().isoformat(),
        "task": {
            "type": task_type,
            "description": description,
            "complexity": "low",  # Could be enhanced with ML
            "knowledge_domain": knowledge_domain
        },
        "execution": {
            "approach": description[:200] if description else "",
            "files_modified": files_modified or [],
            "time_seconds": time_seconds,
            "iterations": 1
        },
        "outcome": {
            "status": status,
            "user_feedback": user_feedback,
            "error_occurred": error_type is not None,
            "error_type": error_type,
            "error_message": error_message,
            "self_assessment_score": self_assessment_score
        },
        "learnings": {
            "what_worked": what_worked or [],
            "what_failed": what_failed or [],
            "insights": insights or []
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
                "errors": 0,
                "user_feedback": "neutral"
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
    if error_type:
        current_session["summary"]["errors"] += 1
    
    # Update knowledge domain performance
    domain_perf = log_data["patterns"]["knowledge_domain_performance"][knowledge_domain]
    domain_perf["task_count"] += 1
    if status == "success":
        # Update success rate
        total = domain_perf["task_count"]
        current_success = domain_perf.get("success_count", 0)
        domain_perf["success_count"] = current_success + 1
        domain_perf["success_rate"] = domain_perf["success_count"] / total
    
    if error_type:
        domain_perf["common_errors"].append({
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    # Update metadata
    log_data["metadata"]["total_tasks"] += 1
    log_data["metadata"]["total_sessions"] = len(log_data["sessions"])
    
    save_log(log_data)
    print(f"[OK] Task logged: {task_type} - {status} ({knowledge_domain})")


def analyze_patterns(period: str = "weekly", task_type_filter: Optional[str] = None) -> Dict:
    """Analyze patterns in the learning log. task_type_filter: e.g. 'drug_discovery' to restrict to discovery tasks."""
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
    
    if task_type_filter:
        if task_type_filter == "drug_discovery":
            all_tasks = [t for t in all_tasks if t.get("task", {}).get("type") in ("drug_discovery", "discovery")]
        else:
            all_tasks = [t for t in all_tasks if t.get("task", {}).get("type") == task_type_filter]
    
    if not all_tasks:
        print(f"No tasks found for period: {period}" + (f" (filter: {task_type_filter})" if task_type_filter else ""))
        return {}
    
    # Analyze patterns
    analysis = {
        "period": period,
        "task_type_filter": task_type_filter,
        "total_tasks": len(all_tasks),
        "success_rate": sum(1 for t in all_tasks if t["outcome"].get("status") == "success") / len(all_tasks),
        "error_rate": sum(1 for t in all_tasks if t["outcome"].get("error_occurred")) / len(all_tasks),
        "knowledge_domain_analysis": {},
        "recurring_errors": [],
        "successful_strategies": [],
        "performance_trends": {}
    }
    
    if task_type_filter == "drug_discovery":
        pivots = [t["discovery_metadata"]["hypothesis_pivots"] for t in all_tasks if t.get("discovery_metadata") and "hypothesis_pivots" in t["discovery_metadata"] and t["discovery_metadata"]["hypothesis_pivots"] is not None]
        council = [t["discovery_metadata"]["council_score"] for t in all_tasks if t.get("discovery_metadata") and "council_score" in t["discovery_metadata"] and t["discovery_metadata"]["council_score"] is not None]
        analysis["discovery_metrics"] = {
            "avg_hypothesis_pivots": sum(pivots) / len(pivots) if pivots else None,
            "avg_council_score": sum(council) / len(council) if council else None,
        }
    
    # Analyze by knowledge domain (use type as fallback when knowledge_domain missing)
    domain_tasks = defaultdict(list)
    for task in all_tasks:
        domain = task.get("task", {}).get("knowledge_domain") or task.get("task", {}).get("type", "general")
        domain_tasks[domain].append(task)
    
    for domain, tasks in domain_tasks.items():
        success_count = sum(1 for t in tasks if t.get("outcome", {}).get("status") == "success")
        error_count = sum(1 for t in tasks if t.get("outcome", {}).get("error_occurred"))
        
        analysis["knowledge_domain_analysis"][domain] = {
            "task_count": len(tasks),
            "success_rate": success_count / len(tasks) if tasks else 0,
            "error_rate": error_count / len(tasks) if tasks else 0,
            "avg_self_assessment": calculate_avg_score(tasks, "self_assessment_score")
        }
        
        # Collect errors
        errors = [t["outcome"]["error_type"] for t in tasks if t.get("outcome", {}).get("error_type")]
        if errors:
            error_counts = Counter(errors)
            analysis["recurring_errors"].extend([
                {"domain": domain, "error_type": err, "frequency": count}
                for err, count in error_counts.most_common(5)
            ])
        
        # Collect successful strategies
        for task in tasks:
            if task.get("outcome", {}).get("status") == "success" and (task.get("learnings") or {}).get("what_worked"):
                analysis["successful_strategies"].extend([
                    {"domain": domain, "strategy": strategy}
                    for strategy in (task.get("learnings") or {}).get("what_worked", [])
                ])
    
    # Sort recurring errors by frequency
    error_freq = Counter((e["domain"], e["error_type"]) for e in analysis["recurring_errors"])
    analysis["recurring_errors"] = sorted(
        analysis["recurring_errors"],
        key=lambda x: error_freq.get((x["domain"], x["error_type"]), 0),
        reverse=True
    )
    
    return analysis


def calculate_avg_score(tasks: List[Dict], score_field: str) -> float:
    """Calculate average score from tasks."""
    scores = [t["outcome"].get(score_field) for t in tasks if t["outcome"].get(score_field) is not None]
    return sum(scores) / len(scores) if scores else 0.0


def get_recommendations(task_type_filter: Optional[str] = None) -> List[Dict]:
    """Get adaptation recommendations based on analysis. task_type_filter: e.g. 'drug_discovery' to base on discovery sessions only."""
    log_data = load_log()
    analysis = analyze_patterns("weekly", task_type_filter=task_type_filter)
    
    if not analysis:
        return []
    
    recommendations = []
    if task_type_filter == "drug_discovery" and analysis.get("discovery_metrics"):
        dm = analysis["discovery_metrics"]
        if dm.get("avg_hypothesis_pivots") is not None and dm["avg_hypothesis_pivots"] > 1:
            recommendations.append({
                "type": "discovery_pivot",
                "priority": "medium",
                "domain": "drug_discovery",
                "issue": f"High average hypothesis pivots ({dm['avg_hypothesis_pivots']:.1f}) in discovery runs",
                "suggestion": "Consider tightening evidence-consistency threshold or improving initial ideation to reduce pivots",
                "action": "Review evidence consistency thresholds in 26_discovery_superpipeline.md",
            })
        if dm.get("avg_council_score") is not None and dm["avg_council_score"] < 70:
            recommendations.append({
                "type": "discovery_quality",
                "priority": "medium",
                "domain": "drug_discovery",
                "issue": f"Average council score below 70 ({dm['avg_council_score']:.1f})",
                "suggestion": "Strengthen Protocol Engine and Red Team pass before council",
                "action": "Review Protocol and Red Team steps in 26_discovery_superpipeline.md",
            })
    
    # Check for recurring errors
    error_freq = defaultdict(int)
    for error in analysis.get("recurring_errors", []):
        key = (error["domain"], error["error_type"])
        error_freq[key] += error["frequency"]
    
    for (domain, error_type), freq in error_freq.items():
        if freq >= 3:  # Minimum threshold
            recommendations.append({
                "type": "error_prevention",
                "priority": "high" if freq >= 5 else "medium",
                "domain": domain,
                "issue": f"Recurring {error_type} errors in {domain}",
                "frequency": freq,
                "suggestion": f"Add preventive rule or checklist for {error_type} in {domain} domain",
                "action": f"Update behavior rules to prevent {error_type} errors"
            })
    
    # Check domain performance
    for domain, perf in analysis.get("knowledge_domain_analysis", {}).items():
        if perf["success_rate"] < 0.7 and perf["task_count"] >= 5:
            recommendations.append({
                "type": "performance_improvement",
                "priority": "high",
                "domain": domain,
                "issue": f"Low success rate ({perf['success_rate']:.1%}) in {domain}",
                "suggestion": f"Review successful strategies and apply to {domain} tasks",
                "action": f"Analyze what_worked patterns for {domain} domain"
            })
    
    # Check for successful strategies that could be generalized
    strategy_counts = Counter(
        s["strategy"] for s in analysis.get("successful_strategies", [])
    )
    for strategy, count in strategy_counts.most_common(3):
        if count >= 3:
            recommendations.append({
                "type": "strategy_adoption",
                "priority": "medium",
                "domain": "general",
                "issue": f"Successful strategy used {count} times",
                "suggestion": f"Consider making '{strategy}' a default approach",
                "action": f"Document and promote '{strategy}' as best practice"
            })
    
    return recommendations


def generate_report(period: str = "monthly") -> str:
    """Generate a performance report."""
    analysis = analyze_patterns(period)
    
    if not analysis:
        return "No data available for report generation."
    
    report_lines = [
        "=" * 80,
        f"LEARNING LOOP PERFORMANCE REPORT - {period.upper()}",
        "=" * 80,
        "",
        f"Period: {period}",
        f"Total Tasks: {analysis['total_tasks']}",
        f"Overall Success Rate: {analysis['success_rate']:.1%}",
        f"Overall Error Rate: {analysis['error_rate']:.1%}",
        "",
        "KNOWLEDGE DOMAIN PERFORMANCE:",
        "-" * 80,
    ]
    
    # Sort domains by task count
    domains_sorted = sorted(
        analysis["knowledge_domain_analysis"].items(),
        key=lambda x: x[1]["task_count"],
        reverse=True
    )
    
    for domain, perf in domains_sorted:
        report_lines.extend([
            f"\n{domain.upper()}:",
            f"  Tasks: {perf['task_count']}",
            f"  Success Rate: {perf['success_rate']:.1%}",
            f"  Error Rate: {perf['error_rate']:.1%}",
            f"  Avg Self-Assessment: {perf['avg_self_assessment']:.1f}/10"
        ])
    
    # Recurring errors
    if analysis["recurring_errors"]:
        report_lines.extend([
            "",
            "RECURRING ERRORS:",
            "-" * 80
        ])
        for error in analysis["recurring_errors"][:10]:
            report_lines.append(
                f"  [{error['domain']}] {error['error_type']}: {error['frequency']} occurrences"
            )
    
    # Successful strategies
    if analysis["successful_strategies"]:
        strategy_counts = Counter(s["strategy"] for s in analysis["successful_strategies"])
        report_lines.extend([
            "",
            "TOP SUCCESSFUL STRATEGIES:",
            "-" * 80
        ])
        for strategy, count in strategy_counts.most_common(5):
            report_lines.append(f"  {strategy}: {count} successful uses")
    
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
        description="Learning Loop - Track and learn from agent interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Log a task execution')
    log_parser.add_argument('--task', required=True, help='Task type')
    log_parser.add_argument('--status', required=True, choices=['success', 'partial', 'failure'],
                          help='Task status')
    log_parser.add_argument('--description', default='', help='Task description')
    log_parser.add_argument('--files', nargs='+', help='Files modified')
    log_parser.add_argument('--error-type', help='Error type if occurred')
    log_parser.add_argument('--error-message', help='Error message')
    log_parser.add_argument('--score', type=float, help='Self-assessment score (0-10)')
    log_parser.add_argument('--feedback', default='none', 
                          choices=['positive', 'neutral', 'negative', 'none'],
                          help='User feedback')
    log_parser.add_argument('--time', type=float, help='Time in seconds')
    log_parser.add_argument('--worked', nargs='+', help='What worked')
    log_parser.add_argument('--failed', nargs='+', help='What failed')
    log_parser.add_argument('--insights', nargs='+', help='Insights')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze patterns')
    analyze_parser.add_argument('--period', default='weekly',
                              choices=['daily', 'weekly', 'monthly', 'all'],
                              help='Time period to analyze')
    analyze_parser.add_argument('--task-type', default='all',
                              choices=['all', 'drug_discovery'],
                              help='Filter by task type (drug_discovery = discovery + drug_discovery only)')
    
    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Get adaptation recommendations')
    recommend_parser.add_argument('--task-type', default='all',
                              choices=['all', 'drug_discovery'],
                              help='Base recommendations on this task type only')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate performance report')
    report_parser.add_argument('--period', default='monthly',
                             choices=['daily', 'weekly', 'monthly', 'all'],
                             help='Time period for report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'log':
        log_task(
            task_type=args.task,
            status=args.status,
            description=args.description,
            files_modified=args.files,
            error_type=args.error_type,
            error_message=args.error_message,
            self_assessment_score=args.score,
            user_feedback=args.feedback,
            time_seconds=args.time,
            what_worked=args.worked,
            what_failed=args.failed,
            insights=args.insights
        )
    
    elif args.command == 'analyze':
        task_filter = None if getattr(args, 'task_type', 'all') == 'all' else args.task_type
        analysis = analyze_patterns(args.period, task_type_filter=task_filter)
        if analysis:
            print(json.dumps(analysis, indent=2))
        else:
            print("No data to analyze.")
    
    elif args.command == 'recommend':
        task_filter = None if getattr(args, 'task_type', 'all') == 'all' else args.task_type
        recommendations = get_recommendations(task_type_filter=task_filter)
        if recommendations:
            print("\nADAPTATION RECOMMENDATIONS:\n")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec['priority'].upper()}] {rec['type']}")
                print(f"   Domain: {rec['domain']}")
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

