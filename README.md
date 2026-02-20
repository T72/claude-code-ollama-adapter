# ollama-openai-proxy

> **A lightweight FastAPI adapter that bridges LiteLLM / Claude Code to Ollama's native `/api/chat` endpoint.**

LiteLLM's `openai/` provider always targets `/v1/chat/completions` and sends OpenAI-schema JSON. Ollama's `/api/chat` endpoint uses a completely different schema (including the `think` reasoning flag for GLM-5:cloud). This proxy sits between them and handles the translation transparently.

---

## Why this exists?

**Claude Code** (and some other advanced agents) expect a strict implementation of tool-calling and reasoning blocks. When using LiteLLM to route to local Ollama models (like GLM-5:cloud), you often encounter two issues:
1. **Schema Mismatch**: LiteLLM sends OpenAI `/v1` format, but reasoning models in Ollama often require the native `/api/chat` format to trigger the `think` flag correctly.
2. **Tool-Calling Validation**: Claude Code is very sensitive to how tool arguments are delivered. This proxy ensures tool calls are accumulated and sent as valid JSON, preventing "Invalid tool parameters" errors.
3. **Silent Hangs**: Prevents Claude Code from hanging by suppressing unsupported `reasoning_content` blocks that LiteLLM cannot sign, ensuring a smooth handoff.

---

## Architecture

```text
Claude Code / other clients
      |
      v
LiteLLM proxy :4001 (auth, routing, logging)
      |
      +-- openai/*     --> Ollama :11434/v1 (Kimi, MiniMax, local coders)
      |
      +-- glm-5:cloud  --> ollama-openai-proxy :4000 --> Ollama :11434/api/chat
                                                          (think: true injected)
```

**Key insight:** GLM-5:cloud is pointed at the proxy (`localhost:4000`) inside `litellm_config.yaml` instead of directly at Ollama. All other models continue to use Ollama's `/v1` path unchanged. No risk to your working Claude Code setup.

---

## Features

- **Protocol Translation**: Translates OpenAI `/v1/chat/completions` requests to Ollama `/api/chat` format.
- **Tool-Call Accumulation**: Fixes "Invalid tool parameters" in Claude Code by ensuring tool arguments are fully formed before delivery.
- **Reasoning Support**: Auto-injects `think: true` for GLM-5:cloud and other configurable reasoning models.
- **Hang Prevention**: Suppresses `reasoning_content` in responses to prevent Claude Code silent hangs.
- **Full Streaming**: Supports SSE and non-streaming responses.
- **Docker Ready**: Includes Dockerfile and docker-compose.yml.
- **Lightweight**: Single file, ~300 lines, zero-config sensible defaults.

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

## Configuration

| Environment variable | Default | Description |
|----------------------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `THINK_MODELS` | (empty) | Comma-separated model names that get `think: true` injected |

---

## License

MIT
