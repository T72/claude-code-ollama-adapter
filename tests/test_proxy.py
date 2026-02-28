import asyncio
import pytest
import httpx
from proxy import health, _openai_to_ollama, _ollama_to_openai, _post_with_think_fallback

def test_health():
    response = asyncio.run(health())
    assert response["status"] == "ok"

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


def test_openai_to_ollama_strips_think_for_unsupported_model():
    body = {
        "model": "deepseek-coder-v2:16b",
        "messages": [{"role": "user", "content": "hi"}],
        "think": True
    }
    ollama_body = _openai_to_ollama(body)
    assert "think" not in ollama_body


class _FakeResponse:
    def __init__(self, status_code, text="", json_data=None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data or {}
        self._request = httpx.Request("POST", "http://localhost:11434/api/chat")

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "status error",
                request=self._request,
                response=httpx.Response(self.status_code, request=self._request, text=self.text),
            )


class _FakeAsyncClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        self.calls.append(json)
        return self._responses.pop(0)


def test_post_with_think_fallback_retries_without_think_on_unsupported_thinking():
    fake_client = _FakeAsyncClient([
        _FakeResponse(400, text='{"error":"model does not support thinking"}'),
        _FakeResponse(
            200,
            json_data={
                "message": {"role": "assistant", "content": "ok"},
                "done": True,
                "prompt_eval_count": 1,
                "eval_count": 2,
            },
        ),
    ])

    response = asyncio.run(
        _post_with_think_fallback(
            fake_client,
            "http://localhost:11434/api/chat",
            {
                "model": "glm-5:cloud",
                "messages": [{"role": "user", "content": "hello"}],
                "think": True,
            },
        )
    )

    assert response.status_code == 200
    assert fake_client.calls[0]["think"] is True
    assert "think" not in fake_client.calls[1]
