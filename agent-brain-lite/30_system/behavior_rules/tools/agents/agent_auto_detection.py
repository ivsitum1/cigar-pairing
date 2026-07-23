#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_auto_detection.py
Automatic agent detection from user prompts and context

Usage:
    from agent_auto_detection import detect_agent_from_prompt
    result = detect_agent_from_prompt("analyze data", context_files=["data.csv"])
"""

import re
import sys
from typing import List, Optional, Dict, Tuple
from pathlib import Path


def detect_agent_from_prompt(
    prompt: str,
    context_files: Optional[List[str]] = None,
    open_files: Optional[List[str]] = None
) -> Dict:
    """
    Detects the most appropriate agent based on user prompt and context.
    
    Args:
        prompt: User's prompt/query (str)
        context_files: List of file paths in context (optional)
        open_files: List of open file paths (optional)
    
    Returns:
        Dict with:
            - agent: Recommended agent name
            - confidence: Confidence score (0-1)
            - triggers: List of matched triggers
            - reasoning: Brief explanation
            - all_scores: Dict of scores for all agents
    """
    
    prompt_lower = prompt.lower()
    all_files = (context_files or []) + (open_files or [])
    
    # Agent trigger definitions (from 15_agent_roles.md)
    agent_triggers = {
        "statistical_analysis_expert": {
            "keywords": [
                "analyz", "analysis", "model", "regress", "test", "distribut", "p-value",
                "ci", "anova", "bayes", "statist", "hypothes", "effect",
                "meta-analysis", "survival", "cox", "kaplan",
                "power", "sample size", "imputat", "missing data", "bootstrap",
                "flexplot", "eda", "explorator"
            ],
            "file_patterns": [r"\.r$", r"\.rmd$", r"\.rdata$", r"\.rds$"],
            "file_keywords": ["analysis", "statistic", "model", "regression"]
        },
        "academic_writing_specialist": {
            "keywords": [
                "write", "draft", "manuscript", "section",
                "abstract", "discussion", "introduction", "methods", "results",
                "revise", "improve", "rewrite", "natural", "human-like",
                "prisma", "grade", "reporting", "citation", "reference"
            ],
            "file_patterns": ["manuscript", "paper", "draft", r"\.docx$", r"\.doc$"],
            "file_keywords": ["manuscript", "paper", "draft", "abstract", "introduction"]
        },
        "clinical_decision_support": {
            "keywords": [
                "patient", "clinical", "diagnos",
                "treatment", "therapy", "drug", "disease", "symptom",
                "anesthesia", "intensive care", "icu", "guideline", "protocol",
                "dosing", "risk", "assessment", "sbar", "differential"
            ],
            "file_patterns": ["protocol", "guideline", "clinical"],
            "file_keywords": ["clinical", "patient", "protocol", "guideline", "icu"]
        },
        "clinical_research_methodologist": {
            "keywords": [
                "design", "protocol", "methodolog",
                "methodology", "sample size", "randomiz", "randomization",
                "rct", "cohort", "case-control", "consort", "strobe",
                "power", "allocation", "blinding", "ethics"
            ],
            "file_patterns": ["protocol", "sap", "design"],
            "file_keywords": ["protocol", "design", "methodology", "sap", "consort"]
        },
        "medical_data_science_coder": {
            "keywords": [
                "code", "script", "function", "package", "install",
                "programming", "implement", "create script", "write code",
                "r script", "python", "data manipulation", "visualization",
                "performance", "optimization", "debug", "error",
                "prd", "ralph", "grill-me", "grill me", "product requirements",
                "vertical slice", "prd.json", "ralph loop", "ralph on",
            ],
            "file_patterns": [r"\.r$", r"\.py$", r"\.rmd$"],
            "file_keywords": ["script", "code", "function", "utils"]
        },
        "code_quality_assurance": {
            "keywords": [
                "check", "review", "verify", "quality",
                "test", "validate", "error", "bug", "fix", "correct",
                "reproducibility", "best practice", "standard"
            ],
            "file_patterns": [r"\.r$", r"\.py$", r"\.rmd$"],
            "file_keywords": ["test", "check", "validate", "quality"]
        },
        "output_controller": {
            "keywords": [
                "output gate", "output check", "kontrola outputa", "provjeri output",
                "final gate", "zero tolerance", "@output_ctrl", "@output-gate",
                "output controller", "isporuči", "deliver before", "release gate",
                "gate before deliver", "provjera outputa"
            ],
            "file_patterns": [r"manuscript", r"03_output", r"draft", r"\.docx$"],
            "file_keywords": ["output", "manuscript", "deliverable", "03_output"]
        },
        "prompt_engineering_specialist": {
            "keywords": [
                "prompt", "optimize", "improve", "efficiency", "token",
                "context", "cursor", "ai interaction", "template"
            ],
            "file_patterns": [],
            "file_keywords": []
        },
        "rules_roles_maintainer": {
            "keywords": [
                "rule", "role", "system", "consistency", "conflict",
                "maintain", "update", "documentation", "version"
            ],
            "file_patterns": ["30_system/behavior_rules", "agent", "rule"],
            "file_keywords": ["rule", "role", "system", "maintain"]
        },
        "discovery_engine": {
            "keywords": [
                "discovery", "drug discovery", "novel therapeutic", "research directions",
                "gap identification", "meddiscovery", "full discovery",
                "novel therapeutic strategy", "therapeutic strategy", "honeymoon"
            ],
            "file_patterns": ["discovery", "protocol"],
            "file_keywords": ["discovery", "protocol", "gap"]
        }
    }
    
    # Score each agent
    agent_scores = {}
    matched_triggers = {}
    
    for agent_name, triggers in agent_triggers.items():
        score = 0.0
        matched = []
        
        # Check keywords in prompt
        keyword_matches = sum(1 for kw in triggers["keywords"] 
                             if kw in prompt_lower)
        if keyword_matches > 0:
            score += keyword_matches * 0.3
            matched.append(f"keywords:{keyword_matches}")
        
        # Check file patterns
        if all_files:
            file_matches = sum(1 for f in all_files 
                              if any(re.search(pattern, f.lower(), re.IGNORECASE) 
                                    for pattern in triggers["file_patterns"]))
            if file_matches > 0:
                score += file_matches * 0.4
                matched.append(f"file_patterns:{file_matches}")
            
            # Check file keywords
            file_keyword_matches = sum(1 for f in all_files 
                                      if any(kw in f.lower() 
                                            for kw in triggers["file_keywords"]))
            if file_keyword_matches > 0:
                score += file_keyword_matches * 0.3
                matched.append(f"file_keywords:{file_keyword_matches}")
        
        agent_scores[agent_name] = score
        matched_triggers[agent_name] = matched
    
    # Find best agent
    best_agent = max(agent_scores, key=agent_scores.get)
    best_score = agent_scores[best_agent]
    
    # Normalize confidence: use the sum of all possible keyword weights as max
    max_possible = max(
        len(t["keywords"]) * 0.3 + len(t.get("file_patterns", [])) * 0.4 + len(t.get("file_keywords", [])) * 0.3
        for t in agent_triggers.values()
    )
    confidence = min(0.95, best_score / max(max_possible, 1.0)) if best_score > 0 else 0.0
    
    # If confidence is very low, default to general agent
    if confidence < 0.15:
        best_agent = "statistical_analysis_expert"
        confidence = 0.15
    
    # Generate reasoning
    triggers_str = ", ".join(matched_triggers[best_agent]) if matched_triggers[best_agent] else "No specific triggers matched, using default"
    reasoning = (
        f"Detected agent: {best_agent} "
        f"(confidence: {confidence * 100:.0f}%) | "
        f"Triggers: {triggers_str}"
    )

    skill_suggestions: list[dict] = []
    pipeline_auto_load: dict | None = None
    similar_errors: list[dict] = []
    try:
        repo_root = Path(__file__).resolve().parents[4]
        assist_root = repo_root / "40_operations" / "python"
        if str(assist_root) not in sys.path:
            sys.path.insert(0, str(assist_root))
        from brain_assist.skill_rerank import rank_skills
        from brain_assist.similar_errors import find_similar_errors

        skill_suggestions = rank_skills(
            prompt,
            top_k=5,
            dag_mode=True,
            auto_pipeline=True,
            context_files=all_files or None,
        )
        if skill_suggestions and skill_suggestions[0].get("pipeline_auto_load"):
            pipeline_auto_load = skill_suggestions[0]["pipeline_auto_load"]
            if best_score < 0.45:
                best_agent = "medical_data_science_coder"
                confidence = max(confidence, pipeline_auto_load.get("confidence", 0.5))
        similar_errors = find_similar_errors(prompt, top_k=3)
    except Exception:
        pass

    return {
        "agent": best_agent,
        "confidence": confidence,
        "triggers": matched_triggers[best_agent],
        "reasoning": reasoning,
        "all_scores": agent_scores,
        "skill_suggestions": skill_suggestions,
        "pipeline_auto_load": pipeline_auto_load,
        "similar_errors": similar_errors,
    }


def format_agent_name(agent_name: str) -> str:
    """Helper function to format agent name for display."""
    agent_display_names = {
        "statistical_analysis_expert": "Statistical Analysis Expert",
        "academic_writing_specialist": "Academic Writing Specialist",
        "clinical_decision_support": "Clinical Decision Support Agent",
        "clinical_research_methodologist": "Clinical Research Methodologist",
        "medical_data_science_coder": "Medical Data Science Coder",
        "code_quality_assurance": "Code Quality Assurance Agent",
        "output_controller": "Output Controller",
        "prompt_engineering_specialist": "Prompt Engineering Specialist",
        "rules_roles_maintainer": "Rules & Roles System Maintainer",
        "discovery_engine": "Discovery Engine (Pipeline 7A/7B)",
    }
    
    return agent_display_names.get(agent_name, agent_name)


AGENT_TO_ORCHESTRATOR = {
    "statistical_analysis_expert": "STATISTICS",
    "academic_writing_specialist": "WRITING",
    "clinical_decision_support": "CLINICAL",
    "clinical_research_methodologist": "METHODOLOGY",
    "medical_data_science_coder": "CODE_IMPL",
    "code_quality_assurance": "CODE_QA",
    "output_controller": "OUTPUT_CTRL",
    "prompt_engineering_specialist": "PROMPT_ENG",
    "rules_roles_maintainer": "RULES_MAINT",
    "discovery_engine": "DISCOVERY_DRUG",
}


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Detect agent from prompt")
    parser.add_argument("--prompt", "-p", required=True, help="User message/prompt")
    parser.add_argument("--files", "-f", default="", help="Comma-separated file paths")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    args = parser.parse_args()

    context_files = [f.strip() for f in args.files.split(",") if f.strip()]
    result = detect_agent_from_prompt(args.prompt, context_files=context_files)
    result["orchestrator_type"] = AGENT_TO_ORCHESTRATOR.get(result["agent"], result["agent"].upper())

    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "all_scores"}, ensure_ascii=False))
    else:
        print(f"Agent: {result['agent']} ({result['orchestrator_type']})")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
