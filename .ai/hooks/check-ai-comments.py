#!/usr/bin/env python3
"""
AI Comments Helper Script

Этот скрипт помогает AI быстро находить файлы без AI-комментариев
и добавлять их.

Usage:
    python3 .ai/hooks/check-ai-comments.py              # Check all files
    python3 .ai/hooks/check-ai-comments.py --fix        # Interactive fix
    python3 .ai/hooks/check-ai-comments.py --report     # Generate report
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Critical files that MUST have AI comments
CRITICAL_FILES = [
    "src/app.py",
    "src/config_manager.py",
    "core/domain/bot.py",
    "core/domain/user_session.py",
    "core/domain/conversation.py",
    "core/services/user_session_service.py",
    "adapters/storage/json_adapter.py",
    "start.py",
]

# High priority files that SHOULD have AI comments
HIGH_PRIORITY_FILES = [
    "src/api/v2/bots.py",
    "src/api/v2/system.py",
    "src/telegram_bot.py",
    "core/usecases/*.py",
]

# AI comment markers to look for
AI_COMMENT_MARKERS = [
    "AI-CRITICAL",
    "AI-CONTEXT",
    "AI-LINK",
    "AI-WARNING",
    "AI-HINT",
    "AI-TODO",
    "AI-DEPRECATED",
]

def has_ai_comments(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check if file has AI comments
    
    Returns:
        (has_comments, found_markers)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_markers = []
        for marker in AI_COMMENT_MARKERS:
            if marker in content:
                found_markers.append(marker)
        
        return len(found_markers) > 0, found_markers
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, []

def check_files(file_list: List[str]) -> Dict[str, any]:
    """Check list of files for AI comments"""
    results = {
        "total": 0,
        "with_comments": 0,
        "without_comments": [],
        "files": {}
    }
    
    for file_pattern in file_list:
        # Handle glob patterns
        if '*' in file_pattern:
            files = list(Path('.').glob(file_pattern))
        else:
            files = [Path(file_pattern)]
        
        for file_path in files:
            if not file_path.exists():
                continue
            if not file_path.is_file():
                continue
            if not str(file_path).endswith('.py'):
                continue
            
            results["total"] += 1
            has_comments, markers = has_ai_comments(file_path)
            
            results["files"][str(file_path)] = {
                "has_comments": has_comments,
                "markers": markers
            }
            
            if has_comments:
                results["with_comments"] += 1
            else:
                results["without_comments"].append(str(file_path))
    
    return results

def print_report(results: Dict):
    """Print nice report"""
    print("\n" + "="*70)
    print("🤖 AI COMMENTS REPORT")
    print("="*70 + "\n")
    
    print(f"📊 Total files checked: {results['total']}")
    print(f"✅ Files with AI comments: {results['with_comments']}")
    print(f"❌ Files without AI comments: {len(results['without_comments'])}")
    
    if results['without_comments']:
        print("\n📝 Files missing AI comments:")
        for file in results['without_comments']:
            print(f"   - {file}")
    
    print("\n" + "="*70)
    
    # Calculate coverage
    if results['total'] > 0:
        coverage = (results['with_comments'] / results['total']) * 100
        print(f"\n📈 AI Comment Coverage: {coverage:.1f}%")
        
        if coverage < 50:
            print("⚠️  LOW coverage - please add AI comments!")
        elif coverage < 80:
            print("👍 MEDIUM coverage - keep adding!")
        else:
            print("🎉 GOOD coverage!")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check AI comments in code")
    parser.add_argument('--report', action='store_true', help="Generate detailed report")
    parser.add_argument('--critical-only', action='store_true', help="Check only critical files")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    print("🤖 Checking AI comments in project...")
    print(f"📁 Project root: {project_root}")
    
    # Check critical files
    print("\n🔴 Checking CRITICAL files...")
    critical_results = check_files(CRITICAL_FILES)
    
    if not args.critical_only:
        print("\n🟡 Checking HIGH PRIORITY files...")
        high_priority_results = check_files(HIGH_PRIORITY_FILES)
        
        # Combine results
        combined = {
            "total": critical_results["total"] + high_priority_results["total"],
            "with_comments": critical_results["with_comments"] + high_priority_results["with_comments"],
            "without_comments": critical_results["without_comments"] + high_priority_results["without_comments"],
            "files": {**critical_results["files"], **high_priority_results["files"]}
        }
        print_report(combined)
    else:
        print_report(critical_results)
    
    # Exit code: 0 if all critical files have comments, 1 otherwise
    if critical_results["without_comments"]:
        print("\n❌ Some critical files are missing AI comments!")
        sys.exit(1)
    else:
        print("\n✅ All critical files have AI comments!")
        sys.exit(0)

if __name__ == "__main__":
    main()

