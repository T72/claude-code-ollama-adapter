---
name: Behavior Change → Test Enforcement
description: Ensure behavioral changes have proper test coverage
---

# Behavior Change → Test Enforcement

## Context

This check enforces TDD requirements defined in the Engineering Governance Playbook v2.1, Section 3.

Reference: `docs/engineering_playbook.md` - "Lightweight TDD is mandatory" and Section 3.2 Minimum TDD Requirements.

## What to Check

### 1. Behavioral Changes Require Tests

When code changes modify behavior, verify tests are present.

**BAD**:

- New feature added without tests
- Logic changed without updating corresponding tests

**GOOD**:

- New feature has unit or contract tests
- Behavior modification includes test updates

### 2. Bug Fixes Require Regression Tests

When fixing bugs, verify regression tests exist.

**BAD**:

- Bug fixed without adding a test that would have caught it
- Edge case handled but not tested

**GOOD**:

- Bug fix includes a regression test
- Edge case has test coverage

### 3. No Skipped Tests

Verify no new skipped tests are introduced.

**BAD**:

```python
@pytest.mark.skip("Reason")
def test_something():
    ...
```

**GOOD**:

- All tests run and pass
- No @skip decorators added

### 4. Refactors Preserve Behavior

When refactoring, ensure tests protect behavior.

**BAD**:

- Large refactor without test coverage
- Tests removed during refactor

**GOOD**:

- Tests exist before refactor
- Refactor is covered by existing tests

## Key Files to Check

- `tests/test_proxy.py`
- Any new test files added

## Exclusions

- Documentation-only changes
- CI/CD configuration changes
- Dependency updates

## Playbook Reference

Section 3.2: "A task is not complete unless:

- New behavior is covered by unit or contract tests.
- Bug fixes include a regression test.
- Refactors do not reduce meaningful coverage.
- No new skipped tests introduced.
- CI passes."
