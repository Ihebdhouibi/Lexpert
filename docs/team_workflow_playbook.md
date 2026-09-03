# Lexpert — Team Workflow Setup Playbook

**Audience:** the Claude Code session working in `Ihebdhouibi/Lexpert`.

**Purpose:** stand up a terminal-driven collaboration mechanism so that the repository owner
(acting as technical lead) can create labels, milestones and issues from a Claude Code session,
and review and squash-merge a collaborator's pull requests from the same session — without
leaving the terminal.

**How to use this file:** copy it into the repository at `docs/team_workflow_playbook.md` and work
through Parts 0-8 in order. Each part is runnable. Part 9 is a verification checklist; run it
before declaring the setup done. Part 10 lists the known traps.

This playbook is transposed from a working setup in another repository
(`Ihebdhouibi/Arabic-Islamic-Rag`), which has been running this mechanism in production. Where a
choice was project-specific, it has been replaced with a procedure for deriving the right answer
for Lexpert rather than a value to copy.

---

## Roles

| Person | Role | What they do |
| --- | --- | --- |
| `Ihebdhouibi` (owner) | Technical lead | Architecture, backlog, issue creation, PR review, merge |
| `OmaymaAbdessamed` | Implementer | Picks up issues, one branch per issue, opens PRs into `develop` |

This division drives two decisions later: the owner is the sole CODEOWNER (Part 3.3), and the
review requirement is set so the collaborator's PRs always get reviewed while the lead is not
blocked on their own (Part 7).

**Use the login `OmaymaAbdessamed` verbatim in every command.** The account's display name is
spelled differently ("Oumaima Abdessamed"), and `gh` matches on the login only — the display-name
spelling will silently fail to resolve.

---

## Observed starting state

Checked against the live repository. Confirm it still holds before starting; if it has moved on,
adapt rather than assume.

| Property | Value |
| --- | --- |
| Repository | `Ihebdhouibi/Lexpert` |
| Visibility | **Public** |
| Default branch | `main` |
| Branches | `main` only |
| Contents | `README.md` (20 bytes) — effectively greenfield |
| Labels | The 9 GitHub defaults only |
| Milestones | None |
| Rulesets | None |
| Collaborators | Owner only (`admin`) |
| Actions | Enabled, all actions allowed |

**On visibility:** the repository was switched from private to public specifically so that
repository rulesets would work. On the GitHub Free plan, rulesets and branch protection are not
available on private repositories — the API returns
`403 Upgrade to GitHub Pro or make this repository public`. If the repo is ever made private
again, Part 7 stops working and every protection listed there silently disappears. In that case
either upgrade to GitHub Pro or accept that the branch model is convention-only. Flag this to the
owner before changing visibility.

Because the repo is public, also make sure no secrets, client data or credentials are committed.
Add `.env` to `.gitignore` in the very first commit and ship `.env.example` instead.

---

## Two rules that apply to everything you write

Non-negotiable, carried over from the source project:

1. **No AI attribution.** Never write "Generated with Claude", "Co-authored-by: Claude",
   "Co-authored-by: Copilot" or anything similar in commit messages, PR descriptions, issue
   bodies, code, or comments. Describe the change only.
2. **No emojis.** Anywhere: code, comments, commit messages, PR titles and descriptions, issue
   text, documentation.

Both go into `CLAUDE.md` (Part 3.1) so future sessions inherit them.

## A note on shell syntax

The owner's default shell is PowerShell on Windows 11; Git Bash is also available. Commands here
are written to work in both: any argument containing spaces or `&` is quoted **as a whole**
(`-f "title=M0 - Foundation"`, not `-f title="M0 - Foundation"`), because PowerShell splits the
unquoted form into separate tokens. For multi-line bodies, write a file and pass `--body-file` —
never a Bash heredoc.

---

## Part 0 — Confirm the stack before building the enforcement layer

The owner's expectation is **React (frontend) + Python (backend)**, but explicitly deferred to
whatever this session has already decided. Resolve this first, because Part 4 (tooling, hooks, CI)
and Part 5.1 (labels) both depend on the answer.

```bash
# What is actually in the repo right now
ls -a
cat README.md
git log --oneline -20
```

Then pick the case that applies:

- **Nothing decided yet, and React + Python is right** — use Part 4 as written. It assumes a
  two-app monorepo.
- **A stack was already chosen in this session or already scaffolded** — keep it. Apply Part 4's
  *structure* (hooks that run on commit, a `lint` job and a `test` job per app, the same commit
  convention) with that stack's tools substituted. Tell the owner what you substituted and why.
- **Single-stack, Python only or React only** — drop the unused half of Part 4 and reduce the CI
  jobs and required status checks (Part 7) to match. Do not leave a required check for a job that
  does not exist; it blocks every PR forever.

Assumed monorepo layout for the rest of this document:

```
Lexpert/
  apps/
    web/                 # React + TypeScript (Vite)
    api/                 # Python (FastAPI), package under apps/api/src/lexpert_api/
  docs/
    implementation/      # plan + issue backlog (Part 6)
    technical_docs/      # design docs
  .github/
```

If you choose a different layout, keep the principle: each app owns its own dependency manifest
and its own lint/test entry points, so CI can run them independently.

---

## Part 1 — Preflight

Run these checks first. Do not proceed past a failure.

```bash
gh --version
gh auth status
gh repo view Ihebdhouibi/Lexpert --json nameWithOwner,visibility,defaultBranchRef
git config user.name
git config user.email
```

### Token scopes — check this before touching CI

