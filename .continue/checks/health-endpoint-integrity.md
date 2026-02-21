---
name: Health Endpoint Integrity
description: Ensure health checks verify actual upstream connectivity
---

# Health Endpoint Integrity

## Context

This check ensures health endpoints provide meaningful status information.

Reference: Current health endpoint in `proxy.py` returns static 'ok' without verifying Ollama connectivity.

## What to Check

### 1. Upstream Connectivity Verification

Verify health checks actually test upstream dependencies.

**Current implementation (needs improvement)**:

```python
@app.get('/health')
async def health():
    return {'status': 'ok', 'ollama_base': OLLAMA_BASE_URL}
```

**BAD**:

- Returns 'ok' even when Ollama is down
- No actual connectivity check

**GOOD**:

```python
@app.get('/health')
async def health():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(OLLAMA_BASE_URL + '/api/tags')
            ollama_ok = resp.status_code == 200
    except:
        ollama_ok = False

    return {
        'status': 'ok' if ollama_ok else 'degraded',
        'ollama_base': OLLAMA_BASE_URL,
        'ollama_connected': ollama_ok
    }
```

### 2. Liveness vs Readiness Separation

If applicable, separate liveness and readiness checks.

**Liveness**: Is the process running?

**Readiness**: Is the service able to handle requests?

**GOOD**:

```python
@app.get('/health/live')
async def liveness():
    return {'status': 'ok'}

@app.get('/health/ready')
async def readiness():
    # Check Ollama connectivity
    ...
```

### 3. Meaningful Status Codes

Use appropriate HTTP status codes.

**BAD**:

```python
return {'status': 'error'}  # Returns 200 OK
```

**GOOD**:

```python
if not ollama_ok:
    return JSONResponse({'status': 'error'}, status_code=503)
```

## Key Files to Check

- `proxy.py` - health endpoint

## Exclusions

- Development-only endpoints
- Basic liveness probes

## Recommendation

The current health endpoint should be enhanced to actually verify Ollama connectivity.
