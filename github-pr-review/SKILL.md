---
name: github-pr-review
description: GitHub Pull Request (PR) review tool. Use this for: (1) Reviewing specific PRs (e.g., "Review #123" or "Review PR #123"), (2) Listing and reviewing all pending PRs, (3) Analyzing code changes and providing improvement suggestions, (4) Adding review comments to PR or generating Markdown reports. Default behavior saves reviews to `.issues/review/{pr_number}/{review_count}-{status}.md` unless explicitly requested to update PR directly.
---

# GitHub PR Review

## Workflow Decision Tree

Start → Is PR specified?
- Yes: Continue reviewing that PR
- No: List all pending PRs and let user choose

## Prerequisites

### Install `gh` CLI

This skill prioritizes using `gh` (GitHub CLI). If not installed, guide user to install:

```bash
# macOS
brew install gh

# Linux
# Visit https://cli.github.com/ for installation instructions
```

Verify installation:
```bash
gh --version
```

### GitHub Authentication

Configure `gh` with GitHub authentication:
```bash
gh auth login
```

Or set environment variable:
```bash
export GITHUB_TOKEN=your_personal_access_token
```

## Reviewing PRs

### Get PR List

When no specific PR is specified, list all pending PRs:

```bash
# List all open PRs in current repository
gh pr list --state open

# List PRs by author
gh pr list --author <username>

# List PRs targeted to specific branch
gh pr list --base <branch-name>
```

PR list should include:
- PR number and title
- Author
- Target branch
- Creation date
- Status (open, closed, merged)

### Get PR Details and Diff

For the selected PR, fetch detailed information:

```bash
# Get PR details
gh pr view <pr-id> --web=false

# Get code diff
gh pr diff <pr-id>

# Get both in combined view
gh pr view <pr-id> --web=false && gh pr diff <pr-id>
```

Or use GitHub API (fallback when gh not available):
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/pulls/<pr-id>"
```

### Code Review Analysis

Perform comprehensive review across these areas:

1. **Code Quality**
   - Code style consistency
   - Naming conventions
   - Code complexity
   - Code duplication

2. **Potential Issues**
   - Security vulnerabilities (SQL injection, XSS, etc.)
   - Resource leaks
   - Missing error handling
   - Performance concerns

3. **Business Logic**
   - Feature completeness
   - Edge case handling
   - Consistency with existing code

### Integrating Code Review Skill

Use built-in `code-review` skill for deep analysis:

```
/review
```

This provides:
- Code quality scores
- Potential issue detection
- Specific improvement suggestions
- Best practice recommendations

## Review Templates

This skill supports three template levels for different needs:

### 1. Brief Template (`brief`)

Minimalistic review focusing on key issues only.

**When to use**: Quick reviews, lightweight PRs, or when user specifically requests brief format.

**Structure**:
```markdown
# PR Review Brief - #{pr-id}
{PR Title}

## Critical Issues ({count})
1. [{title}] - {file}:{line} - {brief description}

## Quality Issues ({count})
1. [{title}] - {file}:{line} - {brief description}

## Suggestions ({count})
1. [{title}] - {brief description}

## Overall Rating: {grade} (e.g., B)
## Status: {pending|approved|needs-changes}
```

### 2. Standard Template (`standard`)

Default template with balanced detail level.

**When to use**: Most reviews, provides good readability and actionable feedback.

**Structure**: See [Generate Review Markdown File](#generate-review-markdown-file) section below.

### 3. Detailed Template (`detailed`)

Comprehensive review with extensive context and code snippets.

**When to use**: Complex PRs, security-sensitive changes, or when user requests detailed format.

**Structure**:
- Everything from Standard Template PLUS:
- Expanded code snippets (10-20 lines per issue)
- Additional context/background for each issue
- Related code references
- Step-by-step implementation guide
- Test recommendations
- Documentation updates needed

### Selecting Template

Default: `standard`

Specify template with:
```
"Review #123 with brief template"
"Review PR #456 in detailed mode"
"Generate a brief review for #789"
```

## Quality Scoring System

Each review includes an overall quality grade based on findings.

### Scoring Methodology

**Calculate grade based on**:

1. **Critical Issues** (🔴): -1 to -3 points each
   - High severity: -3 points
   - Medium severity: -2 points
   - Low severity: -1 point

2. **Code Quality Issues** (🟡): -0.5 points each

3. **Suggestions** (🔵): No penalty, informational only

4. **Strengths** (✅): +0.5 to +1 point each

5. **Bonus points**:
   - Excellent documentation: +1
   - Good test coverage: +1
   - Clean architecture: +1

**Base score**: 10 (perfect)

**Grade thresholds**:
- **A+**: 9.0-10.0 (Excellent)
- **A**: 8.5-8.9 (Very Good)
- **B+**: 8.0-8.4 (Good)
- **B**: 7.0-7.9 (Acceptable)
- **C**: 6.0-6.9 (Needs Improvement)
- **D**: < 6.0 (Requires Major Changes)

### Quality Score Display

Include in review report:

```markdown
## Quality Assessment