`gh auth status` prints the token's scopes. You need:

- `repo` — issues, labels, milestones, pull requests, rulesets, repo settings.
- `workflow` — **required to push any change under `.github/workflows/`.**

The owner's token in the source project had `gist, read:org, repo` and **no `workflow` scope**.
With that token, `git push` is rejected the moment a commit touches a workflow file, with
`refusing to allow an OAuth App to create or update workflow`. Check for it explicitly:

```bash
gh auth status 2>&1 | grep -i "token scopes"
```

If `workflow` is missing, stop and have the owner run:

```bash
gh auth refresh -h github.com -s repo,workflow
```

That opens a browser flow. If this session cannot run an interactive flow, report the blocker
rather than working around it — do not commit the CI file and hope, and do not try to create the
workflow through the API instead.

### Collaborator access

Invite the collaborator once, with write permission:

```bash
gh api -X PUT "repos/Ihebdhouibi/Lexpert/collaborators/OmaymaAbdessamed" -f permission=push
```

Verify the pending invitation, and the permission level after they accept:

```bash
gh api "repos/Ihebdhouibi/Lexpert/invitations" -q '.[] | "\(.invitee.login)\t\(.permissions)"'
gh api "repos/Ihebdhouibi/Lexpert/collaborators/OmaymaAbdessamed/permission" -q .permission
```

`push` is the correct level. Do **not** grant `admin`: the ruleset in Part 7 gives admins a
standing bypass of every branch protection, so an admin collaborator could push straight to
`main`. Write access plus the ruleset is exactly the combination that makes the PR flow
mandatory for them and optional for the lead.

The invite is sent to the login `OmaymaAbdessamed` (verified to exist). It stays pending until she
accepts, and the `collaborators/.../permission` call returns `none` until then — that is expected,
not a failure. Do not re-send the invite in a loop; ask the owner to nudge her instead.

---

## Part 2 — Branch model

Three long-lived branches, each fed by the one below it:

```
main  <-  stable-testing  <-  develop  <-  feature/*  |  chore/*
```

- `main` — protected; release.
- `stable-testing` — protected; release candidate.
- `develop` — protected; integration branch and the **default branch**. All feature work targets
  this branch.
- `feature/*` / `chore/*` — short-lived, one per issue.

Rules the rest of the setup enforces mechanically:

- One issue = one branch = one PR into `develop`. Squash-merge.
- No direct commits to `main`, `stable-testing` or `develop`.
- A PR merges only when CI is green and it has an approving review.

The repo currently has only `main`. Create the other two from it and switch the default:

```bash
git clone https://github.com/Ihebdhouibi/Lexpert.git
cd Lexpert

git checkout main
git checkout -b stable-testing main
git push -u origin stable-testing

git checkout -b develop stable-testing
git push -u origin develop

gh repo edit --default-branch develop
```

Setting `develop` as default matters more than it looks: it makes `gh pr create` target `develop`
automatically, so a mis-targeted PR into `main` becomes something you have to do deliberately
rather than by accident.

Restrict merging to squash only, and delete branches on merge:

```bash
gh repo edit --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false --delete-branch-on-merge
```

---

## Part 3 — Governance documents

Three files. They are what a future Claude session reads to learn the conventions, so they must be
committed, not left in chat history.

### 3.1 `CLAUDE.md` (repository root)

Loaded automatically by Claude Code. Fill in the Project section from what Lexpert actually is;
keep Rules, Branching and Definition-of-done structurally as they are.

~~~markdown
# CLAUDE.md — Working agreement for Lexpert

Guidance for AI coding assistants (Claude Code, Copilot, etc.) and human contributors in this
repo. Read this before making changes.

## Project

<One paragraph: what Lexpert is and what is currently being built.>

- Design docs: `docs/technical_docs/`
- Implementation plan + issue backlog: `docs/implementation/`

Stack: React + TypeScript (`apps/web`); Python <version> + FastAPI (`apps/api`); <datastore>.

## Rules (must follow)

1. **No AI attribution.** Never add "Generated with Claude", "Co-authored-by: Claude", Copilot, or
   any similar mention in commit messages, PR descriptions, or code. Describe the change only.
2. **No emojis.** Anywhere: code, comments, commit messages, PR descriptions, docs.
3. **Always end a task with a summary**, covering: What was done, Why, What to expect, and Edge
   cases to handle.
4. **Commit convention:** `<type>(<scope>): <short imperative subject>`. Types: `feat`, `chore`,
   `docs`, `tests`, `bug`, `ci`. Scope is optional and is one of `web`, `api`, `infra`. Keep the
   subject short; add a body only when needed.
5. **Pre-commit must pass** before every commit (ruff + mypy for the API, eslint + prettier for
   the web app, hygiene hooks, conventional commit-msg). Do not bypass with `--no-verify`.
6. **The repository is public.** Never commit secrets, credentials, client data, or real case
   material. Configuration comes from environment variables; `.env` is git-ignored and
   `.env.example` is the committed template.

## Branching & PRs

- Model: `main` (protected, release) <- `stable-testing` (release candidate) <- `develop`
  (integration) <- `feature/*` or `chore/*` (one branch per issue).
- One issue = one branch = one PR into `develop`. Squash-merge. No direct commits to protected
  branches.
- Use the terminal git CLI for all version-control operations.

## Definition of done

Code + tests, pre-commit clean, CI green, PR links its issue, reviewed.
~~~

Rule 3 is worth keeping verbatim: the end-of-task summary is what makes an assistant's work
reviewable without re-reading the whole diff. Rule 6 is new for Lexpert and exists because the
repo is public.

### 3.2 `CONTRIBUTING.md` (repository root)

The human-facing version. The collaborator reads it once; the PR checklist is the operative part.

~~~markdown
# Contributing to Lexpert

Thanks for contributing. This guide covers the branch model, commit style, local setup, and the
checklist every change must pass.

## Branch model

```
main  <-  stable-testing  <-  develop  <-  feature/*  |  chore/*
```

- `main` — protected, release.
- `stable-testing` — release candidate.
- `develop` — integration branch; all feature work merges here.
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

This is a public repository: never commit secrets, credentials, or client data.

## Local setup

Requires Python 3.11 and Node 20 (or newer LTS).

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

Run the checks the way CI runs them:

```bash
cd apps/api && ruff check . && ruff format --check . && mypy src && pytest
cd apps/web && npm run lint && npx tsc --noEmit && npm test
```

## Working on an issue

```bash
git checkout develop && git pull
git checkout -b feature/<short-slug>     # branch name is given on the issue
# ... work, committing in conventional-commit style ...
git push -u origin feature/<short-slug>
gh pr create --base develop --fill
```

## Pull request checklist

Before opening a PR into `develop`:

- [ ] Branch is `feature/*` or `chore/*` off `develop`, scoped to a single issue.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `tsc --noEmit` clean, tests pass.
- [ ] New/changed behavior is covered by tests; coverage stays above the CI gate.
- [ ] The PR description links its issue (e.g. `Closes #123`).
- [ ] No secrets, credentials, or client data in the diff.

## Definition of done

Code + tests, pre-commit clean, CI green, PR links its issue, reviewed and squash-merged into
`develop`.
~~~

### 3.3 `.github/CODEOWNERS`

**Do not skip this.** The ruleset in Part 7 sets `require_code_owner_review: true`. Without a
CODEOWNERS file that rule matches nothing and silently does not do what it appears to do. With it,
every PR automatically requests review from the owner — which is precisely the technical-lead
workflow being set up.

```
# Default owner for everything in this repository.
* @Ihebdhouibi
```

Verify GitHub parsed it (`0` means valid):

```bash
gh api "repos/:owner/:repo/codeowners/errors" -q '.errors | length'
```

If the split later justifies it, narrow it per area, for example `/apps/web/ @Ihebdhouibi` plus a
second owner for the API. With two people, the single default line is enough.

---

## Part 4 — Enforcement layer (React + Python)

Three things make the standards mechanical rather than aspirational: tool configuration, git
hooks, and CI. Hooks catch problems before a commit exists; CI catches them before a merge.

Only apply this part after Part 0 has confirmed the stack.

### 4.1 Python — `apps/api/pyproject.toml`

```toml
[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "pytest-cov>=5.0",
  "ruff>=0.16",
  "mypy>=1.11",
  "httpx>=0.27",
]

[tool.ruff]
line-length = 100
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src", "tests"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.coverage.run]
source = ["lexpert_api"]

[tool.coverage.report]
show_missing = true
fail_under = 70
exclude_also = [
  "if TYPE_CHECKING:",
  "@(abc\\.)?abstractmethod",
]
```

Two values need real substitution: `source = ["lexpert_api"]` must be the actual importable
package name, and `fail_under` is the coverage gate. It is set to `70` here rather than the source
project's `85` because a gate that is red on the first PR gets disabled instead of respected.
Start where the project can actually hold, then ratchet it up in a `chore:` PR.

`mypy strict = true` on a greenfield codebase is nearly free; retrofitting it later is not. Keep
it.

### 4.2 React / TypeScript — `apps/web`

Use Vite with the React + TypeScript template. The scripts CI depends on are `lint`, `test`, and a
type-check:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "typecheck": "tsc --noEmit",
    "lint": "eslint .",
    "format:check": "prettier --check .",
    "test": "vitest run --coverage"
  }
}
```

Pin a Node version in `.nvmrc` (for example `20`) and commit `package-lock.json` so CI's `npm ci`
is reproducible. Keep ESLint on the flat-config format (`eslint.config.js`) with
`typescript-eslint` and `eslint-plugin-react-hooks`; keep Prettier as the sole formatter and let
ESLint handle only correctness rules, so the two never fight.

If the session prefers lower friction, **Biome** replaces ESLint + Prettier with one binary and one
config and has a first-class pre-commit hook. Either is fine; pick one and say which.

### 4.3 `.pre-commit-config.yaml` (repository root)

One hook manager for both languages. Running two (pre-commit plus husky/lint-staged) means two
things competing for `.git/hooks`; do not do that.

```yaml
# Pre-commit hooks for Lexpert.
# Install once:  pre-commit install && pre-commit install --hook-type commit-msg
# Run manually:  pre-commit run --all-files
minimum_pre_commit_version: "3.5.0"
default_install_hook_types: [pre-commit, commit-msg]

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
        args: [--markdown-linebreak-ext=md]  # preserve markdown hard line breaks
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: [--maxkb=1024]
      - id: check-merge-conflict
      - id: mixed-line-ending
        args: [--fix=lf]
      - id: detect-private-key          # public repo: cheap insurance

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.1
    hooks:
      - id: ruff
        args: [--fix]
        files: ^apps/api/
      - id: ruff-format
        files: ^apps/api/

  - repo: local
    hooks:
      - id: eslint
        name: eslint
        entry: npm --prefix apps/web run lint --
        language: system
        files: ^apps/web/.*\.(ts|tsx|js|jsx)$
        pass_filenames: false
      - id: prettier
        name: prettier
        entry: npx --prefix apps/web prettier --write
        language: system
        files: ^apps/web/.*\.(ts|tsx|js|jsx|css|json|md)$

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, chore, docs, tests, bug, ci]
```

Three things that matter here:

- `default_install_hook_types` — without it, `pre-commit install` wires only the `pre-commit`
  stage and the commit-message check never runs.
- The `files:` filters — without them, the Python hooks try to run on the React app and vice
  versa.
- The `args:` on `conventional-pre-commit` are the **allowed commit types**. They must match
  `CLAUDE.md` rule 4 and `CONTRIBUTING.md`. Change one, change all three.

Once per clone:

```bash
pre-commit install && pre-commit install --hook-type commit-msg
pre-commit run --all-files
```

The first `run --all-files` reformats existing files. Commit that on its own as
`chore: apply pre-commit formatting`, so the noise does not land in a feature PR.

### 4.4 `.github/workflows/ci.yml`

Job names are load-bearing: they are the exact strings the ruleset in Part 7 requires as status
checks. Rename a job and you must update the ruleset in the same change, or merges block forever
on a check that never reports.

```yaml
name: CI

