# Contributing to claude-code-ollama-adapter

Thank you for your interest in contributing! This document explains how to get involved.

---

## Branching Strategy

| Branch | Purpose |
|--------|----------|
| `main` | Stable, released code. Deployable at all times. **Hotfixes only.** |
| `develop` | Active development. All feature PRs target here first. |

> **Note:** For complete branching workflow details, see [docs/developer/branching-strategy.md](docs/developer/branching-strategy.md).

### Feature Workflow
- Create feature branches from `develop`: `git checkout develop && git checkout -b feat/my-feature`
- Target `develop` for pull requests
- Features merge to `develop` via squash merge

### Hotfix Workflow
- Create hotfix branches from `main`: `git checkout main && git checkout -b hotfix/my-fix`
- Target `main` for hotfix pull requests
- Hotfixes are back-merged to `develop` automatically

---

## How to Contribute

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/claude-code-ollama-adapter.git
cd claude-code-ollama-adapter
```

### 2. Create a Branch

```bash
# For features: branch from develop
git checkout develop
git checkout -b fix/my-bugfix
# or
git checkout -b feat/my-feature

# For hotfixes: branch from main
git checkout main
git checkout -b hotfix/my-fix
```

Use conventional prefixes: `fix/`, `feat/`, `docs/`, `chore/`, `refactor/`, `hotfix/`.</parameter>
<task_progress>- [x] Create GitHub issue #10 for CONTRIBUTING.md sync
- [x] Update CONTRIBUTING.md Branching Strategy section
- [x] Update CONTRIBUTING.md "Create a Branch" section
- [ ] Update CONTRIBUTING.md "Open a Pull Request" section
- [x] Add cross-reference to branching-strategy.md
- [ ] Create PR to resolve issue #10</task_progress>
</invoke>

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

- **Features:** Target the `develop` branch.
- **Hotfixes:** Target the `main` branch.
- Fill in the PR template.
- Reference any related issues.</parameter>
<task_progress>- [x] Create GitHub issue #10 for CONTRIBUTING.md sync
- [x] Update CONTRIBUTING.md Branching Strategy section
- [x] Update CONTRIBUTING.md "Create a Branch" section
- [x] Update CONTRIBUTING.md "Open a Pull Request" section
- [x] Add cross-reference to branching-strategy.md
- [ ] Create PR to resolve issue #10</task_progress>
</invoke>

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
