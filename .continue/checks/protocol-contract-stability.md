---
name: Protocol Contract Stability
description: Ensure SSE streaming and API translation contracts remain stable
---

# Protocol Contract Stability

## Context

This check enforces protocol stability as defined in the Engineering Governance Playbook v2.1, Section 6 - "No silent breaking changes."

Reference: `proxy.py` contains SSE streaming logic and translation functions that clients depend on.

## What to Check

### 1. SSE Event Name Consistency

Verify SSE event names match OpenAI/Anthropic specifications exactly.

**Trigger**: Changes to streaming functions (`_stream_openai`, `_stream_anthropic`)

**Current valid event names**:

- `message_start`
- `content_block_start`
- `content_block_delta`
- `content_block_stop`
- `message_delta`
- `message_stop`
- `error`

**BAD** (typo):

```python
yield 'event: messge_start' + chr(10) + ...
```

**GOOD**:

```python
yield 'event: message_start' + chr(10) + ...
```

### 2. Stop Reason Consistency

Verify stop reasons match expected values.

**Valid stop reasons**:

- `end_turn` - Normal conversation end
- `tool_use` - Tool call requested

**BAD**:

```python
stop_reason = 'stop'  # Wrong value
```

**GOOD**:

```python
stop_reason = 'end_turn'
```

### 3. Output Schema Consistency

Verify response fields remain consistent.

**OpenAI response fields**:

- `id`: `chatcmpl-<uuid>`
- `object`: `chat.completion`
- `choices[].message.role`: `assistant`
- `choices[].finish_reason`: `stop` or `tool_calls`

**Anthropic response fields**:

- `id`: `msg_<uuid>`
- `type`: `message`
- `content[].type`: `text`, `thinking`, `tool_use`
- `stop_reason`: `end_turn` or `tool_use`

### 4. Translation Function Changes

When modifying translation functions, verify contract tests exist.

**Trigger**:

- Changes to `_openai_to_ollama()`
- Changes to `_anthropic_to_ollama()`
- Changes to `_ollama_to_openai()`

**BAD**:

- Translation logic changed without test updates

**GOOD**:

- Contract tests updated
- Breaking changes documented

## Key Files to Check

- `proxy.py` - streaming functions and translation logic
- `tests/test_proxy.py` - contract tests

## Exclusions

- Internal helper functions
- Error message text changes

## Playbook Reference

Section 6: "No silent breaking changes."