on:
  pull_request:
    branches: [develop, stable-testing, main]
  push:
    branches: [develop, stable-testing, main]

jobs:
  lint-api:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/api
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: apps/api/pyproject.toml
      - name: Install
        run: pip install -e ".[dev]"
      - name: Ruff lint
        run: ruff check .
      - name: Ruff format
        run: ruff format --check .
      - name: Mypy
        run: mypy src

  test-api:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/api
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: apps/api/pyproject.toml
      - name: Install
        run: pip install -e ".[dev]"
      - name: Pytest
        run: pytest -q --cov=lexpert_api --cov-report=term-missing
      - name: Coverage summary
        if: always()
        run: |
          echo "### API coverage" >> "$GITHUB_STEP_SUMMARY"
          coverage report >> "$GITHUB_STEP_SUMMARY"

  lint-web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: apps/web/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run format:check
      - run: npm run typecheck

  test-web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: apps/web/package-lock.json
      - run: npm ci
      - run: npm test
```

**Do not add `paths:` filters to this workflow.** It is tempting to skip `test-web` when only the
API changed, but a required status check that is skipped by a path filter never reports, and under
the strict policy in Part 7 the PR stays blocked forever with a confusing "Expected" state. On a
project this size, running all four jobs every time costs a couple of minutes and avoids the whole
problem. If job-skipping becomes genuinely necessary later, the correct pattern is a
`dorny/paths-filter` gate job that always runs and reports, with the heavy jobs conditioned on its
output.

If the API needs backing services (Postgres, Redis), add them as `services:` on `test-api` with
health checks and expose addresses through `env:`. Write the integration tests to **skip
automatically when the service is unreachable**, so a local `pytest` without Docker still passes
while CI runs the full set. That pattern is used in the source project and is worth reproducing:
it keeps the local loop fast without weakening CI.

**Push this file and let CI run once on `develop` before creating the ruleset in Part 7.** A
required check that has never reported holds every PR open.

---

## Part 5 — GitHub project scaffolding

This is the part that makes issue and milestone management possible from the terminal.

### 5.1 Labels

The nine GitHub defaults are already on the repo. Add a layer on top so any issue can be filtered
by **the part of the system it touches**.

Do not copy a label set from another project. The source project's labels (`embeddings`,
`retrieval`, `chunking`, `generation`, `eval`) describe a RAG pipeline and would be meaningless
here. Derive Lexpert's set instead, using this test:

> A label is worth creating if it answers: *"which part of the system do I need to understand in
> order to review this PR?"*

And these constraints:

- Aim for **6 to 10** custom labels. Past that, nobody applies them consistently and filtering
  stops being reliable.
- Do **not** create labels that duplicate other GitHub fields: no phase labels (that is what
  milestones are for), no size or priority labels unless the owner asks (those belong in the
  issue body), no `in-progress` (that is assignment plus an open PR).
- Prefer nouns naming a subsystem over adjectives naming a quality.

A sound starting set for a React + Python application, assuming nothing yet about Lexpert's
domain:

```bash
# Layer labels - which app/tier the work lives in
gh label create frontend --color 1D76DB --description "React app (apps/web)"
gh label create backend  --color 0E8A16 --description "Python service (apps/api)"
gh label create api      --color F9D0C4 --description "HTTP contract between web and api"
gh label create database --color 5319E7 --description "Schema, migrations, data access"
gh label create auth     --color B60205 --description "Authentication and authorization"

