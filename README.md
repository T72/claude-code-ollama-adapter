# claude-code-ollama-adapter

[![CI](https://github.com/T72/claude-code-ollama-adapter/actions/workflows/ci.yml/badge.svg)](https://github.com/T72/claude-code-ollama-adapter/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A FastAPI proxy that lets Claude Code (and any Anthropic or OpenAI-compatible client) talk directly to Ollama's native `/api/chat` endpoint.**

Exposes two fully-compatible endpoints:
- **`/v1/messages`** — Anthropic Messages API (used natively by Claude Code)
- **`/v1/chat/completions`** — OpenAI Chat Completions API (used by LiteLLM, OpenAI SDKs, etc.)

Both translate transparently to Ollama's `/api/chat` format, handling streaming, tool calls, and optional `think` reasoning injection.

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
    +-- glm-5:cloud --> claude-code-ollama-adapter :4000 --> Ollama :11434/api/chat
                                                         (think: true injected)
```

---

## Features

- **Anthropic `/v1/messages`** endpoint — full Claude Code compatibility (streaming + tool use)
- **OpenAI `/v1/chat/completions`** endpoint — LiteLLM / OpenAI SDK compatible
- **Tool / function calling** — translates both directions (Anthropic `tool_use` ↔ Ollama `tool_calls`)
- **Reasoning / thinking** support — opt-in `think: true` injection for GLM-5:cloud and configurable models
- **Full streaming** (SSE) and **non-streaming** support
- **`/v1/models`** — proxies Ollama's model list in OpenAI format
- **`/health`** — health check endpoint
- Zero config needed — sensible defaults, everything overridable via env vars
- Single file `proxy.py`, ~350 lines, easy to read and modify
- **Docker support** — includes `Dockerfile`
- **CI/CD** — GitHub Actions workflow for automated testing

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/T72/claude-code-ollama-adapter.git
cd claude-code-ollama-adapter
```

### 2. Run with Docker (Recommended)

```bash
docker build -t claude-code-ollama-adapter .
docker run -p 4000:4000 claude-code-ollama-adapter
```

The proxy will be available at `http://localhost:4000`.

### 3. Manual Installation

```bash
pip install -r requirements.txt
uvicorn proxy:app --host 0.0.0.0 --port 4000
```

---

## Usage with Claude Code

Point Claude Code at the adapter instead of Anthropic directly:

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=ollama
claude --model qwen3-coder:latest
```

---

## Usage with LiteLLM

In your `litellm_config.yaml`, route specific models through the adapter:

```yaml
model_list:
  - model_name: glm-5:cloud
    litellm_params:
      model: openai/glm-5:cloud
      api_base: http://localhost:4000
      api_key: ollama
```

See [`litellm_config.yaml`](litellm_config.yaml) for a full example.

---

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `THINK_MODELS` | (empty) | Comma-separated model names that get `think: true` injected |

---

## LiteLLM Modes

This repo supports two LiteLLM operating modes:

### Mode 1: DB-Free Local Mode (Default)

Use `litellm_config.yaml` for local development without a database.

- **No authentication** - requests pass through directly
- **Works out of the box** - just run `litellm --config litellm_config.yaml`
- **Use case**: Local development, testing, prototyping

```bash
litellm --config litellm_config.yaml --port 4001
```

### Mode 2: DB-Backed Secure Mode (Optional)

Use `litellm_config.secure.example.yaml` for production or shared environments requiring authentication.

- **Virtual key authentication** - requires `master_key` + `DATABASE_URL`
- **Spend tracking & rate limiting** - built-in LiteLLM features
- **Use case**: Production deployments, team environments

```bash
# Set required environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/litellm"
export LITELLM_MASTER_KEY="sk-your-secure-key"

# Start LiteLLM with secure config
litellm --config litellm_config.secure.example.yaml --port 4001
```

> ⚠️ **Warning**: Setting `master_key` without `DATABASE_URL` will cause all requests to fail with `No connected db.` error. Use the default `litellm_config.yaml` for local development.

---

## Testing

```bash
pip install pytest httpx fastapi[testclient]
pytest tests/
```

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

---

## Security

To report a vulnerability, please see [SECURITY.md](SECURITY.md).

---

## License

MIT — see [LICENSE](LICENSE).
