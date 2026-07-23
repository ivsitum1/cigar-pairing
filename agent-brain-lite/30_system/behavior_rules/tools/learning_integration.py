"""
Learning Loop Integration for All Tools — DEPRECATED for error learning.
For error/correction learning use: .cursor/40_operations/scripts/error_ops.py and .cursor/errors/error_log.jsonl.
This module remains for tool-interaction logging only.

This module provides automatic learning loop integration for all tools in the project.
All tools should use this module to log interactions and learn from outcomes.

Version: 1.0
Last Updated: 2026-01-27
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Path to learning log
LEARNING_LOG_PATH = Path(__file__).parent / "learning_log.json"
ASSISTANT_LOG_PATH = Path(__file__).parent / "assistant_learning_log.json"


class LearningLogger:
    """Logs tool interactions for learning loop."""
    
    def __init__(self, log_file: Path = LEARNING_LOG_PATH):
        self.log_file = log_file
        self.ensure_log_exists()
    
    def ensure_log_exists(self):
        """Create log file if it doesn't exist."""
        if not self.log_file.exists():
            initial_data = {
                "metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "total_sessions": 0,
                    "total_tasks": 0
                },
                "sessions": [],
                "patterns": {
                    "recurring_errors": [],
                    "successful_strategies": [],
                    "user_preferences": []
                },
                "adaptations": []
            }
            self._write_log(initial_data)
    
    def log_task(self, 
                 task_type: str,
                 task_description: str,
                 approach: str,
                 status: str,
                 files_modified: Optional[List[str]] = None,
                 error_occurred: bool = False,
                 error_type: Optional[str] = None,
                 user_feedback: Optional[str] = None,
                 self_assessment_score: Optional[float] = None,
                 learnings: Optional[Dict[str, List[str]]] = None,
                 discovery_metadata: Optional[Dict[str, Any]] = None):
        """
        Log a task execution.
        
        Args:
            task_type: Type of task (e.g., "code_generation", "analysis", "setup", "drug_discovery")
            task_description: Brief description of the task
            approach: Description of approach taken
            status: "success", "partial", or "failure"
            files_modified: List of files modified
            error_occurred: Whether an error occurred
            error_type: Type of error if occurred
            user_feedback: User feedback ("positive", "neutral", "negative", "none")
            self_assessment_score: Self-assessment score (1-10)
            learnings: Dict with "what_worked" and "what_failed" lists
            discovery_metadata: Optional dict for drug_discovery/discovery tasks: pipeline_variant, hypothesis_pivots, evidence_consistency_scores, council_score, red_team_flaws
        """
        log_data = self._read_log()
        
        session_id = f"{datetime.now().strftime('%Y%m%d')}-{len(log_data['sessions']) + 1:03d}"
        
        task_entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "task": {
                "type": task_type,
                "description": task_description,
                "complexity": self._estimate_complexity(task_description)
            },
            "execution": {
                "approach": approach,
                "files_modified": files_modified or [],
                "time_seconds": None,  # Can be added if timing available
                "iterations": 1
            },
            "outcome": {
                "status": status,
                "user_feedback": user_feedback or "none",
                "error_occurred": error_occurred,
                "error_type": error_type,
                "self_assessment_score": self_assessment_score
            },
            "learnings": learnings or {
                "what_worked": [],
                "what_failed": [],
                "insights": []
            }
        }
        if discovery_metadata:
            task_entry["discovery_metadata"] = discovery_metadata
        
        # Add to current session or create new session
        if not log_data["sessions"] or self._is_new_session(log_data["sessions"][-1]):
            log_data["sessions"].append({
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "tasks": [task_entry],
                "summary": {
                    "total_tasks": 1,
                    "successful": 1 if status == "success" else 0,
                    "failed": 1 if status == "failure" else 0,
                    "errors": 1 if error_occurred else 0,
                    "user_feedback": user_feedback or "none"
                }
            })
        else:
            log_data["sessions"][-1]["tasks"].append(task_entry)
            log_data["sessions"][-1]["summary"]["total_tasks"] += 1
            if status == "success":
                log_data["sessions"][-1]["summary"]["successful"] += 1
            elif status == "failure":
                log_data["sessions"][-1]["summary"]["failed"] += 1
            if error_occurred:
                log_data["sessions"][-1]["summary"]["errors"] += 1
        
        # Update metadata
        log_data["metadata"]["total_sessions"] = len(log_data["sessions"])
        log_data["metadata"]["total_tasks"] = sum(
            s["summary"]["total_tasks"] for s in log_data["sessions"]
        )
        log_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Update patterns (simplified - full analysis in separate function)
        if error_occurred and error_type:
            self._update_error_patterns(log_data, error_type, task_type)
        
        if status == "success" and approach:
            self._update_success_patterns(log_data, approach, task_type)
        
        self._write_log(log_data)
    
    def _read_log(self) -> Dict[str, Any]:
        """Read log file."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._create_empty_log()
    
    def _write_log(self, data: Dict[str, Any]):
        """Write log file."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _create_empty_log(self) -> Dict[str, Any]:
        """Create empty log structure."""
        return {
            "metadata": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "total_sessions": 0,
                "total_tasks": 0
            },
            "sessions": [],
            "patterns": {
                "recurring_errors": [],
                "successful_strategies": [],
                "user_preferences": []
            },
            "adaptations": []
        }
    
    def _is_new_session(self, last_session: Dict[str, Any]) -> bool:
        """Check if this is a new session (same day = same session)."""
        if not last_session:
            return True
        last_date = last_session["timestamp"][:10]
        current_date = datetime.now().isoformat()[:10]
        return last_date != current_date
    
    def _estimate_complexity(self, description: str) -> str:
        """Estimate task complexity."""
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["simple", "quick", "basic"]):
            return "low"
        elif any(word in desc_lower for word in ["complex", "multiple", "advanced"]):
            return "high"
        return "medium"
    
    def _update_error_patterns(self, log_data: Dict[str, Any], error_type: str, task_type: str):
        """Update recurring error patterns."""
        patterns = log_data["patterns"]["recurring_errors"]
        
        # Find existing pattern
        existing = next(
            (p for p in patterns if p.get("error_type") == error_type and p.get("task_type") == task_type),
            None
        )
        
        if existing:
            existing["frequency"] += 1
            existing["last_occurrence"] = datetime.now().isoformat()[:10]
        else:
            patterns.append({
                "error_type": error_type,
                "task_type": task_type,
                "frequency": 1,
                "first_occurrence": datetime.now().isoformat()[:10],
                "last_occurrence": datetime.now().isoformat()[:10],
                "resolution": None,
                "prevention_rule": None
            })
    
    def _update_success_patterns(self, log_data: Dict[str, Any], approach: str, task_type: str):
        """Update successful strategy patterns."""
        patterns = log_data["patterns"]["successful_strategies"]
        
        # Find existing pattern
        existing = next(
            (p for p in patterns if p.get("strategy") == approach and p.get("task_type") == task_type),
            None
        )
        
        if existing:
            existing["usage_count"] += 1
            existing["success_rate"] = min(1.0, existing.get("success_count", 0) / existing["usage_count"])
        else:
            patterns.append({
                "strategy": approach,
                "task_type": task_type,
                "usage_count": 1,
                "success_count": 1,
                "success_rate": 1.0,
                "recommended": True
            })


