---
name: gitlab-mr-review
description: GitLab Merge Request (MR) review tool. Use this for: (1) Reviewing specific MRs (e.g., "Review !123" or "Review MR !123"), (2) Listing and reviewing all pending MRs, (3) Analyzing code changes and providing improvement suggestions, (4) Adding review comments to MR or generating Markdown reports. Default behavior saves reviews to `.issues/review/{mr_number}/{review_count}-{status}.md` unless explicitly requested to update MR directly.
---

# GitLab MR Review

## Workflow Decision Tree

Start → Is MR specified?
- Yes: Continue reviewing that MR
- No: List all pending MRs and let user choose

## Prerequisites

### Install `glab` CLI

This skill prioritizes using `glab` (GitLab CLI). If not installed, guide user to install:

```bash
# macOS
brew install glab

# Linux
curl -s https://raw.githubusercontent.com/cli/cli/main/scripts/install.sh | sh

# Or visit https://gitlab.com/gitlab-org/cli#installation
```

Verify installation:
```bash
glab --version
```

### GitLab Authentication

Configure `glab` with GitLab authentication:
```bash
glab auth login
```

Or set environment variable:
```bash
export GITLAB_TOKEN=your_personal_access_token
```

For custom GitLab instances:
```bash
export GITLAB_URL=https://gitlab.example.com
```

## Reviewing MRs

### Get MR List

When no specific MR is specified, list all pending MRs:

```bash
# List all open MRs in current project
glab mr list --state opened

# List MRs by author
glab mr list --author <username>

# List MRs targeted to specific branch
glab mr list --target <branch-name>
```

MR list should include:
- MR number and title
- Author
- Target branch
- Creation date
- Status (open, merged, closed)

### Get MR Details and Diff

For the selected MR, fetch detailed information:

```bash
# Get MR details
glab mr view <mr-id> --web=false

# Get code diff
glab mr diff <mr-id>

# Get both in combined view
glab mr view <mr-id> --web=false && glab mr diff <mr-id>
```

Or use GitLab API (fallback when glab not available):
```bash
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects/<project-id>/merge_requests/<mr-id>"
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
# MR Review Brief - !{mr-id}
{MR Title}

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
"Review !123 with brief template"
"Review MR !456 in detailed mode"
"Generate a brief review for !789"
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
.issues/review/{mr_number}/r{review_count}-{status}.md
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
- **MR Status**: {open|merged|closed}
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

**Default Behavior**: Save review to local file unless user explicitly requests MR update.

### File Path Convention

Reviews are saved to:
```
.issues/review/{mr_number}/r{review_count}-{status}.md
```

- `{mr_number}`: GitLab MR number (e.g., 123)
- `{review_count}`: Review count in format `r01`, `r02`, ..., `r21`, etc.
- `{status}`: Review status (default: `pending`)
  - First review of MR #123: `.issues/review/123/r01-pending.md`
  - 21st review of MR #456 with issues addressed: `.issues/review/456/r21-completed.md`

**Auto-detect review count**:
- Check existing review files in `.issues/review/{mr_number}/`
- Increment highest review number found
- Start from `r01` if no previous reviews exist

### Update Review Summary

After saving review, update `.issues/review/summary.md`:

```bash
# Create/update summary file
cat > .issues/review/summary.md << 'EOF'
# MR Review Summary

Last updated: {timestamp}

| MR Number | Title | Status | Last Review | Review Count | Grade |
|-----------|-------|--------|-------------|--------------|-------|
| 123       | {title} | {open/merged/closed} | {date} | r03 | A |
| 456       | {title} | {open/merged/closed} | {date} | r05 | B+ |
| 789       | {title} | {open/merged/closed} | {date} | r01 | C |

## Statistics
- Total MRs Reviewed: {count}
- Open MRs: {count}
- Merged MRs: {count}
- Average Grade: {grade}
- Critical Issues Outstanding: {count}

## Pending Review Actions
| MR | Review Count | Status | Next Action |
|----|--------------|--------|-------------|
| 123 | r03 | in-progress | Verify fix for issue #2 |
| 789 | r01 | pending | Developer needs to address critical issues |
EOF
```

### Generate Review Markdown File

Create structured Markdown report with clear, actionable feedback:

```markdown
# MR Review Report - !{mr-id}
{MR Title}

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
- **MR Status**: {current_status}
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

### Optional: Add Comments to MR

**Only when explicitly requested by user** with phrases like:
- "Add comments to MR"
- "Post review to GitLab"
- "Update MR with review"

```bash
# Add comment to GitLab MR
glab mr note <mr-id> --message "$(cat .issues/review/{mr_number}/r{review_count}-{status}.md)"
```

