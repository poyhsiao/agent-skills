# Conventional Commits Specification

This reference provides a quick guide to the Conventional Commits specification.

## Format

```
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 support` |
| `fix` | Bug fix | `fix(api): resolve null pointer in user endpoint` |
| `docs` | Documentation changes | `docs: update API usage examples` |
| `style` | Code style changes (formatting, missing semicolons, etc.) | `style: format code with prettier` |
| `refactor` | Code refactoring | `refactor(database): simplify query builder` |
| `perf` | Performance improvements | `perf: optimize image loading` |
| `test` | Adding or updating tests | `test: add unit tests for parser` |
| `build` | Changes to build system or dependencies | `build: upgrade webpack to v5` |
| `ci` | CI/CD configuration changes | `ci: add automated testing workflow` |
| `chore` | Other changes that don't modify src or test files | `chore: update dependencies` |
| `revert` | Reverts a previous commit | `revert: revert "feat: add feature X"` |

## Scope

Optional. Provides additional contextual information about what part of the codebase is affected.

Examples:
- `feat(api): add new endpoint`
- `fix(ui/button): correct hover state`
- `docs(readme): update installation steps`

## Breaking Changes

Indicate breaking changes by:
1. Adding `!` after type/scope: `feat!: remove deprecated API`
2. Adding `BREAKING CHANGE:` footer:

```
feat(api): redesign authentication flow

BREAKING CHANGE: The auth endpoint now requires JWT tokens instead of session cookies.
```

## Examples

### Simple feature
```
feat: add user profile page
```

### Bug fix with scope
```
fix(auth): prevent token expiration on page reload
```

### Breaking change
```
feat(api)!: redesign REST API structure

BREAKING CHANGE: All endpoints now use /api/v2 prefix. V1 endpoints are deprecated.
```

### Multi-line with body
```
refactor(database): optimize query performance

Refactored the query builder to use prepared statements
and connection pooling, reducing average query time by 40%.
```

## References

- Official spec: https://www.conventionalcommits.org/
- Angular convention: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit
