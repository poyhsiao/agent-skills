---
name: git-workflow-automation
description: Automate complete git workflow including commit with Conventional Commits format, push, GitHub PR creation with auto-generated descriptions, and automatic issue updates. Use this skill when the user wants to commit changes, create pull requests, or link/close GitHub issues. Triggers include 'commit and push', 'create PR', 'submit changes', 'finish feature', or any request to automate git and GitHub workflows. All output (commit messages, PR descriptions, issue comments) generated in English.
---

# Git Workflow Automation

Automates the complete git workflow from commit to PR creation with issue management.

## Workflow Overview

This skill provides a streamlined workflow that:

1. **Analyzes staged changes** and generates Conventional Commits compliant messages
2. **Commits changes** with properly formatted messages
3. **Pushes to remote** repository
4. **Creates GitHub PR** with auto-generated description
5. **Links and updates issues** based on commit messages
6. **Adds comments** to related issues
7. **Auto-closes issues** when appropriate

All generated content (commit messages, PR descriptions, issue comments) is in **English**.

## Prerequisites

Before using this skill, ensure:

- Git repository is initialized and has a remote
- GitHub CLI (`gh`) is installed and authenticated
- User has push access to the repository
- Changes are staged with `git add`

Check GitHub CLI auth status:
```bash
gh auth status
```

## Complete Workflow Steps

### Step 1: Stage Changes

Verify that changes are staged:

```bash
git status
```

If not staged, stage the files:
```bash
git add <files>
```

### Step 2: Generate Commit Message

Use the commit message generator to create a Conventional Commits compliant message:

```bash
python3 scripts/generate_commit_message.py
```

The script analyzes:
- Changed files and their types
- Diff content for context
- Common directories for scope
- Breaking changes indicators

Output format:
```json
{
  "message": "feat(api): add user authentication endpoint\n\nImplements JWT-based authentication...",
  "type": "feat",
  "scope": "api",
  "breaking": false,
  "files_count": 5
}
```

**Review and customize the message** as needed. The generated message is a starting point.

### Step 3: Commit Changes

Commit with the generated (or customized) message:

```bash
git commit -m "<message>"
```

For multi-line messages with body, use:
```bash
git commit -m "<subject>" -m "<body>"
```

### Step 4: Push to Remote

Push the current branch to remote:

```bash
git push -u origin $(git rev-parse --abbrev-ref HEAD)
```

If the branch already tracks remote:
```bash
git push
```

### Step 5: Extract Issue References

Extract issue numbers from commit messages:

```bash
python3 scripts/extract_issue_numbers.py [base_branch]
```

Default base branch is `main`. The script identifies:
- **Issues to close**: Using keywords (fixes, closes, resolves)
- **Issues to reference**: Using simple `#123` notation

Output:
```json
{
  "closes": [123, 456],
  "references": [789]
}
```

### Step 6: Generate PR Description

Generate a comprehensive PR description:

```bash
python3 scripts/generate_pr_description.py [base_branch] [issues_json]
```

The script creates a description with:
- **Summary**: Categorized commits by type (feat, fix, docs, etc.)
- **Changes**: List of added, modified, deleted files
- **Related Issues**: Automatically formatted with closing keywords

Example output:
```markdown
## Summary

**Feat:**
- feat(api): add user authentication endpoint
- feat(ui): implement login form

**Fix:**
- fix(auth): resolve token expiration issue

## Changes

**5 file(s) changed**

**Added (2):**
- `src/api/auth.ts`
- `src/components/LoginForm.tsx`

**Modified (3):**
- `src/App.tsx`
- `package.json`
- `README.md`

## Related Issues

Closes #123
Closes #456
References #789
```

### Step 7: Create GitHub PR

Create a PR using GitHub CLI with the generated description:

```bash
gh pr create \
  --title "<PR title from first commit or custom title>" \
  --body "<generated description>" \
  --base main
```

**Options:**
- `--draft`: Create as draft PR
- `--reviewer <username>`: Request reviewers
- `--assignee <username>`: Assign PR
- `--label <label>`: Add labels

The `Closes #123` keywords in the PR description will automatically link and close issues when the PR is merged.

### Step 8: Add Comments to Issues

For each referenced issue, add a comment linking to the PR:

```bash
gh issue comment <issue_number> --body "This has been addressed in PR #<pr_number>"
```

For issues that will be closed:
```bash
gh issue comment <issue_number> --body "This issue will be closed by PR #<pr_number>"
```

### Step 9: Verify

Check the created PR:
```bash
gh pr view
```