# Cross-cutting - carry these over unchanged
gh label create infra            --color 1D76DB --description "Project foundation / infrastructure"
gh label create ci               --color 5319E7 --description "CI/CD"
gh label create docs             --color C5DEF5 --description "Documentation"
gh label create test             --color BFD4F2 --description "Tests"
gh label create good-first-issue --color 7057FF --description "Good first issue"
```

Then, **once the domain modules are actually known** — after the plan document in Part 6 exists —
add three to five domain labels naming Lexpert's real feature areas, and tell the owner which ones
you added and why. Do not invent them from the project's name; derive them from the plan document
or ask.

`gh label create` fails if a label exists; add `--force` to make the script re-runnable.

Resolve the duplicate-looking pair before creating issues, or filters will miss things:

```bash
gh label delete "good first issue" --yes    # keep the hyphenated one
gh label list --limit 100
```

### 5.2 Milestones

One milestone per phase, each with a description stating its **exit condition** — not a
restatement of the title. That is what makes "is M2 done?" a question with an answer.

`gh` has no `milestone create` command, so use the API. Note the quoting: the whole `key=value`
pair sits inside the quotes, which PowerShell requires.

Lexpert's phases must come from its own plan document (Part 6). The skeleton below is a shape, not
a backlog — `M0` and `M8` are genuinely reusable, the middle is placeholder:

```bash
gh api "repos/:owner/:repo/milestones" -f "title=M0 - Foundation & infra"     -f "description=Both apps build, hooks installed, CI green on develop"
gh api "repos/:owner/:repo/milestones" -f "title=M1 - Data model & storage"   -f "description=Schema and migrations in place; data access layer covered by tests"
gh api "repos/:owner/:repo/milestones" -f "title=M2 - Auth & accounts"        -f "description=<exit condition>"
gh api "repos/:owner/:repo/milestones" -f "title=M3 - <core domain feature>"  -f "description=<exit condition>"
gh api "repos/:owner/:repo/milestones" -f "title=M4 - <feature>"              -f "description=<exit condition>"
gh api "repos/:owner/:repo/milestones" -f "title=M5 - Web UI"                 -f "description=<exit condition>"
gh api "repos/:owner/:repo/milestones" -f "title=M6 - API surface"            -f "description=Documented endpoints + response schemas, contract tests"
gh api "repos/:owner/:repo/milestones" -f "title=M7 - Hardening & CI/CD"      -f "description=Coverage gate raised, smoke tests, deploy pipeline"
```

The `M<n> - <name>` prefix is deliberate: it sorts correctly and lets issue titles carry `M2-04`
style task ids that map back to the backlog document.

List them with their numbers, and set due dates only if the owner wants them:

```bash
gh api "repos/:owner/:repo/milestones" --paginate -q '.[] | "\(.number)\t\(.title)\t\(.state)"'
gh api -X PATCH "repos/:owner/:repo/milestones/1" -f "due_on=2026-10-31T23:59:59Z"
```

### 5.3 Issue templates

`.github/ISSUE_TEMPLATE/bug_report.yml`:

```yaml
name: Bug report
description: Report a defect.
labels: [bug]
body:
  - type: textarea
    id: what-happened
    attributes:
      label: What happened
      description: A clear description of the bug and what you expected instead.
    validations:
      required: true
  - type: textarea
    id: repro
    attributes:
      label: Steps to reproduce
      description: Commands, inputs, and config needed to reproduce.
    validations:
      required: true
  - type: dropdown
    id: area
    attributes:
      label: Area
      options: [frontend, backend, both, not sure]
    validations:
      required: true
  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: OS, browser, Node/Python version, and which services were running.
    validations:
      required: false
```

`.github/ISSUE_TEMPLATE/feature_request.yml`:

```yaml
name: Feature request
description: Propose a unit of work (milestone task or enhancement).
labels: [enhancement]
body:
  - type: textarea
    id: goal
    attributes:
      label: Goal
      description: What should exist and why.
    validations:
      required: true
  - type: textarea
    id: done-when
    attributes:
      label: Done when
      description: Acceptance criteria (what must be true to close this).
    validations:
      required: true
  - type: input
    id: depends-on
    attributes:
      label: Depends on
      description: Other issues this depends on (optional).
    validations:
      required: false
```

**Done when** is the important field. Every issue carrying explicit acceptance criteria is what
lets the lead review a PR against a stated bar instead of a vague intent.

### 5.4 Pull request template

`.github/pull_request_template.md`:

```markdown
## Summary

<!-- What does this change do and why? Keep it concise. -->

Closes #

## Changes

<!-- Bullet the key changes. -->

-

## Checklist

- [ ] Branch is `feature/*` or `chore/*` off `develop`, scoped to one issue
- [ ] `pre-commit run --all-files` passes
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass
- [ ] Tests cover the change; coverage stays above the CI gate
- [ ] No secrets, credentials, or client data in the diff
```

The bare `Closes #` is intentional: it prompts the author for the issue number, and the keyword
auto-closes the issue on merge, which keeps milestone counters honest without manual grooming.

Commit Parts 3-5 on a `chore/*` branch and open the first PR into `develop`. That first PR is
also the smoke test for the whole setup.

---

## Part 6 — The plan-to-backlog pipeline

This is the mechanism that makes bulk issue creation from a Claude session practical, and it is
the piece most likely to be skipped. Do not skip it. It is also the input to the domain labels
deferred in Part 5.1 and the milestone names in Part 5.2.

Two documents under `docs/implementation/`:

**`<module>_plan.md`** — the design and phasing narrative: what is being built, in what order, and
why. Prose, not a checklist. The technical lead writes or approves this.

**`<module>_issues.md`** — the backlog. Every entry is pre-scoped to exactly one PR and carries a
fixed set of fields:

```markdown
# Lexpert — Issue Backlog

> Companion to [lexpert_plan.md](lexpert_plan.md). Every issue is scoped to one PR. Labels,
> dependencies, size (S <= half-day, M ~ 1-2 days, L ~ 3+ days), and a suggested branch name are
> given. A `gh` bulk-create script is in the appendix.
>
> **Nothing here is implemented yet — this is the proposed backlog, awaiting approval.**

**Legend — labels:** `frontend` `backend` `api` `database` `auth` `infra` `ci` `docs` `test`
`good-first-issue`

---

## M0 — Foundation & infra

### M0-01 - Monorepo scaffolding
- **Labels:** infra - **Size:** S - **Depends on:** — - **Branch:** `feature/m0-scaffolding`
- Create `apps/web` (Vite React TS) and `apps/api` (Python package under `src/`), plus `tests/`
  roots for both. Pin Node and Python versions.
- **Done when:** `npm ci && npm run build` succeeds in `apps/web`; `pip install -e ".[dev]"` and
  an empty `pytest` run succeed in `apps/api`.

### M0-02 - Config & secrets management
- **Labels:** infra - backend - **Size:** S - **Depends on:** M0-01 - **Branch:** `feature/m0-config`
- `pydantic-settings` config for the API; Vite env handling for the web app. Ship `.env.example`;
  keep `.env` git-ignored.
- **Done when:** config loads and validates in both apps; one unit test each.
```

Five fields per issue, and each earns its place: **Labels** drive filtering, **Size** stops
oversized issues from being created, **Depends on** gives a work order, **Branch** means two
people never invent different names for the same work, and **Done when** is the review bar.

The `M<n>-<nn>` task id is the join key between this document, the milestone, and the issue title.

### 6.1 Get approval before creating issues

Write the backlog document first, commit it, and have the owner read it. Creating thirty issues
from an unapproved backlog produces thirty issues that then have to be edited or closed. The
`**Nothing here is implemented yet**` banner exists for exactly this reason.

This matters more than usual here: the owner is playing technical lead, so the backlog *is* the
artifact they are meant to review. Do not skip ahead to creating issues to seem productive.

### 6.2 Bulk-create the issues

Append the script to the backlog document as an appendix so the mapping stays reproducible. One
`gh issue create` per issue, with title, body, labels and milestone:

```bash
gh issue create \
  --title "M0-01 Monorepo scaffolding" \
  --label infra \
  --milestone "M0 - Foundation & infra" \
  --body-file .github/issue-bodies/m0-01.md
```

Points that matter:

- `--milestone` takes the milestone **title**, matched exactly. A typo creates nothing and returns
  an error, so read the output rather than assuming success.
- Multiple labels: repeat the flag (`--label infra --label ci`), do not comma-separate.
- Put `Size`, `Depends on`, `Branch` and `Done when` in the body. They are what the collaborator
  reads to start work without asking a question.
- Prefer `--body-file` over `--body` for anything multi-line. It sidesteps every shell-quoting
  problem, which on PowerShell is not a theoretical concern.

Verify the result, then hand the owner the list:

```bash
gh issue list --limit 100 --json number,title,labels,milestone \
  -q '.[] | "\(.number)\t\(.milestone.title)\t\(.title)"'
```

### 6.3 Assigning work

```bash
gh issue edit 12 --add-assignee OmaymaAbdessamed
gh issue list --assignee OmaymaAbdessamed --state open
gh issue list --milestone "M1 - Data model & storage" --state open
```

---

## Part 7 — Branch protection (repository ruleset)

Use a **repository ruleset**, not classic branch protection: one ruleset covers all three
protected branches through a single ref-name pattern list.

Two preconditions:

1. **The repository must be public** (or on GitHub Pro). It is public as of this writing. On the
   Free plan with a private repo, `POST /repos/{owner}/{repo}/rulesets` returns
   `403 Upgrade to GitHub Pro or make this repository public`, and nothing in this part works.
2. **CI must have reported `lint-api`, `test-api`, `lint-web` and `test-web` at least once**
   (Part 4.4). Required checks that have never run block every PR.

Write the payload to a file — this avoids all shell-quoting issues and gives you something
versioned and reviewable.

`.github/ruleset.json`:

```json
{
  "name": "protected-branches",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": [
        "refs/heads/main",
        "refs/heads/stable-testing",
        "refs/heads/develop"
      ],
      "exclude": []
    }
  },
  "bypass_actors": [
    {
      "actor_id": 5,
      "actor_type": "RepositoryRole",
      "bypass_mode": "always"
    }
  ],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "required_reviewers": [],
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "lint-api" },
          { "context": "test-api" },
          { "context": "lint-web" },
          { "context": "test-web" }
        ]
      }
    }
  ]
}
```

Apply, inspect, update:

```bash
gh api -X POST "repos/:owner/:repo/rulesets" --input .github/ruleset.json

gh api "repos/:owner/:repo/rulesets" -q '.[] | "\(.id)\t\(.name)\t\(.enforcement)"'
gh api "repos/:owner/:repo/rulesets/RULESET_ID"

gh api -X PUT "repos/:owner/:repo/rulesets/RULESET_ID" --input .github/ruleset.json
```

### What each rule buys

- `deletion` / `non_fast_forward` — protected branches cannot be deleted or force-pushed. No
  downside; always on.
- `required_status_checks` with `strict_required_status_checks_policy: true` — the branch must be
  **up to date with `develop`** before merging, and all four checks must pass. The strict flag is
  what prevents "green in isolation, broken after merge".
- `required_review_thread_resolution: true` — every review comment must be resolved before merge.
  For a technical lead reviewing another person's work, this is the single most valuable rule
  here: it makes review comments binding rather than advisory.
- `dismiss_stale_reviews_on_push: true` — an approval is void once new commits land.
- `require_code_owner_review: true` — combined with the CODEOWNERS file from Part 3.3, review is
  automatically requested from the owner on every PR.
- `allowed_merge_methods: ["squash"]` — one issue produces exactly one commit on `develop`. This
  narrows the source project's `["merge", "squash", "rebase"]` to match the stated convention.

### On `required_approving_review_count: 1` and the admin bypass