**Overall Grade**: {grade} ({score}/10.0)

**Score Breakdown**:
- Base Score: 10.0
- Critical Issues: {negative_value}
- Quality Issues: {negative_value}
- Strengths: {positive_value}
- Bonuses: {positive_value}
- **Final Score**: {final_score}

**Issue Distribution**:
- 🔴 Critical: {count}
- 🟡 Quality: {count}
- 🔵 Suggestions: {count}

### Recommendations:
{Based on grade}
```

Examples:
- A+ = No critical issues, well-structured, good tests
- B = Some quality issues, acceptable functionality
- D = Multiple critical issues, requires significant rework

## Review Status Tracking

Each review file includes status tracking in filename.

### Status Types

- **`pending`**: Review created, issues identified, awaiting fixes
- **`in-progress`**: Developer is working on addressing review points
- **`completed`**: All issues addressed, review satisfied

### Filename Convention

```
.issues/review/{pr_number}/r{review_count}-{status}.md
```

**Examples**:
- First review with issues: `.issues/review/123/r01-pending.md`
- Second review, still working on fixes: `.issues/review/123/r02-in-progress.md`
- Third review, all issues addressed: `.issues/review/123/r03-completed.md`

### Status Transitions

```bash
# After review creation (default)
r01-pending.md

# When developer starts addressing issues
mv r01-pending.md r01-in-progress.md

# When all issues resolved
mv r01-in-progress.md r01-completed.md

# Create new review if additional changes needed
r02-pending.md (starts new review cycle)
```

### Status Metadata in File

Include status info in review metadata:

```markdown
## Review Metadata
- **Review Date**: {timestamp}
- **Reviewer**: {AI Assistant}
- **Review Count**: r{review_count}
- **Status**: {pending|in-progress|completed}
- **Grade**: {grade}
- **PR Status**: {open|merged|closed}
```

### Updating Status

When updating review status, preserve all content but update:

```markdown
## Review Metadata
- **Review Date**: {original-date}
- **Last Updated**: {update-date}
- **Status**: {in-progress}  # Updated status
```

Add resolution section when marking as `completed`:

```markdown
## Issue Resolution Status

| Issue # | Type | Status | Resolution Notes |
|---------|------|--------|------------------|
| 1       | Critical | ✅ Fixed | Described how it was fixed |
| 2       | Quality | ✅ Fixed | ... |
| 3       | Suggestion | 🔄 In Progress | ... |
```

## Saving Review Results

**Default Behavior**: Save review to local file unless user explicitly requests PR update.

### File Path Convention

Reviews are saved to:
```
.issues/review/{pr_number}/r{review_count}-{status}.md
```

- `{pr_number}`: GitHub PR number (e.g., 123)
- `{review_count}`: Review count in format `r01`, `r02`, ..., `r21`, etc.
- `{status}`: Review status (default: `pending`)
  - First review of PR #123: `.issues/review/123/r01-pending.md`
  - 21st review of PR #456 with issues addressed: `.issues/review/456/r21-completed.md`

**Auto-detect review count**:
- Check existing review files in `.issues/review/{pr_number}/`
- Increment highest review number found
- Start from `r01` if no previous reviews exist

### Update Review Summary

After saving review, update `.issues/review/summary.md`:

```bash
# Create/update summary file
cat > .issues/review/summary.md << 'EOF'
# PR Review Summary

Last updated: {timestamp}

| PR Number | Title | Status | Last Review | Review Count | Grade |
|-----------|-------|--------|-------------|--------------|-------|
| 123       | {title} | {open/merged/closed} | {date} | r03 | A |
| 456       | {title} | {open/merged/closed} | {date} | r05 | B+ |
| 789       | {title} | {open/merged/closed} | {date} | r01 | C |

## Statistics
- Total PRs Reviewed: {count}
- Open PRs: {count}
- Merged PRs: {count}
- Average Grade: {grade}
- Critical Issues Outstanding: {count}

## Pending Review Actions
| PR | Review Count | Status | Next Action |
|----|--------------|--------|-------------|
| 123 | r03 | in-progress | Verify fix for issue #2 |
| 789 | r01 | pending | Developer needs to address critical issues |
EOF
```

### Generate Review Markdown File

Create structured Markdown report with clear, actionable feedback:

```markdown
# PR Review Report - #{pr-id}
{PR Title}

## Basic Information
- **Author**: {author}
- **Branch**: {source-branch} → {target-branch}
- **Created**: {created-at}
- **Changed Files**: {changed-files}
- **Code Changes**: +{additions} -{deletions}

