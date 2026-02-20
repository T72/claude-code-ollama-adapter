'''
ollama-openai-proxy - proxy.py
Exposes OpenAI-compatible (/v1/chat/completions) AND Anthropic-compatible (/v1/messages) endpoints.
Translates incoming requests to Ollama's native /api/chat format.
'''

import json
import os
import re
import time
import uuid
from typing import AsyncIterator, Optional
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
_SSE_SEP = chr(10) + chr(10)

# Think models: opt-in only via THINK_MODELS env var
_DEFAULT_THINK_MODELS: set[str] = set()
THINK_MODELS: set[str] = _DEFAULT_THINK_MODELS | {
    m.strip() for m in os.getenv('THINK_MODELS', '').split(',') if m.strip()
}

_ANTHROPIC_DROP_PARAMS = {'output_config', 'thinking', 'metadata', 'anthropic_version', 'betas'}

app = FastAPI(title='Ollama OpenAI/Anthropic Proxy', version='0.3.3')

def _should_think(model: str, request_think: Optional[bool]) -> bool:
    if request_think is not None: return request_think
    return model in THINK_MODELS

def _normalize_messages(messages: list) -> list:
    normalized = []
    for msg in messages:
        content = msg.get('content')
        if isinstance(content, list):
            text = ' '.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text')
            normalized.append({**msg, 'content': text})
        else:
            normalized.append(msg)
    return normalized

def _openai_to_ollama(body: dict) -> dict:
    model = body.get('model', '')
    messages = _normalize_messages(body.get('messages', []))
    stream = body.get('stream', False)
    ollama_body = {'model': model, 'messages': messages, 'stream': stream}
    if _should_think(model, body.get('think')): ollama_body['think'] = True
    options = {}
    for key in ('temperature', 'top_p', 'top_k', 'num_predict', 'seed', 'stop'):
        if key in body: options[key] = body[key]
    if 'max_tokens' in body and 'num_predict' not in options:
        options['num_predict'] = body['max_tokens']
    if options: ollama_body['options'] = options
    return ollama_body

def _anthropic_to_ollama(body: dict) -> dict:
    model = body.get('model', '')
    messages = []
    system = body.get('system')
    if isinstance(system, list):
        system_text = ' '.join(b.get('text', '') for b in system if b.get('type') == 'text')
        messages.append({'role': 'system', 'content': system_text})
    elif isinstance(system, str):
        messages.append({'role': 'system', 'content': system})

    for m in body.get('messages', []):
        content = m.get('content')
        if isinstance(content, list):
            text = ' '.join(b.get('text', '') for b in content if b.get('type') == 'text')
            messages.append({'role': m.get('role'), 'content': text})
        else:
            messages.append(m)

    ollama_body = {'model': model, 'messages': messages, 'stream': body.get('stream', False)}
    if 'max_tokens' in body:
        ollama_body['options'] = {'num_predict': body['max_tokens']}
    return ollama_body

@app.post('/v1/messages')
async def anthropic_messages(request: Request):
    body = await request.json()
    model = body.get('model', '')
    stream = body.get('stream', False)
    ollama_body = _anthropic_to_ollama(body)
    url = OLLAMA_BASE_URL + '/api/chat'

    if stream:
        return StreamingResponse(_stream_anthropic(url, ollama_body, model), media_type='text/event-stream')

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, json=ollama_body)
        if resp.status_code != 200:
            return Response(content=resp.text, status_code=resp.status_code)
        ollama_data = resp.json()
        content = ollama_data.get('message', {}).get('content', '')
        return JSONResponse({
            'id': 'msg_' + uuid.uuid4().hex[:12], 'type': 'message', 'role': 'assistant',
            'content': [{'type': 'text', 'text': content}], 'model': model, 'stop_reason': 'end_turn',
            'usage': {'input_tokens': ollama_data.get('prompt_eval_count', 0), 'output_tokens': ollama_data.get('eval_count', 0)}
        })