Or use API:
```bash
curl --request POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --data "body=$(cat .issues/review/{mr_number}/r{review_count}-{status}.md)" \
  "https://gitlab.example.com/api/v4/projects/<project-id>/merge_requests/<mr-id>/notes"
```

## Review Summary Management

Maintain `.issues/review/summary.md` for project-wide review tracking.

### Summary Structure

```markdown
# MR Review Summary

Last updated: {date} {time}

## Overview
- Total MRs Reviewed: {count}
- Open MRs: {count}
- Merged MRs: {count}
- Closed MRs: {count}
- In Progress Reviews: {count}
- Average Grade: {grade}

## All Reviews

| MR # | Title | Author | Status | Last Review | Review Count | Grade | Template |
|------|-------|--------|--------|-------------|--------------|-------|----------|
| 123  | Fix login bug | @user | open | 2025-01-15 | r03 | A | standard |
| 456  | Add new feature | @dev | merged | 2025-01-10 | r05 | B+ | detailed |
| 789  | Refactor API | @dev2 | open | 2025-01-20 | r01 | C | brief |

## Statistics by Grade
- A+: {count} MRs
- A: {count} MRs
- B+: {count} MRs
- B: {count} MRs
- C: {count} MRs
- D: {count} MRs

## Outstanding Issues

### High Priority
- MR {number}: {summary} ({review_count}, grade {grade})
  - {count} critical issues
  - Last reviewed: {date}

### Medium Priority
- MR {number}: {summary} ({review_count}, grade {grade})
  - {count} quality issues
  - Last reviewed: {date}

## Pending Review Actions

| MR | Review | Status | Next Action | Priority |
|----|--------|--------|-------------|----------|
| 123 | r03 | in-progress | Verify fixes for issues #1, #2 | High |
| 789 | r01 | pending | Developer to address all critical issues | High |
| 456 | r05 | completed | Ready for merge | Low |

## Recent Activity
- {date}: Created review r01 for MR #{number} (grade: {grade})
- {date}: Updated review r02 for MR #{number} to 'completed'
- {date}: Created review r01 for MR #{number} (template: {template})
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

# Show specific MR reviews
ls -la .issues/review/{mr_number}/

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

### Review Specific MR

```
"Review !123 MR code changes"
"Help me review MR !456 for potential issues"
```

### Review with Custom Template

```
"Review !123 with brief template"
"Review MR !456 in detailed mode"
"Generate standard review for !789"
```

### List and Select MR to Review

```
"List all pending MRs"
"Review all open MRs in project A"
```

### Review Multiple MRs

```
"Review !123 and !456"
"Batch review the first 5 pending MRs"
```

### Generate Report File

```
"Review !123 and save to file"
"Review MR !456 and create Markdown report"
```

### Post Comment to MR (Explicit Request)

```
"Review !123 and add comments to MR"
"Post review of MR !456 to GitLab"
```

### Check Review Summary

```
"Show review summary"
"List outstanding review issues"
"What MRs need attention?"
```

### Update Review Status

```
"Mark review r01 for MR !123 as completed"
"Update MR !456 review to in-progress status"
```

## Configuration Requirements

Before using this skill, configure:

1. **GitLab Access Token** (environment variable or config file)
   ```bash
   export GITLAB_TOKEN=your_personal_access_token
   ```

2. **GitLab API Endpoint** (for custom domains)
   ```bash
   export GITLAB_URL=https://gitlab.example.com
   ```

3. **Project ID** (for API calls)
   Get from GitLab project page or use `glab api projects`

## Important Notes

- Ensure proper access permissions before review
- **Default behavior creates local files**, not direct MR updates
- Confirm before sensitive operations (like posting comments)
- Large MR diffs may be detailed, watch for context window limits
- Security-related code changes require extra careful review
- Review files are versioned in `.issues/review/` for history tracking
- Use appropriate template level based on MR complexity
- Review summary is automatically updated after each review

## Best Practices

1. **Always save review first**: Default to local `.issues/review/` files
2. **Clear location info**: Always specify file:line for each issue
3. **Actionable feedback**: Provide concrete code examples and clear reasoning
4. **Impact awareness**: Explain potential risks and benefits of changes
5. **Structured format**: Use consistent markdown structure for easy scanning
6. **Review history**: Track all reviews for the same MR in sequence (r01, r02, ...)
7. **User confirmation**: Ask before posting to MR unless explicitly requested
8. **Template selection**: Choose appropriate template based on MR complexity and needs
9. **Status tracking**: Update review status as issues are addressed
10. **Summary maintenance**: Keep `.issues/review/summary.md` up to date for project visibility
11. **Quality grading**: Apply consistent grading methodology across all reviews
12. **Issue resolution tracking**: Mark issues as resolved when addressed