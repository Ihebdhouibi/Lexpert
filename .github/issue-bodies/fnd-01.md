**Task id:** `FND-01`
**Milestone:** MVP
**Size:** S (half a day or less)
**Depends on:** nothing
**Branch:** `feature/fnd-01-monorepo-scaffolding`
**Labels:** `infra`

## Goal

Create the two-app monorepo layout every later issue assumes, so that both apps build, lint and run their (empty) test suites from a clean clone. Nothing functional is added here; this issue exists so that no feature PR has to also invent the project structure.

## Requirements

1. Create `apps/web` from the Vite React + TypeScript template. Add the scripts CI depends on: `dev`, `build`, `typecheck` (`tsc --noEmit`), `lint` (`eslint .`), `format:check` (`prettier --check .`), `test` (`vitest run --coverage`).
2. Configure ESLint on the flat-config format (`eslint.config.js`) with `typescript-eslint` and `eslint-plugin-react-hooks`. Prettier is the only formatter; ESLint handles correctness rules only, so the two never disagree.
3. Commit `apps/web/package-lock.json` so CI's `npm ci` is reproducible. Node version is pinned in the repository-root `.nvmrc` (already committed, value `20`).
4. Create `apps/api` as an installable Python package: `pyproject.toml` with the package under `apps/api/src/lexpert_api/`, plus an `apps/api/tests/` root.
5. **Python 3.11**, pinned deliberately -- it is what the rest of the team's stack runs. Set `requires-python = ">=3.11,<3.12"` so an install on the wrong interpreter fails immediately rather than at some later import, and commit a `.python-version` of `3.11` for pyenv. CI runs 3.11 too, so a local pass means a CI pass.
6. Configure `apps/api/pyproject.toml` exactly as specified in the Deliverables section below: ruff, mypy strict, pytest and coverage with `fail_under = 70`.
7. Add one trivial passing test per app so the suites are not empty (`vitest` on a smoke assertion, `pytest` on a package-import assertion).
8. Run `pre-commit install && pre-commit install --hook-type commit-msg`, then `pre-commit run --all-files`. If that reformats files, commit the reformat as its own `chore: apply pre-commit formatting` commit so the noise stays out of the feature diff.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- From a clean clone: `cd apps/web && npm ci && npm run build` succeeds.
- `npm run lint`, `npm run format:check`, `npm run typecheck` and `npm test` all succeed in `apps/web`.
- From a clean clone: `cd apps/api && pip install -e ".[dev]"` succeeds, then `ruff check .`, `ruff format --check .`, `mypy src` and `pytest` all succeed.
- `python --version` reports 3.11.x, and installing under 3.12 or 3.10 is refused by `requires-python`.
- `pre-commit run --all-files` passes at the repository root.
- `git commit -m "bad message"` is rejected by the commit-msg hook; `git commit -m "chore: verify hook"` is accepted.

## Deliverables

- `apps/web/` with `package.json`, `package-lock.json`, `eslint.config.js`, `.prettierrc`, `tsconfig.json`, `vite.config.ts`, one smoke test.
- `apps/api/pyproject.toml`, `apps/api/src/lexpert_api/__init__.py`, `apps/api/tests/test_smoke.py`.
- `.python-version` at the repository root, containing `3.11`.
- A short `apps/README.md` stating which app is which and how to run each.

## Notes

The `apps/api/pyproject.toml` configuration is fixed, because CI and the ruleset depend on it:

```toml
[project]
requires-python = ">=3.11,<3.12"

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.16", "mypy>=1.11", "httpx>=0.27"]

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
```

Do not raise `fail_under` in this issue. A gate that is red on the first PR gets disabled instead of respected; it is ratcheted up later in a `chore:` PR.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/fnd-01-monorepo-scaffolding`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
