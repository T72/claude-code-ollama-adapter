---
name: Configuration Drift Prevention
description: Ensure environment variables and configuration are properly documented
---

# Configuration Drift Prevention

## Context

This check enforces documentation requirements defined in the Engineering Governance Playbook v2.1, Section 8 - "Documentation as part of Definition of Done."

Reference: Current environment variables documented in README.md Configuration table.

## What to Check

### 1. Environment Variable Documentation

When new `os.getenv()` is added, verify documentation is updated.

**Trigger**: New environment variable usage in code

**Current documented env vars**:

- `OLLAMA_BASE_URL` - Ollama server URL (default: `http://localhost:11434`)
- `THINK_MODELS` - Comma-separated model names for think mode

**BAD**:

```python
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')  # Not documented
```

**GOOD**:

- README.md Configuration table updated
- Default value documented

### 2. Correct Documentation Audience

Verify documentation goes to the correct folder.

Reference: `docs/engineering_playbook.md` Section 8.1

| Folder | Audience | Content Type |
| --- | --- | --- |
| `docs/user/` | Consumer-facing | API usage, quick start |
| `docs/developer/` | Internal engineering | ADRs, architecture |
| `docs/operations/` | Deployment and runtime | Deployment, monitoring |

**BAD**:

- Deployment instructions in `docs/user/`
- Internal design notes in `docs/user/`

**GOOD**:

- Configuration in correct audience folder
- No cross-audience mixing

### 3. Default Value Clarity

Verify all new environment variables have clear defaults.

**BAD**:

```python
API_KEY = os.getenv('API_KEY')  # No default, no documentation
```

**GOOD**:

```python
# Default: not set (required)
API_KEY = os.getenv('API_KEY', 'default-key')
```

### 4. Naming Consistency

Verify naming follows existing conventions.

**Current pattern**:

- `OLLAMA_BASE_URL`
- `THINK_MODELS`

**BAD**:

```python
ollamaUrl = os.getenv('OLLAMA_URL')  # Inconsistent naming
```

**GOOD**:

```python
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')  # Consistent
```

## Key Files to Check

- `proxy.py` - environment variable usage
- `README.md` - Configuration table
- `docs/` - Documentation folders

## Exclusions

- Temporary development variables
- Test-only configuration

## Playbook Reference

Section 8: "Documentation as part of Definition of Done"
Section 8.4: "Changes that modify... Deployment process... must update documentation before merge."
