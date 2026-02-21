---
name: PR Scope & Governance Compliance
description: Enforce PR governance rules and scope coherence
---

# PR Scope & Governance Compliance

## Context

This check enforces PR governance rules defined in the Engineering Governance Playbook v2.1, Sections 2 and 5.

Reference: `docs/engineering_playbook.md` - "No non-trivial change without a GitHub issue" and PR title format requirements.

## What to Check

### 1. Issue Reference

Verify that the PR references exactly one primary issue.

**BAD** (No issue referenced):

```markdown
Closes #
```

**GOOD** (Valid issue reference):

```markdown
Closes #123
```

### 2. PR Title Format

Verify PR title follows the format: `<type>: concise description`

**BAD**:

- "Fixed the thing"
- "Changes"
- "Update proxy.py"

**GOOD**:

- fix: correct healthcheck endpoint
- feat: add streaming support for tool calls
- refactor: extract shared API key verification
- docs: update README with new env vars

### 3. Scope Coherence

Verify the PR contains only changes related to the primary issue.

**BAD**:

- Primary issue is about health check, but includes unrelated formatting changes
- Fix includes new features not discussed in issue
- Multiple unrelated concerns in one PR

**GOOD**:

- Changes are focused on the single issue
- No opportunistic scope expansion

## Key Files to Check

- `.github/pull-request-template.md`
- PR title and body in the pull request

## Exclusions

- Hotfix branches (may have different conventions)
- Automated dependency updates (dependabot)
