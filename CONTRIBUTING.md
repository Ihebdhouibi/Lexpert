# Contributing to Lexpert

Thanks for contributing. This guide covers the branch model, commit style, local setup, and the
checklist every change must pass.

## What you are working on

Lexpert is a multi-vertical tele-consulting marketplace for Tunisia with an escrow payment model.
Read `docs/Phase1-Feasibility-Business-Architecture.md` once before your first issue, then
`docs/implementation/lexpert_plan.md` for what is being built in what order and
`docs/implementation/roadmap.md` for the build order and what each phase demonstrates.

If you are working on the interface, read `docs/design/design_brief.md` too. Two rules from it
are worth repeating here because they cause the most rework when missed: **every screen ships
with its states** (loading, empty, error, offline, plus the product-specific ones like pending
acceptance and hold-window countdown), and **no screen is implemented before its design exists**.

Two MVP constraints to keep in mind while implementing anything:

- **The escrow is simulated.** No real money moves in the MVP. The ledger and state machine are
  real code; the payment provider behind them is a simulator implementing the `EscrowProvider`
  interface. Keep provider-specific behavior inside the adapter so a licensed partner can replace
  it in Beta without touching the ledger.
- **The product UI is French only.** All user-facing strings are French and go through the i18n
  catalogue, never hard-coded in components. Code, comments, commits and issues are English.

## Branch model

```
main  <-  stable-testing  <-  develop  <-  feature/*  |  chore/*
```

- `main` — protected, release.
- `stable-testing` — release candidate.
- `develop` — integration branch; all feature work merges here. This is the default branch.
- `feature/*` / `chore/*` — one branch per issue.

Rules:

- One issue = one branch = one PR into `develop`. Squash-merge.
- No direct commits to protected branches (`main`, `stable-testing`, `develop`).
- Use the terminal `git` CLI for version control.

## Commit style

Conventional commits, enforced by a `commit-msg` hook. Allowed types:

`feat`, `chore`, `docs`, `tests`, `bug`, `ci`

Format: `<type>(<scope>): <short imperative subject>`, scope optional (`web`, `api`, `infra`).
Add a body only when it adds information.

Two hard rules for all commits, code, comments, PRs, and docs:

- **No AI attribution** (no "Generated with ...", "Co-authored-by: ...", etc.). Describe the
  change only.
- **No emojis** anywhere.

This is a public repository: never commit secrets, credentials, or client data. There is a further
rule specific to this project: never commit real professional licence numbers, real identity
documents, or any real consultation content, even as test fixtures. Use synthetic data.

## Local setup

Requires Python 3.11 (see `.python-version`) and Node 20 (see `.nvmrc`), plus PostgreSQL 16
(Docker is fine). The Python version is pinned deliberately: 3.11 is what the rest of the
team's stack runs, and CI runs the same version, so a local pass means a CI pass.

```bash
# Backend
cd apps/api
pip install -e ".[dev]"

# Frontend
cd ../web
npm ci

# Git hooks, from the repository root (once per clone)
cd ../..
pip install pre-commit
pre-commit install && pre-commit install --hook-type commit-msg
```

Copy `.env.example` to `.env` and fill it in. `.env` is git-ignored and must stay that way.

Run the checks the way CI runs them:

```bash
cd apps/api && ruff check . && ruff format --check . && mypy src && pytest
cd apps/web && npm run lint && npm run format:check && npm run typecheck && npm test
```

## Working on an issue

```bash
git checkout develop && git pull
git checkout -b feature/<short-slug>     # branch name is given on the issue
# ... work, committing in conventional-commit style ...
git push -u origin feature/<short-slug>
gh pr create --base develop --fill
```

Every issue states its **Requirements**, its **Validation / test checks**, and its
**Deliverables**. Those three sections are the bar the PR is reviewed against. If a requirement
turns out to be wrong or impossible, say so on the issue before implementing something different
-- do not silently change the scope in the PR.

## Pull request checklist

Before opening a PR into `develop`:

- [ ] Branch is `feature/*` or `chore/*` off `develop`, scoped to a single issue.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] New/changed behavior is covered by tests; coverage stays above the CI gate.
- [ ] Every "Validation / test checks" item on the issue is satisfied, and the PR says how.
- [ ] The PR description links its issue (e.g. `Closes #123`).
- [ ] No secrets, credentials, or client data in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

## Review

The repository owner is the sole code owner and reviews every PR. Review comments are binding:
the ruleset requires every review thread to be resolved before a merge is possible. Push fixes to
the same branch; an approval is dismissed automatically when new commits land.

## Definition of done

Code + tests, pre-commit clean, CI green, PR links its issue, reviewed and squash-merged into
`develop`.
