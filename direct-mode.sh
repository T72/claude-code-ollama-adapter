#!/bin/bash
# direct-mode.sh.example
# Template for Direct Mode - bypass LiteLLM and connect Claude Code directly to the adapter
#
# Usage:
#   1. Copy this file to direct-mode.sh
#   2. Customize the environment variables below as needed
#   3. Source this file before running Claude Code: source direct-mode.sh
#   4. Start the adapter: uvicorn proxy:app --host 0.0.0.0 --port 4000
#   5. Run Claude Code: claude --model <your-model>
#
# For more details, see README.md "Direct Mode (Skip LiteLLM)" section.

# ============================================================================
# Required: Point Claude Code to the adapter
# ============================================================================
# The adapter runs on port 4000 and exposes both Anthropic and OpenAI compatible endpoints
export ANTHROPIC_BASE_URL=http://localhost:4000

# Any non-empty value works - the adapter doesn't require authentication
export ANTHROPIC_API_KEY=ollama

# ============================================================================
# Optional: Configure models that support thinking/reasoning
# ============================================================================
# Models like glm-5:cloud and glm4:thinking support the 'think' parameter
# Uncomment and modify as needed:
# export THINK_MODELS="glm-5:cloud,glm4:thinking"

# ============================================================================
# Optional: Ollama configuration
# ============================================================================
# The adapter connects to Ollama - customize if Ollama runs on a different URL
# export OLLAMA_BASE_URL=http://localhost:11434

# ============================================================================
# Usage hints
# ============================================================================
echo "Direct Mode configured!"
echo ""
echo "To use with Claude Code:"
echo "  1. Start the adapter: uvicorn proxy:app --host 0.0.0.0 --port 4000"
echo "  2. Run Claude Code with a local model, e.g.:"
echo "       claude --model qwen3-coder:latest"
echo "       claude --model llama3:latest"
echo "       claude --model kimi-k2:latest"
echo ""
echo "Available models can be listed via: curl http://localhost:4000/v1/models"
