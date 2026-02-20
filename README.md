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

### 1. Clone and enter the repo

```cmd
git clone https://github.com/T72/ollama-openai-proxy.git
cd ollama-openai-proxy
```

### 2. Install proxy dependencies

```cmd
pip install -r requirements.txt
```

> **Note (Windows):** Skip the `source .venv/bin/activate` line — it's Linux-only.
> A venv is optional here since all three dependencies (`fastapi`, `uvicorn`, `httpx`)
> are likely already in your global Python environment.

### 3. Install LiteLLM (if not already installed)

```cmd
pip install "litellm[proxy]"
```

### 4. Start the proxy (Terminal 1 — keep it open)

```cmd
uvicorn proxy:app --host 0.0.0.0 --port 4000
```

Expected output:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4000 (Press CTRL+C to quit)
```

### 5. Start LiteLLM (Terminal 2 — keep it open)

```cmd
litellm --config litellm_config.yaml --port 4001
```

### 6. Test

```cmd
curl http://localhost:4000/health
```

```cmd
curl -X POST http://localhost:4000/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\": \"glm-5:cloud\", \"messages\": [{\"role\": \"user\", \"content\": \"What is 17 times 23?\"}], \"stream\": false}"
```

> **PowerShell alternative** (avoids escaping issues):
> ```powershell
> $body = @{ model = 'glm-5:cloud'; messages = @(@{ role = 'user'; content = 'What is 17 times 23?' }); stream = $false } | ConvertTo-Json -Depth 3
> Invoke-RestMethod -Uri http://localhost:4000/v1/chat/completions -Method POST -ContentType 'application/json' -Body $body
> ```

---

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `THINK_MODELS` | *(empty)* | Comma-separated model names that get `think: true` injected in addition to the built-in defaults |

**Built-in think models** (always get `think: true`):
- `glm-5:cloud`
- `glm4:thinking`

Example — add a custom model (Windows CMD):

```cmd
set THINK_MODELS=my-reasoning-model:latest
uvicorn proxy:app --port 4000
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

## Known Issues & Fixes

### FastAPI startup error on Python 3.13

Fixed in commit `a8d5987`. The original code used `JSONResponse | StreamingResponse`
as a return type annotation, which FastAPI tries to parse as a Pydantic response model.
Fix: `response_model=None` added to the `@app.post` decorator, return type changed to
the base `Response` class.

### `source` command not found on Windows

`source .venv/bin/activate` is Linux/macOS only. On Windows CMD use:
```cmd
.venv\Scripts\activate
```
Or skip the venv entirely if the global environment already has the dependencies.

### `litellm` command not found

LiteLLM is a separate install from the proxy itself:
```cmd
pip install "litellm[proxy]"
```

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

- Python 3.11+ (tested on 3.13)
- Ollama running locally (or accessible via network)
- LiteLLM — `pip install "litellm[proxy]"` (optional, only needed for full Claude Code integration)

---

## License

MIT — see [LICENSE](LICENSE).
