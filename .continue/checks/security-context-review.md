---
name: Security-in-Context Review
description: Review security aspects in context of changes
---

# Security-in-Context Review

## Context

This check reviews security aspects when relevant changes are made.

This is NOT a general security check - it triggers only on specific change types to avoid duplicating deterministic tools (secret scanning, SAST).

## What to Check

### 1. New Endpoints - Authorization Enforcement

When new endpoints are added, verify authorization is considered.

**Trigger**: New `@app.post()` or `@app.get()` decorators

**BAD**:

```python
@app.post('/admin/reset')
async def admin_reset(request: Request):
    # No auth check
    return {'status': 'ok'}
```

**GOOD**:

```python
@app.post('/admin/reset')
async def admin_reset(request: Request):
    # Verify admin authorization
    if not is_admin(request):
        raise HTTPException(status_code=403)
    ...
```

### 2. Sensitive Data Logging

Verify sensitive data is not logged.

**Trigger**: Changes involving logging or response generation

**BAD**:

```python
logger.info(f"API Key: {api_key}")  # Leaks secret
print(f"User token: {token}")  # Leaks secret
```

**GOOD**:

```python
logger.info(f"API request received")  # No sensitive data
```

### 3. Input Validation

Verify new endpoints have proper input validation.

**Trigger**: New endpoint parameters or request body handling

**BAD**:

```python
@app.post('/process')
async def process(data: dict):
    result = dangerous_operation(data['unsafe_field'])  # No validation
```

**GOOD**:

```python
@app.post('/process')
async def process(data: dict):
    if 'unsafe_field' not in data:
        raise HTTPException(status_code=400)
    validated = validate_input(data['unsafe_field'])
    ...
```

### 4. SSRF Risk Assessment

When adding new outbound call targets, assess SSRF risk.

**Trigger**: New `httpx.AsyncClient` calls to user-controlled URLs

**BAD**:

```python
url = request.query_params['url']
response = await client.get(url)  # SSRF vulnerability
```

**GOOD**:

```python
url = request.query_params['url']
if not is_internal_url(url):  # Validate not internal
    raise HTTPException(status_code=400)
response = await client.get(url)
```

### 5. Environment Variable Security

When new environment variables are added, verify they're not sensitive.

**Trigger**: New `os.getenv()` calls

**BAD**:

```python
SECRET_KEY = os.getenv('SECRET_KEY')  # Hardcoded in code review
API_KEY = os.getenv('MY_API_KEY')  # Should be secrets manager
```

**GOOD**:

- Non-sensitive config: environment variable (OK)
- Sensitive secrets: use secrets manager or vault

## Key Files to Check

- `proxy.py` - endpoint definitions
- Any new files

## Exclusions

- Secret detection (handled by deterministic tools like git-secrets, gitleaks)
- Test files with mock data
- Health check endpoints

## Important Notes

- This check is TRIGGER-BASED - only runs when relevant changes are made
- Do NOT duplicate deterministic security scanning
- Focus on architectural security decisions that require judgment
