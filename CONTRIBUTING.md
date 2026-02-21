# Contributing to claude-code-ollama-adapter

Thank you for your interest in contributing! This document explains how to get involved.

---

## Branching Strategy

| Branch | Purpose |
|--------|----------|
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

### 5. Run Tests

```bash
pytest tests/
```

All tests must pass before submitting.

### 6. Commit with Conventional Commits

```
feat: add streaming support for new endpoint
fix: handle empty tool_calls array
docs: update README with new env vars
chore: bump dependencies
```

### 7. Open a Pull Request

- Target the `main` branch.
- Fill in the PR template.
- Reference any related issues.

---

## Code Style

- Python: follow PEP 8, use type hints where practical.
- Keep functions small and focused.
- Prefer explicit over implicit.

---

## Reporting Issues

Open an issue with:
- A clear title and description.
- Steps to reproduce.
- Expected vs actual behavior.
- Python version and OS.

---

## Security

To report a vulnerability privately, see [SECURITY.md](SECURITY.md).

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
