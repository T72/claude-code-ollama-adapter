# ollama-openai-proxy

> **A lightweight FastAPI adapter that bridges LiteLLM / Claude Code to Ollama's native `/api/chat` endpoint.**

LiteLLM's `openai/` provider always targets `/v1/chat/completions` and sends OpenAI-schema JSON. Ollama's `/api/chat` endpoint uses a completely different schema (including the `think` reasoning flag for GLM-5:cloud). This proxy sits between them and handles the translation transparently.

---

## Architecture

```
Claude Code / other clients
        |
        v
  LiteLLM proxy  :4001   (auth, routing, logging)
        |
        +-- openai/* --> Ollama :11434/v1          (Kimi, MiniMax, local coders)
        |
        +-- glm-5:cloud --> ollama-openai-proxy :4000  --> Ollama :11434/api/chat
                                                           (think: true injected)
```

**Key insight:** GLM-5:cloud is pointed at the proxy (`localhost:4000`) inside `litellm_config.yaml` instead of directly at Ollama. All other models continue to use Ollama's `/v1` path unchanged. No risk to your working Claude Code setup.

---

## Features

- Translates OpenAI `/v1/chat/completions` requests to Ollama `/api/chat` format
- Auto-injects `think: true` for GLM-5:cloud and other configurable reasoning models
- Exposes `reasoning_content` field in responses (Anthropic-style, readable by Claude Code)
- Full **streaming** (SSE) and **non-streaming** support
- `/v1/models` endpoint proxies Ollama's model list
- `/health` endpoint for monitoring
- Zero config needed — sensible defaults, everything overridable via env vars
- Single file, ~250 lines, easy to read and modify

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the proxy

```bash
uvicorn proxy:app --host 0.0.0.0 --port 4000
```

The proxy now listens on `http://localhost:4000` and forwards requests to Ollama at `http://localhost:11434` by default.

### 3. Configure LiteLLM

Use the provided `litellm_config.yaml`:

```yaml
- model_name: glm-5:cloud
  litellm_params:
    model: openai/glm-5:cloud
    api_base: http://localhost:4000/v1   # <-- proxy, not Ollama directly
    api_key: "dummy-key-not-checked-by-proxy"
```

Then start LiteLLM:

```bash
litellm --config litellm_config.yaml --port 4001
```

### 4. Test it

```bash
# Health check
curl http://localhost:4000/health

# Chat completion with GLM-5:cloud (think mode auto-enabled)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5:cloud",
    "messages": [{"role": "user", "content": "What is 17 * 23? Think step by step."}],
    "stream": false
  }'
```

---

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `THINK_MODELS` | *(empty)* | Comma-separated model names that get `think: true` injected in addition to the built-in defaults |

**Built-in think models** (always get `think: true`):
- `glm-5:cloud`
- `glm4:thinking`

Example — add a custom model:

```bash
THINK_MODELS="my-reasoning-model:latest" uvicorn proxy:app --port 4000
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Returns `{"status": "ok"}` |
| `/v1/models` | GET | Lists available Ollama models in OpenAI format |
| `/v1/chat/completions` | POST | Main proxy endpoint |

### Request mapping

| OpenAI field | Ollama field | Notes |
|---|---|---|
| `model` | `model` | Passed through |
| `messages` | `messages` | Passed through |
| `stream` | `stream` | Passed through |
| `temperature` | `options.temperature` | |
| `max_tokens` | `options.num_predict` | |
| `top_p` | `options.top_p` | |
| `stop` | `options.stop` | |
| *(auto)* | `think` | Set `true` for models in THINK_MODELS |

### Response mapping

| Ollama field | OpenAI field | Notes |
|---|---|---|
| `message.content` | `choices[0].message.content` | |
| `message.thinking` | `choices[0].message.reasoning_content` | GLM-5:cloud reasoning trace |
| `prompt_eval_count` | `usage.prompt_tokens` | |
| `eval_count` | `usage.completion_tokens` | |

---

## Why not just use Ollama's `/v1` path?

Ollama's `/v1/chat/completions` compatibility layer does not currently expose the `think` parameter or the `thinking` response field. To access GLM-5:cloud's reasoning output you must use `/api/chat` directly — which this proxy enables within a standard OpenAI/LiteLLM workflow.

---

## File Structure

```
ollama-openai-proxy/
  proxy.py             # FastAPI app (single-file, no framework magic)
  requirements.txt     # fastapi, uvicorn, httpx
  litellm_config.yaml  # Example LiteLLM config with dual-path routing
  README.md
  LICENSE              # MIT
```

---

## Requirements

- Python 3.11+
- Ollama running locally (or accessible via network)
- LiteLLM (optional, only needed if you want the full Claude Code integration)

---

## License

MIT — see [LICENSE](LICENSE).
