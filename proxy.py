"""
ollama-openai-proxy  –  proxy.py

Exposes an OpenAI-compatible  POST /v1/chat/completions  endpoint.
Translates incoming OpenAI-style requests to Ollama's native /api/chat format,
then maps Ollama's response back to OpenAI format.

Supports:
  - Non-streaming and streaming (SSE) responses
  - GLM-5:cloud  think / reasoning_content  fields
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

# ---------------------------------------------------------------------------
# Configuration (override via environment variables)
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Models that should have  think: true  injected automatically.
# Extend this list or set THINK_MODELS env var (comma-separated).
_DEFAULT_THINK_MODELS = {"glm-5:cloud", "glm4:thinking"}
THINK_MODELS: set[str] = _DEFAULT_THINK_MODELS | {
    m.strip()
    for m in os.getenv("THINK_MODELS", "").split(",")
    if m.strip()
}

app = FastAPI(
    title="Ollama OpenAI Proxy",
    description="OpenAI-compatible proxy for Ollama /api/chat",
    version="0.1.1",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _should_think(model: str, request_think: Optional[bool]) -> bool:
    """Return True if think mode should be enabled for this model/request."""
    if request_think is not None:
        return request_think
    return model in THINK_MODELS


def _openai_to_ollama(body: dict) -> dict:
    """Convert an OpenAI /v1/chat/completions request body to Ollama /api/chat."""
    model: str = body.get("model", "")
    messages: list = body.get("messages", [])
    stream: bool = body.get("stream", False)
    think: Optional[bool] = body.get("think")  # passthrough if caller set it

    ollama_body: dict = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }

    if _should_think(model, think):
        ollama_body["think"] = True

    # Forward supported options
    options: dict = {}
    for key in ("temperature", "top_p", "top_k", "num_predict", "seed", "stop"):
        if key in body:
            options[key] = body[key]
    # OpenAI uses max_tokens; Ollama uses num_predict
    if "max_tokens" in body and "num_predict" not in options:
        options["num_predict"] = body["max_tokens"]
    if options:
        ollama_body["options"] = options

    return ollama_body


def _ollama_to_openai(ollama_resp: dict, model: str) -> dict:
    """Convert a non-streaming Ollama /api/chat response to OpenAI format."""
    msg = ollama_resp.get("message", {})
    content: str = msg.get("content", "")
    thinking: Optional[str] = msg.get("thinking")  # GLM-5:cloud reasoning

    finish_reason = "stop"
    if ollama_resp.get("done_reason") == "length":
        finish_reason = "length"

    choice_msg: dict = {"role": "assistant", "content": content}
    if thinking:
        # Expose thinking content as reasoning_content (Anthropic-style) so
        # Claude Code / LiteLLM consumers can access it.
        choice_msg["reasoning_content"] = thinking

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": choice_msg,
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": ollama_resp.get("prompt_eval_count", 0),
            "completion_tokens": ollama_resp.get("eval_count", 0),
            "total_tokens": (
                ollama_resp.get("prompt_eval_count", 0)
                + ollama_resp.get("eval_count", 0)
            ),
        },
    }


def _ollama_chunk_to_openai_sse(chunk: dict, model: str, cid: str) -> str:
    """Convert one streaming Ollama chunk to an OpenAI SSE data line."""
    msg = chunk.get("message", {})
    delta: dict = {}

    if msg.get("role"):
        delta["role"] = msg["role"]
    if msg.get("content"):
        delta["content"] = msg["content"]
    if msg.get("thinking"):
        delta["reasoning_content"] = msg["thinking"]

    finish_reason = None
    if chunk.get("done"):
        reason = chunk.get("done_reason", "stop")
        finish_reason = "length" if reason == "length" else "stop"

    payload = {
        "id": cid,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
    }
    return f"data: {json.dumps(payload)}

"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok", "ollama_base": OLLAMA_BASE_URL}


@app.get("/v1/models")
async def list_models() -> JSONResponse:
    """Proxy Ollama's model list as OpenAI-style /v1/models."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            r.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    models = r.json().get("models", [])
    data = [
        {
            "id": m["name"],
            "object": "model",
            "created": 0,
            "owned_by": "ollama",
        }
        for m in models
    ]
    return JSONResponse({"object": "list", "data": data})


@app.post("/v1/responses", response_model=None)
@app.post("/v1/chat/completions", response_model=None)
async def chat_completions(request: Request) -> Response:
    """
    Main proxy endpoint: OpenAI -> Ollama /api/chat -> OpenAI.
    Supports both standard /v1/chat/completions and the /v1/responses alias.
    """
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}") from exc

    model: str = body.get("model", "")
    stream: bool = body.get("stream", False)
    ollama_body = _openai_to_ollama(body)

    url = f"{OLLAMA_BASE_URL}/api/chat"

    if stream:
        return StreamingResponse(
            _stream_ollama(url, ollama_body, model),
            media_type="text/event-stream",
        )

    # --- Non-streaming ---
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(url, json=ollama_body)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=exc.response.text,
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return JSONResponse(_ollama_to_openai(resp.json(), model))


async def _stream_ollama(
    url: str, ollama_body: dict, model: str
) -> AsyncIterator[str]:
    """Yield OpenAI SSE chunks from a streaming Ollama response."""
    cid = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            async with client.stream("POST", url, json=ollama_body) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    yield _ollama_chunk_to_openai_sse(chunk, model, cid)
                    if chunk.get("done"):
                        break
        except httpx.HTTPStatusError as exc:
            error_payload = {
                "error": {
                    "message": exc.response.text,
                    "type": "upstream_error",
                    "code": exc.response.status_code,
                }
            }
            yield f"data: {json.dumps(error_payload)}

"
    yield "data: [DONE]

"