Verify issue linkage:
```bash
gh issue view <issue_number>
```

## Conventional Commits Format

This skill uses Conventional Commits format. See [conventional-commits.md](references/conventional-commits.md) for detailed specification.

**Quick reference:**

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Common types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Breaking changes:**
```
feat!: breaking change description
```

or

```
BREAKING CHANGE: description in footer
```

## Issue Linking Keywords

GitHub recognizes specific keywords for automatic issue closing. See [issue-keywords.md](references/issue-keywords.md) for complete list.

**Closing keywords:**
- `close`, `closes`, `closed`
- `fix`, `fixes`, `fixed`
- `resolve`, `resolves`, `resolved`

**Usage:**
```
fixes #123
closes #456, closes #789
```

## Automated Workflow Example

Complete example workflow:

```bash
# 1. Stage changes
git add src/api/auth.ts src/components/LoginForm.tsx

# 2. Generate commit message
COMMIT_DATA=$(python3 scripts/generate_commit_message.py)
COMMIT_MSG=$(echo "$COMMIT_DATA" | jq -r '.message')

# 3. Commit
git commit -m "$COMMIT_MSG"

# 4. Push
git push -u origin feature/user-auth

# 5. Extract issues
ISSUES=$(python3 scripts/extract_issue_numbers.py main)

# 6. Generate PR description
PR_DESC=$(python3 scripts/generate_pr_description.py main "$ISSUES")

# 7. Create PR
PR_URL=$(gh pr create --title "Add user authentication" --body "$PR_DESC" --base main)

# 8. Get PR number
PR_NUM=$(echo "$PR_URL" | grep -oE '[0-9]+$')

# 9. Comment on issues
for issue in $(echo "$ISSUES" | jq -r '.closes[]'); do
  gh issue comment $issue --body "This issue will be closed by PR #$PR_NUM"
done

for issue in $(echo "$ISSUES" | jq -r '.references[]'); do
  gh issue comment $issue --body "This has been addressed in PR #$PR_NUM"
done

echo "PR created: $PR_URL"
```

## Customization

### Custom Commit Message

If the generated commit message needs adjustments:

1. Generate the message
2. Review the output
3. Edit as needed
4. Commit with the customized message

### Custom PR Title

By default, use the first commit subject as PR title. To customize:

```bash
gh pr create --title "Your Custom Title" --body "$PR_DESC"
```

### Adding PR Metadata

```bash
gh pr create \
  --title "Add authentication" \
  --body "$PR_DESC" \
  --reviewer username1,username2 \
  --label feature,priority-high \
  --assignee @me
```

## Troubleshooting

### No staged changes

```
Error: No staged changes found
```

**Solution:** Stage your changes first:
```bash
git add <files>
```

### GitHub CLI not authenticated

```
Error: authentication required
```

**Solution:** Authenticate with GitHub:
```bash
gh auth login
```

### Base branch doesn't exist

```
Error: unknown revision
```

**Solution:** Specify correct base branch:
```bash
python3 scripts/extract_issue_numbers.py develop
python3 scripts/generate_pr_description.py develop
```

### Script execution permission

```
Error: Permission denied
```

**Solution:** Make scripts executable:
```bash
chmod +x scripts/*.py
```

## Best Practices

1. **Review generated content**: Always review commit messages and PR descriptions before using them
2. **Stage selectively**: Only stage related changes together for coherent commits
3. **Write clear commits**: Even with automation, clarity matters
4. **Reference issues early**: Include issue numbers in commit messages
5. **Test before pushing**: Ensure changes work before pushing
6. **Use draft PRs**: For work-in-progress, use `--draft` flag
7. **Request reviews**: Add reviewers when creating PRs for faster feedback

## Scripts Reference

### generate_commit_message.py

Analyzes staged changes and generates Conventional Commits message.

**Usage:**
```bash
python3 scripts/generate_commit_message.py
```

**Output:** JSON with message, type, scope, breaking flag, files count

### extract_issue_numbers.py

Extracts issue numbers from commit messages.

**Usage:**
```bash
python3 scripts/extract_issue_numbers.py [base_branch]
```

**Arguments:**
- `base_branch`: Base branch to compare against (default: main)

**Output:** JSON with closes and references arrays

### generate_pr_description.py

Generates PR description from commits and files.

**Usage:**
```bash
python3 scripts/generate_pr_description.py [base_branch] [issues_json]
```

**Arguments:**
- `base_branch`: Base branch to compare against (default: main)
- `issues_json`: JSON string from extract_issue_numbers.py (default: {})

**Output:** Markdown formatted PR description