This combination is deliberate for the lead/implementer split:

- The collaborator has `push` access and **no** bypass, so their PRs genuinely require the owner's
  approval, green CI, and resolved threads before merging. That is the review gate.
- `actor_id: 5` is the built-in `admin` repository role. With `bypass_mode: "always"`, the owner
  can merge their own PRs without waiting for an approval they cannot give themselves, and can
  unblock an emergency.

The bypass is a real hole — it is what makes the setup workable for one reviewer, but the owner
should still open PRs rather than pushing to `develop` directly, since nothing now stops them. If
the owner would rather be held to the same bar, remove the `bypass_actors` array entirely and
accept being blocked when the collaborator is unavailable.

Confirm which of the two the owner wants; do not assume. Then verify the bypass resolves to what
you intended:

```bash
gh api "repos/:owner/:repo/rulesets/RULESET_ID" -q '.bypass_actors'
```

---

## Part 8 — The daily loop

### 8.1 Owner: driving the backlog from a Claude session

```bash
# What is open, and where does it sit
gh issue list --state open --limit 100
gh issue list --milestone "M1 - Data model & storage" --state open
gh issue list --label frontend --state open

# Create, retitle, relabel, re-milestone, close
gh issue create --title "..." --label backend --milestone "M1 - Data model & storage" --body-file body.md
gh issue edit 12 --add-label ci --milestone "M7 - Hardening & CI/CD"
gh issue edit 12 --add-assignee OmaymaAbdessamed
gh issue comment 12 --body "Blocked on #9; picking this up after that merges."
gh issue close 12 --reason completed

# Milestone progress
gh api "repos/:owner/:repo/milestones" -q '.[] | "\(.title)\topen:\(.open_issues)\tclosed:\(.closed_issues)"'
```

### 8.2 Collaborator: one issue, one branch, one PR

```bash
git checkout develop && git pull
git checkout -b feature/m1-user-model     # branch name from the issue
# ... work ...
git push -u origin feature/m1-user-model
gh pr create --base develop --title "feat(api): add user model and migration" --body "Closes #12"
```

### 8.3 Owner: reviewing and merging from the terminal

```bash
# Queue, with author and branch
gh pr list --state open --json number,title,author,headRefName \
  -q '.[] | "\(.number)\t\(.author.login)\t\(.headRefName)\t\(.title)"'

# Read the PR
gh pr view 34                      # description, checks, reviews
gh pr view 34 --comments           # discussion so far
gh pr diff 34                      # full diff
gh pr checks 34                    # CI status per check

# Check it out locally and actually run it
gh pr checkout 34
pre-commit run --all-files
cd apps/api && mypy src && pytest && cd ../..
cd apps/web && npm ci && npm run typecheck && npm test && cd ../..
```

Reviewing. Prefer inline comments on specific lines over one long summary comment — they anchor to
the code, and with `required_review_thread_resolution` each one must be resolved before merge:

```bash
# Request changes with a summary
gh pr review 34 --request-changes --body "Two issues inline; see comments."

# Approve
gh pr review 34 --approve --body "Matches the Done-when criteria on #12."

# Inline comment on a specific line (REST API; gh has no first-class command for this)
gh api -X POST "repos/:owner/:repo/pulls/34/comments" \
  -f "body=This drops the error case - add a test for the empty-input path." \
  -f "commit_id=$(gh pr view 34 --json headRefOid -q .headRefOid)" \
  -f "path=apps/api/src/lexpert_api/users.py" \
  -F "line=42" \
  -f "side=RIGHT"
```

Merging:

```bash
gh pr merge 34 --squash --delete-branch
```

Before merging, confirm the PR body contains `Closes #<n>` — that is what closes the issue and
keeps the milestone counters honest:

```bash
gh pr view 34 --json body -q .body | grep -i "closes #"
```

Promotion up the chain, when a set of changes on `develop` is ready:

```bash
gh pr create --base stable-testing --head develop --title "chore: promote develop to stable-testing"
gh pr create --base main --head stable-testing --title "chore: release"
```

### 8.4 Reduce permission prompts

Claude Code prompts before each `gh` write. Pre-allow the routine ones in
`.claude/settings.local.json` (git-ignored, per-machine) or `.claude/settings.json` (committed,
shared with the collaborator):

```json
{
  "permissions": {
    "allow": [
      "Bash(gh pr merge *)",
      "Bash(gh pr view *)",
      "Bash(gh pr diff *)",
      "Bash(gh pr list *)",
      "Bash(gh pr checks *)",
      "Bash(gh issue list *)",
      "Bash(gh issue view *)",
      "Bash(gh label list *)"
    ]
  }
}
```

The source project allowed only `Bash(gh pr merge *)`. Keep read-only commands and `pr merge`
allowed; leave `gh pr review`, `gh issue create` and anything touching rulesets prompting, since
those are outward-facing or hard to reverse.

Add `.claude/settings.local.json` to `.gitignore` if it is not already there.

---

## Part 9 — Verification checklist

Run every one of these. Each maps to a step above.

