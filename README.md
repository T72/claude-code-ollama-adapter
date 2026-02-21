# ollama-openai-proxy

> **A lightweight FastAPI adapter that bridges LiteLLM / Claude Code to Ollama's native `/api/chat` endpoint.**

LiteLLM's `openai/` provider always targets `/v1/chat/completions` and sends OpenAI-schema JSON. Ollama's `/api/chat` endpoint uses a completely different schema (including the `think` reasoning flag for GLM-5:cloud). This proxy sits between them and handles the translation transparently.

---

## Architecture

```
Claude Code / other clients
    |
    v
LiteLLM proxy :4001 (auth, routing, logging)
    |
    +-- openai/* --> Ollama :11434/v1 (Kimi, MiniMax, local coders)
    |
    +-- glm-5:cloud --> ollama-openai-proxy :4000 --> Ollama :11434/api/chat
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
- **Docker Support** — Includes Dockerfile and docker-compose.yml
- **CI/CD** — GitHub Actions workflow for automated testing

---

## Quick Start

### 1. Clone and enter the repo

```bash
git clone https://github.com/T72/ollama-openai-proxy.git
cd ollama-openai-proxy
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up -d --build
```

The proxy will be available at `http://localhost:4000`.

### 3. Manual Installation

```bash
pip install -r requirements.txt
uvicorn proxy:app --host 0.0.0.0 --port 4000
```

---

## Testing

Run the unit tests to verify translation logic:
```bash
pytest tests/
```

---

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `THINK_MODELS` | (empty) | Comma-separated model names that get `think: true` injected |

---

## License

MIT