# Convenience functions for tools to use

def log_setup(project_name: str, study_type: str, status: str, error: Optional[str] = None):
    """Log project setup execution."""
    logger = LearningLogger()
    logger.log_task(
        task_type="setup",
        task_description=f"Setup project: {project_name} (type: {study_type})",
        approach=f"Automatic setup with study type detection",
        status=status,
        error_occurred=error is not None,
        error_type=error,
        learnings={
            "what_worked": [] if error else ["Automatic study type detection"],
            "what_failed": [error] if error else []
        }
    )


def log_analysis(analysis_type: str, method: str, status: str, learnings: Optional[Dict] = None):
    """Log statistical analysis execution."""
    logger = LearningLogger()
    logger.log_task(
        task_type="analysis",
        task_description=f"{analysis_type} analysis",
        approach=method,
        status=status,
        learnings=learnings
    )


def log_writing_check(ai_score_before: float, ai_score_after: float, strategies_used: List[str]):
    """Log AI writing detection check."""
    logger = LearningLogger()
    improved = ai_score_after < ai_score_before
    logger.log_task(
        task_type="writing_check",
        task_description="AI writing detection and revision",
        approach=f"Strategies: {', '.join(strategies_used)}",
        status="success" if improved else "partial",
        learnings={
            "what_worked": strategies_used if improved else [],
            "what_failed": [] if improved else ["Strategies did not reduce AI score"],
            "insights": [f"Score reduced from {ai_score_before:.1f}% to {ai_score_after:.1f}%"]
        }
    )


if __name__ == "__main__":
    # Example usage
    logger = LearningLogger()
    logger.log_task(
        task_type="setup",
        task_description="Test project setup",
        approach="Automatic detection",
        status="success",
        user_feedback="positive"
    )
    print("Learning log updated successfully!")
