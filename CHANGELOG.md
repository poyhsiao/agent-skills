# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `github-pr-review` - GitHub Pull Request (PR) review tool with AI-powered code analysis
  - PR list and detail retrieval via GitHub CLI and API
  - Comprehensive code quality review with severity-based scoring
  - Multiple review templates (brief, standard, detailed)
  - Quality grading system (A+ to D)
  - Review status tracking (pending → in-progress → completed)
  - Automatic review summary management
  - Issue resolution tracking
  - Support for batch PR reviews
  - Scripts for GitHub API interaction:
    - `github-pr-list.sh` - List PRs with filtering options
    - `github-pr-detail.sh` - Get detailed PR information

- `gitlab-mr-review` - GitLab Merge Request (MR) review tool with AI-powered code analysis
  - MR list and detail retrieval via GitLab CLI and API
  - Comprehensive code quality review with severity-based scoring
  - Multiple review templates (brief, standard, detailed)
  - Quality grading system (A+ to D)
  - Review status tracking (pending → in-progress → completed)
  - Automatic review summary management
  - Issue resolution tracking
  - Support for batch MR reviews
  - Scripts for GitLab API interaction:
    - `gitlab-mr-list.sh` - List MRs with filtering options
    - `gitlab-mr-detail.sh` - Get detailed MR information

### Changed

- Updated README.md to include new skills documentation

### Features

#### Code Review Analysis
- Code Quality evaluation (style, naming, complexity, duplication)
- Potential Issues detection (security, resource leaks error handling, performance)
- Business Logic review (completeness, edge cases, consistency)

#### Review Templates
1. **Brief Template** - Minimalistic review focusing on key issues
2. **Standard Template** - Balanced detail level (default)
3. **Detailed Template** - Comprehensive review with extended context

#### Quality Scoring System
- Base score: 10.0 (perfect)
- Critical Issues (🔴): -1 to -3 points each based on severity
- Code Quality Issues (🟡): -0.5 points each
- Strengths (✅): +0.5 to +1 point each
- Bonus points: documentation, test coverage, architecture
- Grade thresholds: A+ (9.0-10.0), A (8.5-8.9), B+ (8.0-8.4), B (7.0-7.9), C (6.0-6.9), D (<6.0)

#### Review Status Tracking
- `pending` - Review created, issues identified, awaiting fixes
- `in-progress` - Developer working on addressing review points
- `completed` - All issues addressed, review satisfied
- Filename convention: `.issues/review/{mr_number}/r{review_count}-{status}.md`
- Auto-detect review count and increment

#### Review Summary Management
- `.issues/review/summary.md` for project-wide tracking
- Statistics: total reviews, open/merged/closed, average grade
- Outstanding issues by priority
- Pending review actions table
- Recent activity log

## [0.1.0] - 2025-02-07

### Added

- `git-workflow-automation` - Complete Git workflow automation skill
  - Auto-generate Conventional Commits messages
  - Extract and reference GitHub Issues
  - Generate PR descriptions with issue associations
  - Auto-create PRs and update Issue comments
  - Scripts:
    - `generate_commit_message.py` - Generate conventional commits
    - `extract_issue_numbers.py` - Extract issue IDs from commits
    - `generate_pr_description.py` - Generate PR descriptions

- Initial project structure
- Apache License 2.0
- Basic documentation in README.md