async def _stream_anthropic(url: str, ollama_body: dict, model: str):
    mid = 'msg_' + uuid.uuid4().hex[:12]
    # Anthropic initial events
    yield 'event: message_start' + chr(10) + f'data: {json.dumps({"type": "message_start", "message": {"id": mid, "type": "message", "role": "assistant", "content": [], "model": model, "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 0, "output_tokens": 0}}})}' + _SSE_SEP
    yield 'event: content_block_start' + chr(10) + f'data: {json.dumps({"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})}' + _SSE_SEP

    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream('POST', url, json=ollama_body) as resp:
            if resp.status_code != 200:
                yield f'data: {json.dumps({"type": "error", "error": {"type": "upstream_error", "message": (await resp.aread()).decode()}})}' + _SSE_SEP
                return
            async for line in resp.aiter_lines():
                if not line.strip(): continue
                chunk = json.loads(line)
                content = chunk.get('message', {}).get('content', '')
                if content:
                    yield 'event: content_block_delta' + chr(10) + f'data: {json.dumps({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": content}})}' + _SSE_SEP
                if chunk.get('done'):
                    yield 'event: content_block_stop' + chr(10) + f'data: {json.dumps({"type": "content_block_stop", "index": 0})}' + _SSE_SEP
                    yield 'event: message_delta' + chr(10) + f'data: {json.dumps({"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": chunk.get("eval_count", 0)}})}' + _SSE_SEP
                    yield 'event: message_stop' + chr(10) + 'data: {"type": "message_stop"}' + _SSE_SEP

@app.post('/v1/chat/completions')
@app.post('/v1/responses')
async def chat_completions(request: Request):
    body = await request.json()
    for p in _ANTHROPIC_DROP_PARAMS: body.pop(p, None)
    model = body.get('model', '')
    stream = body.get('stream', False)
    ollama_body = _openai_to_ollama(body)
    url = OLLAMA_BASE_URL + '/api/chat'

    if stream:
        return StreamingResponse(_stream_openai(url, ollama_body, model), media_type='text/event-stream')

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, json=ollama_body)
        resp.raise_for_status()
        return JSONResponse(_ollama_to_openai(resp.json(), model))

def _ollama_to_openai(ollama_resp: dict, model: str) -> dict:
    content = ollama_resp.get('message', {}).get('content', '')
    return {
        'id': 'chatcmpl-' + uuid.uuid4().hex[:12],
        'object': 'chat.completion',
        'created': int(time.time()),
        'model': model,
        'choices': [{
            'index': 0,
            'message': {'role': 'assistant', 'content': content},
            'finish_reason': 'stop'
        }],
        'usage': {
            'prompt_tokens': ollama_resp.get('prompt_eval_count', 0),
            'completion_tokens': ollama_resp.get('eval_count', 0),
            'total_tokens': ollama_resp.get('prompt_eval_count', 0) + ollama_resp.get('eval_count', 0)
        }
    }

async def _stream_openai(url: str, ollama_body: dict, model: str):
    cid = 'chatcmpl-' + uuid.uuid4().hex[:12]
    # OpenAI compliant initial role chunk
    yield 'data: ' + json.dumps({
        'id': cid, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model,
        'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]
    }) + _SSE_SEP

    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream('POST', url, json=ollama_body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip(): continue
                chunk = json.loads(line)
                content = chunk.get('message', {}).get('content', '')
                if content:
                    yield 'data: ' + json.dumps({
                        'id': cid, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model,
                        'choices': [{'index': 0, 'delta': {'content': content}, 'finish_reason': None}]
                    }) + _SSE_SEP
                if chunk.get('done'):
                    # Final compliance chunk with usage and stop reason
                    yield 'data: ' + json.dumps({
                        'id': cid, 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': model,
                        'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}],
                        'usage': {
                            'prompt_tokens': chunk.get('prompt_eval_count', 0),
                            'completion_tokens': chunk.get('eval_count', 0),
                            'total_tokens': chunk.get('prompt_eval_count', 0) + chunk.get('eval_count', 0)
                        }
                    }) + _SSE_SEP
    yield 'data: [DONE]' + _SSE_SEP

@app.get('/health')
async def health(): return {'status': 'ok', 'ollama_base': OLLAMA_BASE_URL}

@app.get('/v1/models')
async def list_models():
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(OLLAMA_BASE_URL + '/api/tags')
        r.raise_for_status()
        models = r.json().get('models', [])
        return JSONResponse({
            'object': 'list',
            'data': [
                {'id': m['name'], 'object': 'model', 'created': 0, 'owned_by': 'ollama'}
                for m in models
            ]
        })
