---
name: HTTP Client & Error Handling Discipline
description: Ensure proper HTTP client configuration and error handling
---

# HTTP Client & Error Handling Discipline

## Context

This check enforces error handling discipline as defined in the Engineering Governance Playbook v2.1, Section 6 - "No silent breaking changes."

Reference: `proxy.py` uses `httpx.AsyncClient` for all outbound calls.

## What to Check

### 1. HTTP Client Timeout Configuration

Verify explicit timeout configuration.

**Trigger**: New `httpx.AsyncClient` usage

**BAD**:

```python
async with httpx.AsyncClient() as client:  # No timeout
```

**GOOD**:

```python
async with httpx.AsyncClient(timeout=120) as client:
```

### 2. Exception Handling Completeness

Verify comprehensive exception handling.

**Current handling in proxy.py**:

```python
except httpx.ReadTimeout:
    yield 'data: [DONE]' + _SSE_SEP
```

**BAD** (incomplete):

```python
try:
    response = await client.post(url, json=data)
except httpx.ReadTimeout:
    handle_timeout()
```

**GOOD** (comprehensive):

```python
try:
    response = await client.post(url, json=data)
except httpx.ReadTimeout:
    handle_timeout()
except httpx.ConnectError:
    handle_connection_error()
except httpx.HTTPStatusError:
    handle_status_error()
except json.JSONDecodeError:
    handle_parse_error()
```

### 3. Error Response Mapping

Verify consistent error response mapping.

**BAD**:

```python
if resp.status_code != 200:
    return Response(content=resp.text, status_code=500)  # Loses original error
```

**GOOD**:

```python
if resp.status_code != 200:
    return Response(content=resp.text, status_code=resp.status_code)  # Preserve original
```

### 4. No Silent Fallbacks

Verify no silent error swallowing.

**BAD**:

```python
try:
    response = await client.post(url, json=data)
except Exception:
    pass  # Silent failure
```

**GOOD**:

```python
try:
    response = await client.post(url, json=data)
except Exception as e:
    logger.error(f"Request failed: {e}")
    raise
```

## Key Files to Check

- `proxy.py` - all httpx usage

## Exclusions

- Health check endpoint (may have different requirements)
- Test files

## Playbook Reference

Section 6: "No silent breaking changes."
