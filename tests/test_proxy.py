import json
import pytest
from fastapi.testclient import TestClient
from proxy import app, _openai_to_ollama, _ollama_to_openai

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_openai_to_ollama_translation():
    body = {
        "model": "glm-5:cloud",
        "messages": [{"role": "user", "content": "hi"}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    ollama_body = _openai_to_ollama(body)
    assert ollama_body["model"] == "glm-5:cloud"
    assert ollama_body["think"] is True
    assert ollama_body["options"]["temperature"] == 0.7
    assert ollama_body["options"]["num_predict"] == 100

def test_ollama_to_openai_translation():
    ollama_resp = {
        "message": {"role": "assistant", "content": "hello", "thinking": "reasoning..."},
        "done": True,
        "prompt_eval_count": 10,
        "eval_count": 20
    }
    openai_resp = _ollama_to_openai(ollama_resp, "glm-5:cloud")
    assert openai_resp["choices"][0]["message"]["content"] == "hello"
    assert openai_resp["choices"][0]["message"]["reasoning_content"] == "reasoning..."
    assert openai_resp["usage"]["total_tokens"] == 30
