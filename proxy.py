"""
ollama-openai-proxy - proxy.py
Exposes an OpenAI-compatible POST /v1/chat/completions endpoint.
Translates incoming OpenAI-style requests to Ollama's native /api/chat format,
then maps Ollama's response back to OpenAI format.
Supports:
 - Non-streaming and streaming (SSE) responses
 - GLM-5:cloud think / reasoning_content fields
 - Configurable Ollama base URL and per-model think flag
 - OpenAI Responses API endpoint alias (/v1/responses)
Usage:
 uvicorn proxy:app --host 0.0.0.0 --port 4000
"""
import json
import os
import time
import uuid
from typing import AsyncIterator, Optional
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# SSE requires each event to end with two newlines.
# Defined as a constant to avoid f-string/backslash issues on Python 3.12+.
_SSE_SEP = '\n\n'

_DEFAULT_THINK_MODELS = {'glm-5:cloud', 'glm4:thinking'}
THINK_MODELS: set[str] = _DEFAULT_THINK_MODELS | {
    m.strip()
    for m in os.getenv('THINK_MODELS', '').split(',')
    if m.strip()
}

app = FastAPI(
    title='Ollama OpenAI Proxy',
    description='OpenAI-compatible proxy for Ollama /api/chat',
    version='0.1.7',
)

def _should_think(model: str, request_think: Optional[bool]) -> bool:
    if request_think is not None:
        return request_think
    return model in THINK_MODELS

def _openai_to_ollama(body: dict) -> dict:
    model: str = body.get('model', '')
    messages: list = body.get('messages', [])
    stream: bool = body.get('stream', False)
    think: Optional[bool] = body.get('think')

    ollama_body: dict = {
        'model': model,
        'messages': messages,
        'stream': stream,
    }

    if _should_think(model, think):
        ollama_body['think'] = True

    options: dict = {}
    for key in ('temperature', 'top_p', 'top_k', 'num_predict', 'seed', 'stop'):
        if key in body:
            options[key] = body[key]
    
    if 'max_tokens' in body and 'num_predict' not in options:
        options['num_predict'] = body['max_tokens']

    if options:
        ollama_body['options'] = options

    return ollama_body

def _ollama_to_openai(ollama_resp: dict, model: str) -> dict:
    msg = ollama_resp.get('message', {})
    content: str = msg.get('content', '')
    thinking: Optional[str] = msg.get('thinking')

    finish_reason = 'stop'
    if ollama_resp.get('done_reason') == 'length':
        finish_reason = 'length'

    choice_msg: dict = {'role': 'assistant', 'content': content}
    if thinking:
        choice_msg['reasoning_content'] = thinking

    # usage fields are critical for LiteLLM/Claude Code cost calculation
    usage = {
        'prompt_tokens': ollama_resp.get('prompt_eval_count', 0),
        'completion_tokens': ollama_resp.get('eval_count', 0),
        'total_tokens': (
            ollama_resp.get('prompt_eval_count', 0)
            + ollama_resp.get('eval_count', 0)
        ),
    }

    return {
        'id': 'chatcmpl-' + uuid.uuid4().hex[:12],
        'object': 'chat.completion',
        'created': int(time.time()),
        'model': model,
        'choices': [{'index': 0, 'message': choice_msg, 'finish_reason': finish_reason}],
        'usage': usage,
    }

def _ollama_chunk_to_openai_sse(chunk: dict, model: str, cid: str) -> str:
    msg = chunk.get('message', {})
    delta: dict = {}
    if msg.get('role'):
        delta['role'] = msg['role']
    if msg.get('content'):
        delta['content'] = msg['content']
    if msg.get('thinking'):
        delta['reasoning_content'] = msg['thinking']

    finish_reason = None
    usage = None

    if chunk.get('done'):
        reason = chunk.get('done_reason', 'stop')
        finish_reason = 'length' if reason == 'length' else 'stop'
        # Include usage in the final chunk if available
        usage = {
            'prompt_tokens': chunk.get('prompt_eval_count', 0),
            'completion_tokens': chunk.get('eval_count', 0),
            'total_tokens': (
                chunk.get('prompt_eval_count', 0)
                + chunk.get('eval_count', 0)
            ),
        }

    payload = {
        'id': cid,
        'object': 'chat.completion.chunk',
        'created': int(time.time()),
        'model': model,
        'choices': [{'index': 0, 'delta': delta, 'finish_reason': finish_reason}],
    }
    if usage:
        payload['usage'] = usage

    return 'data: ' + json.dumps(payload) + _SSE_SEP

@app.get('/health')
async def health():
    return {'status': 'ok', 'ollama_base': OLLAMA_BASE_URL}

@app.get('/v1/models')
async def list_models():
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(OLLAMA_BASE_URL + '/api/tags')
        r.raise_for_status()
        models = r.json().get('models', [])
        data = [
            {'id': m['name'], 'object': 'model', 'created': 0, 'owned_by': 'ollama'}
            for m in models
        ]
        return JSONResponse({'object': 'list', 'data': data})

@app.post('/v1/responses')
@app.post('/v1/chat/completions')
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get('model', '')
    stream = body.get('stream', False)

    ollama_body = _openai_to_ollama(body)
    url = OLLAMA_BASE_URL + '/api/chat'

    if stream:
        return StreamingResponse(
            _stream_ollama(url, ollama_body, model),
            media_type='text/event-stream',
        )

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, json=ollama_body)
        resp.raise_for_status()
        return JSONResponse(_ollama_to_openai(resp.json(), model))

async def _stream_ollama(url: str, ollama_body: dict, model: str):
    cid = 'chatcmpl-' + uuid.uuid4().hex[:12]
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            async with client.stream('POST', url, json=ollama_body) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    yield _ollama_chunk_to_openai_sse(chunk, model, cid)
                    
                    if chunk.get('done'):
                        break
        except Exception as exc:
            err = {'error': {'message': str(exc), 'type': 'upstream_error'}}
            yield 'data: ' + json.dumps(err) + _SSE_SEP
        
        yield 'data: [DONE]' + _SSE_SEP
