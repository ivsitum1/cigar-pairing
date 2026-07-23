#!/usr/bin/env python3
"""
Fast AI Score Checker

Standalone script for fast AI score checking without plagiarism detection.
Optimized for real-time checks during writing workflow.

Usage:
    python check_ai_score_fast.py <text_file> [--fast]
    python check_ai_score_fast.py --text "Your text here" [--fast]
    
    --fast: Use only fast methods (basic_ai, text_statistics), skip transformers
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import check_ai_plagiarism functions
sys.path.insert(0, str(Path(__file__).parent.parent / "30_system/behavior_rules" / "tools"))

try:
    from check_ai_plagiarism import check_ai_score_only, read_file
except ImportError:
    print("Error: Could not import check_ai_plagiarism module.")
    print("Make sure 30_system/behavior_rules/tools/check_ai_plagiarism.py exists.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Fast AI score checker for real-time writing workflow"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input text file path (or use --text for direct input)"
    )
    parser.add_argument(
        "--text",
        help="Text to check directly (alternative to file input)"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use only fast methods (skip transformers)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Get text input
    if args.text:
        text = args.text
    elif args.input:
        try:
            text = read_file(args.input)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Either provide a file path or use --text option.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # Check AI score
    result = check_ai_score_only(text, fast_mode=args.fast)
    
    # Output results
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print("AI SCORE CHECK RESULTS")
        print("=" * 60)
        print(f"\nAI Probability: {result['score']:.1%}")
        print(f"Method: {result['method']}")
        
        if 'component_scores' in result:
            print("\nComponent Scores:")
            for method, score in result['component_scores'].items():
                print(f"  {method}: {score:.1%}")
        
        if 'recommendations' in result:
            print("\nRecommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
        
        print("\n" + "=" * 60)
        
        # Exit with appropriate code
        if result['score'] >= 0.2:
            sys.exit(1)  # High AI probability
        else:
            sys.exit(0)  # Low AI probability


if __name__ == "__main__":
    main()