## Review Summary
{Brief description of main changes}

---

## Quality Assessment

**Overall Grade**: {grade} ({score}/10.0)

**Score Breakdown**:
- Base Score: 10.0
- Critical Issues: {negative_value}
- Quality Issues: {negative_value}
- Strengths: {positive_value}
- Bonuses: {positive_value}
- **Final Score**: {final_score}

**Issue Distribution**:
- 🔴 Critical: {count}
- 🟡 Quality: {count}
- 🔵 Suggestions: {count}

---

## Review Findings

### 🔴 Critical Issues

#### Issue 1: {Issue Title}

**📍 Location**: `{file}:{line}`

**🔍 Original Code**:
```
{Original code snippet, 5-10 lines}
```

**⚠️ Problem**:
{Detailed explanation of the issue and why it's a problem}

**💡 Suggested Change**:
```
{Improved code snippet, 5-10 lines}
```

**📊 Impact**:
- **Risk Level**: High/Medium/Low
- **What it affects**: {Description of affected functionality/behavior}
- **Why change is needed**: {Clear reasoning}

---

### 🟡 Code Quality Issues

#### Issue 1: {Issue Title}

**📍 Location**: `{file}:{line}`

**🔍 Original Code**:
```
{Original code snippet}
```

**✏️ Suggestion**:
```
{Improved code snippet}
```

**📋 Reason**:
{Detailed explanation of why this would improve code quality}

**📊 Impact**:
- **Improves**: {e.g., readability, maintainability, performance}
- **Trade-offs**: {Any potential downsides, if applicable}

---

### 🔵 Suggestions & Best Practices

#### Suggestion 1: {Title}

**📍 Location**: `{file}:{line}` (or "General" for overall suggestions)

**Current Approach**:
```
{Brief description or code of current approach}
```

**Recommended Approach**:
```
{Suggested code or description}
```

**Benefits**:
- {Benefit 1}
- {Benefit 2}

**When to Apply**:
{Context-specific guidance}

---

## Overall Assessment

### ✅ Strengths
- {Strength 1}
- {Strength 2}

### ⚠️ Areas for Improvement
- {Improvement area 1}
- {Improvement area 2}

### 📋 Recommendations
1. {Recommendation 1}
2. {Recommendation 2}

---

## Review Metadata
- **Review Date**: {timestamp}
- **Reviewer**: {AI Assistant}
- **Review Count**: r{review_count}
- **Status**: {pending|in-progress|completed}
- **PR Status**: {current_status}
- **Template**: {brief|standard|detailed}

## Next Steps
1. Address critical issues marked with 🔴
2. Review and implement code quality improvements 🟡
3. Consider suggestions marked with 🔵
4. Request re-review after making changes

## Issue Resolution Status

| Issue # | Type | Status | Resolution Notes |
|---------|------|--------|------------------|
| 1       | Critical | ⏳ Pending | |
| 2       | Quality | ⏳ Pending | |
| 3       | Suggestion | ℹ️ Info only | |
```

**Key formatting rules**:
- Use clear section headers (`##`, `###`)
- Employ emoji badges for visual distinction
- Separate each finding with horizontal rules (`---`)
- Always include: file location, original code, suggestion, and reasoning
- Highlight impact and trade-offs clearly
- Track issue resolution status

### Optional: Add Comments to PR

**Only when explicitly requested by user** with phrases like:
- "Add comments to PR"
- "Post review to GitHub"
- "Update PR with review"

```bash
# Add comment to GitHub PR
gh pr comment <pr-id> --body-file .issues/review/{pr_number}/r{review_count}-{status}.md
```

Or use API:
```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/owner/repo/pulls/<pr-id>/comments" \
  -d "$(cat .issues/review/{pr_number}/r{review_count}-{status}.md)"
```

For inline comments:
```bash
gh pr comment <pr-id> --body "Your comment here" --file-or-editor
```

## Review Summary Management

Maintain `.issues/review/summary.md` for project-wide review tracking.

### Summary Structure

```markdown
# PR Review Summary

Last updated: {date} {time}

## Overview
- Total PRs Reviewed: {count}
- Open PRs: {count}
- Merged PRs: {count}
- Closed PRs: {count}
- In Progress Reviews: {count}
- Average Grade: {grade}

## All Reviews

| PR # | Title | Author | Status | Last Review | Review Count | Grade | Template |
|------|-------|--------|--------|-------------|--------------|-------|----------|
| 123  | Fix login bug | @user | open | 2025-01-15 | r03 | A | standard |
| 456  | Add new feature | @dev | merged | 2025-01-10 | r05 | B+ | detailed |
| 789  | Refactor API | @dev2 | open | 2025-01-20 | r01 | C | brief |

## Statistics by Grade
- A+: {count} PRs
- A: {count} PRs
- B+: {count} PRs
- B: {count} PRs
- C: {count} PRs
- D: {count} PRs

## Outstanding Issues

### High Priority
- PR {number}: {summary} ({review_count}, grade {grade})
  - {count} critical issues
  - Last reviewed: {date}

### Medium Priority
- PR {number}: {summary} ({review_count}, grade {grade})
  - {count} quality issues
  - Last reviewed: {date}

## Pending Review Actions

| PR | Review | Status | Next Action | Priority |
|----|--------|--------|-------------|----------|
| 123 | r03 | in-progress | Verify fixes for issues #1, #2 | High |
| 789 | r01 | pending | Developer to address all critical issues | High |
| 456 | r05 | completed | Ready for merge | Low |

## Recent Activity
- {date}: Created review r01 for PR #{number} (grade: {grade})
- {date}: Updated review r02 for PR #{number} to 'completed'
- {date}: Created review r01 for PR #{number} (template: {template})
```

### Updating Summary

After each review, update summary by:

1. Add or update entry in "All Reviews" table
2. Update statistics sections
3. Remove completed items from "Outstanding Issues"
4. Update "Pending Review Actions"

### Quick Summary Commands

```bash
# Show summary
cat .issues/review/summary.md

# Show outstanding issues only
grep -A 10 "## Outstanding Issues" .issues/review/summary.md

# Show specific PR reviews
ls -la .issues/review/{pr_number}/

# Show all pending reviews
find .issues/review -name "*-pending.md"
```

## Git Workflow Integration

Works with these Git tools:
- `/git-workflow-automation` - Complete Git workflow automation
- `/git-commit` - Create conventional commit messages
- `/git-cleanBranches` - Clean up merged/stale branches

After review completion, can:
1. Use `/git-commit` to create conventional commit messages
2. Update related .issues tracking files
3. Use `/git-workflow-automation` for complete workflow

## Usage Examples

### Review Specific PR

```
"Review #123 PR code changes"
"Help me review PR #456 for potential issues"
```

### Review with Custom Template

```
"Review #123 with brief template"
"Review PR #456 in detailed mode"
"Generate standard review for #789"
```

### List and Select PR to Review

```
"List all pending PRs"
"Review all open PRs in repository"
```

### Review Multiple PRs

```
"Review #123 and #456"
"Batch review the first 5 pending PRs"
```

### Generate Report File

```
"Review #123 and save to file"
"Review PR #456 and create Markdown report"
```

### Post Comment to PR (Explicit Request)

```
"Review #123 and add comments to PR"
"Post review of PR #456 to GitHub"
```

### Check Review Summary

```
"Show review summary"
"List outstanding review issues"
"What PRs need attention?"
```

### Update Review Status

```
"Mark review r01 for PR #123 as completed"
"Update PR #456 review to in-progress status"
```

## Configuration Requirements

Before using this skill, configure:

1. **GitHub Access Token** (environment variable or config file)
   ```bash
   export GITHUB_TOKEN=your_personal_access_token
   ```

2. **Repository ID** (for API calls)
   Either use auto-detection from git remote or set:
   ```bash
   export GITHUB_REPOSITORY=owner/repo
   ```

## Important Notes

- Ensure proper access permissions before review
- **Default behavior creates local files**, not direct PR updates
- Confirm before sensitive operations (like posting comments)
- Large PR diffs may be detailed, watch for context window limits
- Security-related code changes require extra careful review
- Review files are versioned in `.issues/review/` for history tracking
- Use appropriate template level based on PR complexity
- Review summary is automatically updated after each review

## Best Practices

1. **Always save review first**: Default to local `.issues/review/` files
2. **Clear location info**: Always specify file:line for each issue
3. **Actionable feedback**: Provide concrete code examples and clear reasoning
4. **Impact awareness**: Explain potential risks and benefits of changes
5. **Structured format**: Use consistent markdown structure for easy scanning
6. **Review history**: Track all reviews for the same PR in sequence (r01, r02, ...)
7. **User confirmation**: Ask before posting to PR unless explicitly requested
8. **Template selection**: Choose appropriate template based on PR complexity and needs
9. **Status tracking**: Update review status as issues are addressed
10. **Summary maintenance**: Keep `.issues/review/summary.md` up to date for project visibility
11. **Quality grading**: Apply consistent grading methodology across all reviews
12. **Issue resolution tracking**: Mark issues as resolved when addressed

## Using Scripts

The skill includes scripts for GitHub API interaction:

### List PRs
```bash
./scripts/github-pr-list.sh [state]
# state: open (default), closed, merged, all
```

### Get PR Details
```bash
./scripts/github-pr-detail.sh <pr-id>
```

Environment variables required:
- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_REPOSITORY`: Repository in format `owner/repo` (auto-detected if in git repo)