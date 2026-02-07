# GitHub Issue Keywords

This reference lists keywords that GitHub recognizes for automatically linking and closing issues.

## Closing Keywords

These keywords, when used in commit messages or PR descriptions, will automatically close the referenced issue when the commit/PR is merged to the default branch.

### Supported Keywords

- `close`
- `closes`
- `closed`
- `fix`
- `fixes`
- `fixed`
- `resolve`
- `resolves`
- `resolved`

### Usage Patterns

**Single issue:**
```
fixes #123
```

**Multiple issues:**
```
closes #123, closes #456
fixes #789 and resolves #101
```

**In commit message:**
```
fix(auth): prevent session timeout

This commit fixes #42 by implementing keep-alive tokens.
```

**In PR description:**
```
## Summary
Add new authentication flow

Closes #123
Fixes #456
```

## Reference Keywords

To reference an issue without closing it, simply use the issue number with `#`:

```
See #123 for more context
Related to #456
Part of #789
```

## Issue Linking in Different Repositories

To reference issues in different repositories:

```
fixes owner/repo#123
resolves organization/project#456
```

## Best Practices

1. **Be explicit**: Use closing keywords at the beginning of lines in PR descriptions
2. **One per line**: For clarity, list each issue on a separate line
3. **Commit vs PR**: Issues are closed when the PR is merged, not when commits are pushed
4. **Multiple fixes**: If fixing multiple issues, list each with its own keyword

## Examples

### Commit message
```
feat(api): add rate limiting

Implements rate limiting middleware to prevent abuse.

Fixes #234
```

### PR description
```
## Summary
Redesign user dashboard with improved performance

## Changes
- Optimize data fetching
- Add caching layer
- Improve UI responsiveness

## Related Issues
Closes #123
Closes #456
References #789
```

## References

- GitHub docs: https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue
