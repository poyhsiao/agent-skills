#!/usr/bin/env python3
"""
Extract issue numbers from commit messages.
Looks for patterns like #123, closes #456, fixes #789, etc.
"""

import sys
import re
import subprocess
import json
from typing import List, Dict, Set


def run_command(cmd: List[str]) -> str:
    """Run a shell command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def get_commit_messages(base_branch: str = "main") -> List[str]:
    """
    Get commit messages from current branch that are not in base branch.
    
    Args:
        base_branch: The base branch to compare against
        
    Returns:
        List of commit messages
    """
    # Get current branch
    current_branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    
    if current_branch == base_branch:
        # If on base branch, just get the last commit
        return [run_command(['git', 'log', '-1', '--pretty=%B'])]
    
    # Get commits not in base branch
    log_output = run_command([
        'git', 'log', f'{base_branch}..HEAD', '--pretty=%B%n---COMMIT_SEPARATOR---'
    ])
    
    if not log_output:
        return []
    
    commits = [c.strip() for c in log_output.split('---COMMIT_SEPARATOR---') if c.strip()]
    return commits


def extract_issues(messages: List[str]) -> Dict[str, List[int]]:
    """
    Extract issue numbers and their actions from commit messages.
    
    Args:
        messages: List of commit messages
        
    Returns:
        Dict with 'closes' and 'references' lists
    """
    # Keywords that close issues
    close_keywords = ['close', 'closes', 'closed', 'fix', 'fixes', 'fixed', 
                     'resolve', 'resolves', 'resolved']
    
    closes_issues: Set[int] = set()
    references_issues: Set[int] = set()
    
    for message in messages:
        # Pattern 1: "closes #123" or "fixes #123"
        close_pattern = r'\b(' + '|'.join(close_keywords) + r')\s+#(\d+)'
        for match in re.finditer(close_pattern, message, re.IGNORECASE):
            issue_num = int(match.group(2))
            closes_issues.add(issue_num)
        
        # Pattern 2: Just "#123" (reference only)
        ref_pattern = r'#(\d+)'
        for match in re.finditer(ref_pattern, message):
            issue_num = int(match.group(1))
            # Only add as reference if not already in closes
            if issue_num not in closes_issues:
                references_issues.add(issue_num)
    
    return {
        "closes": sorted(list(closes_issues)),
        "references": sorted(list(references_issues))
    }


def main():
    """Main function."""
    # Check if input is provided via stdin or arguments
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        # If argument provided and doesn't look like a flag, treat as test message
        test_message = ' '.join(sys.argv[1:])
        messages = [test_message]
    elif not sys.stdin.isatty():
        # Read from stdin
        messages = [sys.stdin.read()]
    else:
        # Get from git log
        base_branch = "main"
        messages = get_commit_messages(base_branch)
    
    if not messages:
        print(json.dumps({"closes": [], "references": []}))
        return
    
    # Extract issues
    issues = extract_issues(messages)
    
    print(json.dumps(issues, indent=2))


if __name__ == "__main__":
    main()
