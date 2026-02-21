# Contributing to claude-code-ollama-adapter

Thank you for your interest in contributing! This document explains how to get involved.

---

## Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, released code. All PRs must target `main`. |
| `develop` | Active development. Experimental features land here first. |

Please base your feature branches off `main` unless you are working on something experimental, in which case branch from `develop`.

---

## How to Contribute

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/claude-code-ollama-adapter.git
cd claude-code-ollama-adapter
```

### 2. Create a Branch

```bash
git checkout -b fix/my-bugfix
# or
git checkout -b feat/my-feature
```

Use conventional prefixes: `fix/`, `feat/`, `docs/`, `chore/`, `refactor/`.

### 3. Set Up Your Environment

```bash
pip install -r requirements.txt
pip install pytest httpx fastapi[testclient]
```

### 4. Make Your Changes

- Keep changes focused and minimal.
- `proxy.py` is intentionally a single file — please keep it that way.
- Add or update tests in `tests/test_proxy.py` for any logic change.

### 5. Run the Tests

```bash
pytest tests/
```

All tests must pass before submitting a PR.

### 6. Commit with a Clear Message

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for /v1/responses endpoint
fix: handle empty tool_calls list in stream
docs: update README Quick Start section
```

### 7. Open a Pull Request

- Target the `main` branch.
- Fill in the PR template (describes your change and links the related issue).
- Ensure CI is green before requesting review.

---

## Code Style

- Python 3.10+
- No external linters are enforced, but please follow PEP 8.
- Keep functions short and well-named.
- Prefer explicit over implicit.

---

## Reporting Bugs

Please use the [Bug Report issue template](https://github.com/T72/claude-code-ollama-adapter/issues/new?template=bug_report.md).

## Requesting Features

Please use the [Feature Request issue template](https://github.com/T72/claude-code-ollama-adapter/issues/new?template=feature_request.md).

---

## Code of Conduct

By participating in this project you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

---

Thank you for helping make this project better!
