---
name: Documentation Governance & Integrity Enforcement
description: Ensure documentation updates, audience separation, and ADR creation when required by governance rules
---

# Documentation Governance & Integrity Enforcement

## Context

This check enforces documentation as a governance artifact per the Engineering Governance Playbook v2.1.

Reference: Sections 6, 7, 8, and 9 - ADRs, Documentation Placement, and Definition of Done.

## What to Check

### 1. Definition-of-Done Documentation Compliance

When code changes affect API behavior, architecture, deployment, or governance rules, verify documentation is updated.

**Trigger**: Changes to `proxy.py`, deployment configs, or governance files

**BAD**:

- API behavior changed but no documentation update
- Architecture modified without docs update
- Governance rules changed without updating `docs/engineering_playbook.md`

**GOOD**:

- `docs/user/` updated for API changes
- `docs/developer/` updated for architecture changes
- `docs/operations/` updated for deployment changes
- `docs/engineering_playbook.md` updated for governance changes

**Playbook**: Section 8.4 - "Documentation is part of Definition of Done"

### 2. Audience Separation Enforcement

Verify documentation is placed in the correct audience folder.

**Correct placement**:

| Folder | Audience | Content Type |
| --- | --- | --- |
| `docs/user/` | Consumers | API usage, quick start, features |
| `docs/developer/` | Engineers | ADRs, architecture, development guides |
| `docs/operations/` | Ops | Deployment, runtime, monitoring |

**BAD**:

- Internal design notes in `docs/user/`
- Deployment instructions in `docs/user/`
- Architecture docs mixed with user docs

**GOOD**:

- Architecture in `docs/developer/architecture/`
- Deployment in `docs/operations/`
- User guides in `docs/user/`

**Playbook**: Section 8.1 - Audience Separation

### 3. ADR Trigger Enforcement

When architectural triggers occur, verify ADR exists.

**Trigger changes**:

- Core boundaries modified
- Public API contracts changed
- Provider abstraction modified
- Routing behavior changed
- Middleware order altered
- Agent lifecycle behavior changed
- Tool governance rules modified

**BAD**:

- Core logic changed without ADR
- Translation logic modified without ADR
- Breaking API change without ADR

**GOOD**:

- ADR created in `docs/developer/adr/`
- ADR follows naming: `adr-xxx-short-title.md`
- ADR documents rationale and impact

**Playbook**: Sections 6 and 7

### 4. Configuration Drift Prevention

When new environment variables are introduced, verify documentation.

**Trigger**: New `os.getenv()` in `proxy.py`

**BAD**:

- New env var without README.md update
- New config without `.env.example` update (if present)
- Default value not documented

**GOOD**:

- README.md Configuration table updated
- Default value clearly documented
- Correct audience folder used

**Playbook**: Section 8.4

## Key Files to Check

- `proxy.py` - environment variable usage
- `README.md` - Configuration table
- `docs/engineering_playbook.md` - governance rules
- `docs/developer/adr/` - ADR directory
- `docs/user/` - consumer docs
- `docs/developer/` - engineering docs
- `docs/operations/` - deployment docs

## Exclusions

- Documentation-only PRs (triggers but validates internal consistency)
- Test documentation
- Inline code comments
- Spell-checking (deterministic)
- Grammar/style (deterministic)

## Explicit Constraints

This check must:

- Be trigger-based only
- Not critique writing style
- Not duplicate linter/formatter checks
- Reference explicit playbook sections
- Focus on governance, not prose quality
