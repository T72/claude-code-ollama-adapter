---
name: ADR & Boundary Trigger Guard
description: Ensure architectural changes have proper ADR documentation
---

# ADR & Boundary Trigger Guard

## Context

This check enforces ADR requirements defined in the Engineering Governance Playbook v2.1, Sections 6 and 7.

Reference: `docs/engineering_playbook.md` - "If a change affects core boundaries, public API contracts, agent lifecycle behavior, tool governance rules, provider abstraction, routing behavior → Create an ADR."

## What to Check

### 1. Core Boundary Changes

When modifying core vs plugin boundaries, verify ADR exists.

**Trigger files**:

- Any changes to `proxy.py` core logic
- New endpoint definitions
- Middleware modifications

**BAD**:

- Core logic changed without ADR
- Plugin boundaries modified without review

**GOOD**:

- ADR created in `docs/developer/adr/`
- ADR follows naming convention: `adr-xxx-short-title.md`

### 2. Provider Abstraction Changes

When modifying provider abstraction, verify ADR exists.

**Trigger**:

- Changes to `_openai_to_ollama()` or `_anthropic_to_ollama()`
- New provider support added
- Translation logic modifications

**BAD**:

- Provider abstraction modified without ADR
- Translation changes without documentation

**GOOD**:

- ADR documents the change rationale
- Backward compatibility considered

### 3. Routing Behavior Changes

When modifying routing logic, verify ADR exists.

**Trigger**:

- Changes to endpoint routing
- New route handlers
- URL pattern changes

### 4. Public API Contract Changes

When modifying public API contracts, verify ADR exists.

**Trigger**:

- Changes to response format
- New fields in responses
- Breaking changes to existing endpoints

**BAD**:

- Response format changed without ADR
- Breaking changes without documentation

**GOOD**:

- ADR explains the change
- Migration path documented

### 5. Middleware Order Changes

When modifying middleware order, verify documentation exists.

## Key Files to Check

- `proxy.py` - core logic
- `docs/developer/adr/` - ADR directory
- Any new endpoint definitions

## Exclusions

- Bug fixes that don't change architecture
- Test-only changes
- Documentation updates

## Playbook Reference

Section 6: "If a change affects: Core boundaries, Public API contracts, Agent lifecycle behavior, Tool governance rules, Provider abstraction, Routing behavior → Create an ADR."

Section 7: ADR location and naming conventions.
