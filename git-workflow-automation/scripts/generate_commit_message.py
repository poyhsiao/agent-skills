#!/usr/bin/env python3
"""
Generate a Conventional Commits compliant commit message from staged changes.
Analyzes git diff and suggests an appropriate commit message.
"""

import sys
import subprocess
import json
from typing import Dict, List, Tuple


def run_command(cmd: List[str]) -> str:
    """Run a shell command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def get_staged_diff() -> str:
    """Get the diff of staged changes."""
    return run_command(['git', 'diff', '--staged'])


def get_changed_files() -> List[str]:
    """Get list of staged files."""
    output = run_command(['git', 'diff', '--staged', '--name-only'])
    return [f for f in output.split('\n') if f]


def analyze_changes(diff: str, files: List[str]) -> Tuple[str, str, List[str]]:
    """
    Analyze changes and determine commit type, scope, and breaking changes.
    
    Returns:
        tuple: (type, scope, breaking_changes)
    """
    commit_type = "chore"
    scope = ""
    breaking_changes = []
    
    # Determine type based on files and diff content
    file_types = {
        'test': ['/test/', 'test_', '.test.', '.spec.'],
        'docs': ['/docs/', 'README', '.md'],
        'ci': ['.github/', '.gitlab-ci', 'Jenkinsfile', '.circleci/'],
        'build': ['package.json', 'pom.xml', 'build.gradle', 'Makefile', 'setup.py'],
        'style': ['.css', '.scss', '.sass', '.less'],
    }
    
    for file in files:
        if any(pattern in file for pattern in file_types['test']):
            commit_type = "test"
            break
        elif any(pattern in file for pattern in file_types['docs']):
            commit_type = "docs"
            break
        elif any(pattern in file for pattern in file_types['ci']):
            commit_type = "ci"
            break
        elif any(pattern in file for pattern in file_types['build']):
            commit_type = "build"
            break
        elif any(pattern in file for pattern in file_types['style']):
            commit_type = "style"
            break
    
    # Check diff content for type hints
    diff_lower = diff.lower()
    if 'new file mode' in diff or '+++ b/' in diff:
        if commit_type == "chore":
            commit_type = "feat"
    elif '--- a/' in diff and 'deleted file mode' in diff:
        commit_type = "refactor"
    elif 'fix' in diff_lower or 'bug' in diff_lower or 'issue' in diff_lower:
        commit_type = "fix"
    elif 'refactor' in diff_lower:
        commit_type = "refactor"
    elif 'performance' in diff_lower or 'perf' in diff_lower or 'optimize' in diff_lower:
        commit_type = "perf"
    
    # Try to determine scope from directory structure
    if files:
        common_dirs = set()
        for file in files:
            parts = file.split('/')
            if len(parts) > 1:
                common_dirs.add(parts[0])
        
        if len(common_dirs) == 1:
            scope = list(common_dirs)[0]
        elif len(common_dirs) <= 3:
            scope = ','.join(sorted(common_dirs))
    
    # Check for breaking changes
    if 'BREAKING CHANGE' in diff or 'breaking' in diff_lower:
        breaking_changes.append("API changes may affect existing functionality")
    
    return commit_type, scope, breaking_changes


def generate_message(commit_type: str, scope: str, files: List[str], 
                     breaking_changes: List[str]) -> str:
    """
    Generate a commit message.
    
    Args:
        commit_type: Type of commit (feat, fix, etc.)
        scope: Scope of changes
        files: List of changed files
        breaking_changes: List of breaking change descriptions
        
    Returns:
        str: Formatted commit message
    """
    # Generate a brief description based on files
    if len(files) == 1:
        description = f"update {files[0]}"
    elif len(files) <= 3:
        description = f"update {', '.join(files)}"
    else:
        description = f"update {len(files)} files"
    
    # Build commit message
    type_scope = f"{commit_type}({scope})" if scope else commit_type
    breaking_marker = "!" if breaking_changes else ""
    
    message = f"{type_scope}{breaking_marker}: {description}"
    
    # Add body with file list if many files
    if len(files) > 3:
        body = "\n\nModified files:\n"
        for file in files[:10]:  # Limit to 10 files in body
            body += f"- {file}\n"
        if len(files) > 10:
            body += f"... and {len(files) - 10} more files\n"
        message += body
    
    # Add breaking change footer
    if breaking_changes:
        message += "\n\nBREAKING CHANGE: " + " ".join(breaking_changes)
    
    return message


def main():
    """Main function."""
    # Check if there are staged changes
    staged_files = get_changed_files()
    if not staged_files:
        print("No staged changes found. Please stage your changes first with 'git add'.", 
              file=sys.stderr)
        sys.exit(1)
    
    # Get diff and analyze
    diff = get_staged_diff()
    commit_type, scope, breaking_changes = analyze_changes(diff, staged_files)
    
    # Generate message
    message = generate_message(commit_type, scope, staged_files, breaking_changes)
    
    # Output as JSON for easy parsing
    result = {
        "message": message,
        "type": commit_type,
        "scope": scope,
        "breaking": bool(breaking_changes),
        "files_count": len(staged_files)
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
