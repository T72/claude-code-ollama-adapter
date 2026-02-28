import asyncio
import pytest
import httpx
from proxy import (
    health,
    list_models,
    _normalize_messages,
    _openai_to_ollama,
    _anthropic_to_ollama,
    _ollama_to_openai,
    _post_with_think_fallback,
)

def test_health():
    response = asyncio.run(health())
    assert response["status"] == "ok"

def test_openai_to_ollama_translation():
    body = {
        "model": "glm-5:cloud",
        "messages": [{"role": "user", "content": "hi"}],
        "temperature": 0.7,
        "max_tokens": 100,
        "stop": ["END"],
        "tools": [{"type": "function", "function": {"name": "ping"}}],
    }
    ollama_body = _openai_to_ollama(body)
    assert ollama_body["model"] == "glm-5:cloud"
    assert ollama_body["think"] is True
    assert ollama_body["options"]["temperature"] == 0.7
    assert ollama_body["options"]["num_predict"] == 100
    assert ollama_body["options"]["stop"] == ["END"]
    assert ollama_body["tools"] == [{"type": "function", "function": {"name": "ping"}}]

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


def test_ollama_to_openai_tool_calls_translation():
    ollama_resp = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": "call_1", "function": {"name": "sum", "arguments": {"a": 1}}}
            ],
        },
        "done": True,
        "prompt_eval_count": 1,
        "eval_count": 2,
    }
    openai_resp = _ollama_to_openai(ollama_resp, "glm-5:cloud")
    choice = openai_resp["choices"][0]
    assert choice["finish_reason"] == "tool_calls"
    tool_call = choice["message"]["tool_calls"][0]
    assert tool_call["id"] == "call_1"
    assert tool_call["function"]["name"] == "sum"
    assert tool_call["function"]["arguments"] == '{"a": 1}'


def test_openai_to_ollama_strips_think_for_unsupported_model():
    body = {
        "model": "deepseek-coder-v2:16b",
        "messages": [{"role": "user", "content": "hi"}],
        "think": True
    }
    ollama_body = _openai_to_ollama(body)
    assert "think" not in ollama_body


def test_openai_to_ollama_preserves_num_predict_over_max_tokens():
    body = {
        "model": "glm-5:cloud",
        "messages": [{"role": "user", "content": "hi"}],
        "num_predict": 7,
        "max_tokens": 100,
    }
    ollama_body = _openai_to_ollama(body)
    assert ollama_body["options"]["num_predict"] == 7


def test_normalize_messages_flattens_text_blocks():
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "hello"},
                {"type": "text", "text": "world"},
                {"type": "image", "text": "ignored"},
            ],
        }
    ]
    normalized = _normalize_messages(messages)
    assert normalized[0]["content"] == "hello world"


def test_anthropic_to_ollama_translates_system_and_tool_result():
    body = {
        "model": "glm-5:cloud",
        "system": [{"type": "text", "text": "sys"}],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "hi"},
                    {"type": "tool_result", "tool_use_id": "toolu_1", "content": "ok"},
                ],
            }
        ],
        "tools": [
            {"name": "sum", "description": "add", "input_schema": {"type": "object"}}
        ],
        "max_tokens": 10,
    }
    ollama_body = _anthropic_to_ollama(body)
    assert ollama_body["messages"][0] == {"role": "system", "content": "sys"}
    assert {"role": "tool", "content": "ok", "tool_call_id": "toolu_1"} in ollama_body["messages"]
    assert {"role": "user", "content": "hi"} in ollama_body["messages"]
    assert ollama_body["tools"][0]["function"]["name"] == "sum"
    assert ollama_body["options"]["num_predict"] == 10


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


def test_post_with_think_fallback_no_retry_without_think():
    fake_client = _FakeAsyncClient([
        _FakeResponse(400, text='{"error":"model does not support thinking"}')
    ])
    response = asyncio.run(
        _post_with_think_fallback(
            fake_client,
            "http://localhost:11434/api/chat",
            {"model": "glm-5:cloud", "messages": [{"role": "user", "content": "hi"}]},
        )
    )
    assert response.status_code == 400
    assert len(fake_client.calls) == 1


class _FakeAsyncGetClient:
    def __init__(self, json_data):
        self._json_data = json_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url):
        return _FakeResponse(200, json_data=self._json_data)


def test_list_models_formats_ollama_tags(monkeypatch):
    fake_client = _FakeAsyncGetClient(
        {"models": [{"name": "model-a"}, {"name": "model-b"}]}
    )
    monkeypatch.setattr("proxy.httpx.AsyncClient", lambda timeout=30: fake_client)
    response = asyncio.run(list_models())
    data = response.body.decode()
    assert "\"id\":\"model-a\"" in data
    assert "\"id\":\"model-b\"" in data
