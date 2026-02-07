#!/usr/bin/env python3
"""
Generate a PR description from commit messages and changed files.
Creates a structured description with summary, changes, and issue references.
"""

import sys
import subprocess
import json
from typing import List, Dict
from collections import defaultdict


def run_command(cmd: List[str]) -> str:
    """Run a shell command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def get_commit_info(base_branch: str = "main") -> List[Dict[str, str]]:
    """
    Get commit information from current branch.
    
    Args:
        base_branch: The base branch to compare against
        
    Returns:
        List of commit info dicts
    """
    current_branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    
    if current_branch == base_branch:
        # If on base branch, just get the last commit
        log_output = run_command([
            'git', 'log', '-1', '--pretty=%H%n%s%n%b%n---COMMIT_SEPARATOR---'
        ])
    else:
        log_output = run_command([
            'git', 'log', f'{base_branch}..HEAD', 
            '--pretty=%H%n%s%n%b%n---COMMIT_SEPARATOR---'
        ])
    
    if not log_output:
        return []
    
    commits = []
    for commit_block in log_output.split('---COMMIT_SEPARATOR---'):
        if not commit_block.strip():
            continue
        
        lines = commit_block.strip().split('\n')
        if len(lines) >= 2:
            commits.append({
                'hash': lines[0][:7],
                'subject': lines[1],
                'body': '\n'.join(lines[2:]) if len(lines) > 2 else ''
            })
    
    return commits


def get_changed_files(base_branch: str = "main") -> Dict[str, List[str]]:
    """
    Get changed files categorized by change type.
    
    Args:
        base_branch: The base branch to compare against
        
    Returns:
        Dict with 'added', 'modified', 'deleted' file lists
    """
    current_branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    
    if current_branch == base_branch:
        diff_output = run_command(['git', 'diff', '--name-status', 'HEAD~1'])
    else:
        diff_output = run_command(['git', 'diff', '--name-status', f'{base_branch}...HEAD'])
    
    files = defaultdict(list)
    
    for line in diff_output.split('\n'):
        if not line:
            continue
        parts = line.split('\t', 1)
        if len(parts) != 2:
            continue
        
        status, filepath = parts[0], parts[1]
        
        if status.startswith('A'):
            files['added'].append(filepath)
        elif status.startswith('M'):
            files['modified'].append(filepath)
        elif status.startswith('D'):
            files['deleted'].append(filepath)
        elif status.startswith('R'):
            files['renamed'].append(filepath)
    
    return files


def categorize_commits(commits: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """
    Categorize commits by type (feat, fix, docs, etc.).
    
    Args:
        commits: List of commit info dicts
        
    Returns:
        Dict mapping commit types to commit subjects
    """
    categories = defaultdict(list)
    
    for commit in commits:
        subject = commit['subject']
        
        # Parse conventional commit format
        if ':' in subject:
            type_part = subject.split(':', 1)[0]
            # Remove scope if present
            commit_type = type_part.split('(')[0].strip()
            categories[commit_type].append(subject)
        else:
            categories['other'].append(subject)
    
    return categories


def generate_description(commits: List[Dict[str, str]], 
                        files: Dict[str, List[str]],
                        issues: Dict[str, List[int]]) -> str:
    """
    Generate PR description.
    
    Args:
        commits: List of commit info
        files: Changed files by type
        issues: Issue numbers to close/reference
        
    Returns:
        Formatted PR description
    """
    description = []
    
    # Summary section
    description.append("## Summary\n")
    
    if len(commits) == 1:
        description.append(f"{commits[0]['subject']}\n")
    else:
        # Categorize commits
        categories = categorize_commits(commits)
        
        for commit_type in ['feat', 'fix', 'refactor', 'perf', 'docs', 'test', 'chore', 'other']:
            if commit_type in categories:
                type_name = commit_type.capitalize() if commit_type != 'other' else 'Other'
                description.append(f"**{type_name}:**\n")
                for commit_subject in categories[commit_type]:
                    description.append(f"- {commit_subject}\n")
                description.append("\n")
    
    # Changes section
    total_files = sum(len(f) for f in files.values())
    if total_files > 0:
        description.append("## Changes\n")
        description.append(f"**{total_files} file(s) changed**\n\n")
        
        if files['added']:
            description.append(f"**Added ({len(files['added'])}):**\n")
            for f in files['added'][:5]:
                description.append(f"- `{f}`\n")
            if len(files['added']) > 5:
                description.append(f"- ... and {len(files['added']) - 5} more\n")
            description.append("\n")
        
        if files['modified']:
            description.append(f"**Modified ({len(files['modified'])}):**\n")
            for f in files['modified'][:5]:
                description.append(f"- `{f}`\n")
            if len(files['modified']) > 5:
                description.append(f"- ... and {len(files['modified']) - 5} more\n")
            description.append("\n")
        
        if files['deleted']:
            description.append(f"**Deleted ({len(files['deleted'])}):**\n")
            for f in files['deleted'][:5]:
                description.append(f"- `{f}`\n")
            if len(files['deleted']) > 5:
                description.append(f"- ... and {len(files['deleted']) - 5} more\n")
            description.append("\n")
    
    # Related issues section
    if issues['closes'] or issues['references']:
        description.append("## Related Issues\n")
        
        if issues['closes']:
            for issue_num in issues['closes']:
                description.append(f"Closes #{issue_num}\n")
        
        if issues['references']:
            for issue_num in issues['references']:
                description.append(f"References #{issue_num}\n")
        
        description.append("\n")
    
    return ''.join(description).strip()


def main():
    """Main function."""
    base_branch = sys.argv[1] if len(sys.argv) > 1 else "main"
    issues_json = sys.argv[2] if len(sys.argv) > 2 else '{}'
    
    # Parse issues
    issues = json.loads(issues_json)
    if 'closes' not in issues:
        issues['closes'] = []
    if 'references' not in issues:
        issues['references'] = []
    
    # Get commit info and files
    commits = get_commit_info(base_branch)
    files = get_changed_files(base_branch)
    
    if not commits:
        print("No commits found", file=sys.stderr)
        sys.exit(1)
    
    # Generate description
    description = generate_description(commits, files, issues)
    
    print(description)


if __name__ == "__main__":
    main()