```bash
# Branches and default
git ls-remote --heads origin | grep -E "main|stable-testing|develop"
gh repo view --json defaultBranchRef -q .defaultBranchRef.name        # -> develop

# Visibility (rulesets depend on it)
gh repo view --json visibility -q .visibility                         # -> PUBLIC

# Merge settings
gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed,deleteBranchOnMerge

# Governance files present and valid
ls CLAUDE.md CONTRIBUTING.md .github/CODEOWNERS
gh api "repos/:owner/:repo/codeowners/errors" -q '.errors | length'   # -> 0

# Hooks work
pre-commit run --all-files
git commit --allow-empty -m "bad message"                             # must be REJECTED
git commit --allow-empty -m "chore: verify commit-msg hook"           # must be ACCEPTED

# CI reported all four contexts at least once
gh run list --limit 5
gh api "repos/:owner/:repo/commits/develop/status" -q '.statuses[].context'

# Scaffolding
gh label list --limit 100
gh api "repos/:owner/:repo/milestones" -q '.[] | "\(.number)\t\(.title)"'
ls .github/ISSUE_TEMPLATE/ .github/pull_request_template.md

# Ruleset active
gh api "repos/:owner/:repo/rulesets" -q '.[] | "\(.id)\t\(.name)\t\(.enforcement)"'

# Collaborator access
gh api "repos/:owner/:repo/collaborators/OmaymaAbdessamed/permission" -q .permission   # -> push

# Public-repo hygiene
git log --all --full-history -- .env                                  # must be empty
grep -rn "SECRET\|PASSWORD\|API_KEY" --include="*.env*" .             # only .env.example
```

Then the real end-to-end test, which is the only proof the mechanism works:

1. Create one issue from the terminal with a label and milestone.
2. Branch, make a trivial change, commit with a conventional message, push, open a PR with
   `Closes #<n>`.
3. Confirm CI runs and the PR **cannot** merge before checks pass and review is given.
4. Approve, `gh pr merge --squash --delete-branch`.
5. Confirm the issue auto-closed and the milestone counter moved.

If step 3 lets you merge with red checks, the ruleset is not matching. Check the ref names in
`conditions.ref_name.include` and that the check contexts match the CI job names exactly.

Ideally run step 2 as the collaborator, not the owner — the owner has the admin bypass, so their
own PR will not prove the gate works.

---

## Part 10 — Known traps

Ordered by how often they bite.

1. **Missing `workflow` token scope.** Pushing anything under `.github/workflows/` fails. Fix with
   `gh auth refresh -s repo,workflow`. Part 1.
2. **Required status check that never ran.** Creating the ruleset before CI has reported all four
   contexts once blocks every PR indefinitely with a confusing "Expected" state. Let CI run first.
3. **`paths:` filters on required checks.** A skipped job never reports, so the PR stays blocked
   forever. Part 4.4.
4. **Check-name drift.** The ruleset requires the literal strings `lint-api`, `test-api`,
   `lint-web`, `test-web`. Renaming a CI job without updating the ruleset silently blocks all
   merges.
5. **Making the repo private again.** Rulesets vanish on the Free plan and every protection in
   Part 7 stops applying, without a warning. Part 0.
6. **`require_code_owner_review` with no CODEOWNERS file.** The rule appears set but matches
   nothing. Part 3.3.
7. **Verifying the gate as the owner.** The admin bypass means the owner's own PR merges
   regardless. Test with the collaborator's account. Part 9.
8. **PowerShell argument splitting.** `-f title="M0 - Foundation"` breaks; use
   `-f "title=M0 - Foundation"`. For multi-line bodies use `--body-file`, never a Bash heredoc.
9. **Two hook managers.** pre-commit plus husky/lint-staged fight over `.git/hooks`. Pick one;
   this playbook uses pre-commit for both languages. Part 4.3.
10. **Duplicate `good first issue` / `good-first-issue` labels.** Pick one. Part 5.1.
11. **Coverage gate set too high on day one.** A permanently red gate gets disabled rather than
    respected. Start where the project sits, then ratchet.
12. **`pre-commit install` without `--hook-type commit-msg`.** The conventional-commit check never
    runs. The `default_install_hook_types` line prevents this, but run both install commands
    anyway.
13. **Creating issues from an unapproved backlog.** Write the backlog doc, get it read, then bulk
    create. Part 6.1.
14. **Secrets in a public repo.** `.env` git-ignored from the first commit; `detect-private-key`
    hook enabled. Part 4.3.

---

## Appendix — Source project reference

This mechanism is in production use in `Ihebdhouibi/Arabic-Islamic-Rag`. Files worth reading
directly if something here is ambiguous — note that its stack is Python-only, so the React half of
Part 4 has no counterpart there:

| File | What it shows |
| --- | --- |
| `CLAUDE.md` | Working agreement as actually written |
| `CONTRIBUTING.md` | Branch model, commit style, PR checklist |
| `.pre-commit-config.yaml` | Hook set and pinned revisions |
| `.github/workflows/ci.yml` | `lint` + `test` jobs with service containers |
| `.github/ISSUE_TEMPLATE/*.yml` | Bug and feature templates |
| `.github/pull_request_template.md` | PR checklist |
| `docs/implementation/general_module_plan.md` | Plan document shape |
| `docs/implementation/general_module_issues.md` | Backlog shape and the bulk-create appendix |
| `pyproject.toml` | ruff / mypy / pytest / coverage configuration |

### Suggested order of work

1. Part 0 — confirm the stack. Report it to the owner before writing code.
2. Part 1 — preflight, token scopes, invite the collaborator.
3. Part 2 — branches, default branch, merge settings.
4. Parts 3-5 — governance docs, enforcement layer, scaffolding. One `chore/*` branch, one PR.
5. Let CI run green on `develop`.
6. Part 7 — the ruleset.
7. Part 6 — plan document, then backlog document, then **stop and get approval**, then bulk-create
   issues and add the domain labels deferred in Part 5.1.
8. Part 9 — verify end to end with the collaborator.
