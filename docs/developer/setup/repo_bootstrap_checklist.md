
# Repo Bootstrap Checklist

Use this checklist when creating a new repository or standardizing an existing one.

---

## A) Governance & Workflow

- [ ] Add `docs/engineering_playbook.md` (v2+)
- [ ] Add `CONTRIBUTING.md` (includes lightweight TDD policy)
- [ ] Add `.github/pull_request_template.md`
- [ ] Add `.github/ISSUE_TEMPLATE/engineering-issue.yml`
- [ ] (Optional) Add `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled: false`
- [ ] Define label taxonomy (type/area/priority/phase/meta)
- [ ] Create initial milestones using `<Phase> – <Objective>`

### Branching Strategy (Develop-first)
- [ ] Confirm branches:
  - `develop` = integration branch (default target for PRs)
  - `main` = release/deploy branch
  - `feature/*` branches off `develop`
- [ ] Policy:
  - Merge `feature/*` ? `develop` via PR only (after CI passes)
  - Merge `develop` ? `main` only when verified/validated for deployment (release PR)
- [ ] (Optional) Add `docs/developer/branching-strategy.md` documenting the above

---

## B) Documentation Structure

- [ ] Create `docs/README.md`
- [ ] Create `docs/user/README.md`
- [ ] Create `docs/developer/README.md`
- [ ] Create `docs/operations/README.md`
- [ ] Create `docs/developer/adr/` and add `ADR-TEMPLATE.md`
- [ ] Create `docs/developer/reports/` (for analysis/review reports)
- [ ] Ensure “Docs placement rules” are included in `docs/ENGINEERING_PLAYBOOK.md`

---

## C) Testing & TDD Defaults

- [ ] Ensure test folders exist:
  - [ ] `tests/unit/`
  - [ ] `tests/contract/`
  - [ ] `tests/integration/` (optional)
- [ ] Ensure CI runs unit + contract tests by default
- [ ] Ensure a local command exists to run tests (e.g., `scripts/validate.sh` or `make test`)
- [ ] Enforce: bugfixes require a regression test (documented in CONTRIBUTING)

---

## D) CI/CD & Quality Gates (Develop + Main)

- [ ] Add GitHub Actions workflow for lint/typecheck/tests
- [ ] Ensure CI runs on:
  - PRs targeting `develop` and `main`
  - pushes to `develop` and `main`

### Branch Protection: `develop` (integration branch)
- [ ] Require CI checks to pass
- [ ] Require PR review (at least 1) before merge
- [ ] Disallow direct pushes to `develop` (recommended)

### Branch Protection: `main` (release/deploy branch)
- [ ] Require CI checks to pass
- [ ] Require PR review (at least 1) before merge
- [ ] Disallow direct pushes to `main`
- [ ] Policy/process: only merge into `main` from `develop` (release PR)

- [ ] (Optional) Add a dedicated Release PR template for `develop` ? `main` merges

---

## E) Project Tooling

- [ ] Add config and scripts for local dev (tooling depends on stack)
- [ ] Add `.env.example` (and document required env vars)
- [ ] Add Docker setup if applicable (`Dockerfile`, `compose.yaml`)
- [ ] Document how to run locally:
  - User-facing: `docs/user/getting-started.md` (if applicable)
  - Developer-facing: `docs/developer/setup.md`

---

## F) Sanity Checks

- [ ] Create a test PR to confirm:
  - [ ] CI runs on PR to `develop`
  - [ ] PR template appears
  - [ ] Issue template appears
  - [ ] Required folders/files exist
- [ ] Create a release PR (`develop` ? `main`) to confirm:
  - [ ] CI runs on PR to `main`
  - [ ] Branch protections enforce the workflow
