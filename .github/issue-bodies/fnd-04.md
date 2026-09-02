**Task id:** `FND-04`
**Milestone:** MVP
**Size:** S (half a day or less)
**Depends on:** `FND-01`
**Branch:** `chore/fnd-04-activate-ci`
**Labels:** `ci`, `infra`

## Goal

Move the CI workflow from its staging directory into `.github/workflows/` and, once it has reported all four check contexts on `develop`, add those contexts as required status checks on the branch ruleset. Until this lands, CI does not run and the only merge gate is code-owner review.

## Requirements

1. **This issue is owned by the repository owner, not the implementer.** It needs the `workflow` OAuth scope, which only the owner can grant to their own token.
2. The owner runs `gh auth refresh -h github.com -s repo,workflow` (a browser flow).
3. `git mv .github/workflows-staged/ci.yml .github/workflows/ci.yml`, remove `.github/workflows-staged/README.md`, open the PR and merge it.
4. Let CI run once on `develop` so all four contexts report: `lint-api`, `test-api`, `lint-web`, `test-web`.
5. Only then apply the full ruleset, which adds the required-status-checks rule: `gh api -X PUT "repos/:owner/:repo/rulesets/<id>" --input .github/ruleset.json`.
6. Delete `.github/ruleset-no-checks.json` in the same PR; it exists only to bridge the gap before CI is live.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- `gh auth status | grep -i "token scopes"` includes `workflow`.
- `gh api "repos/:owner/:repo/commits/develop/status" -q '.statuses[].context'` lists all four contexts.
- `gh api "repos/:owner/:repo/rulesets/<id>"` shows a `required_status_checks` rule with `strict_required_status_checks_policy: true` and the four contexts.
- A pull request with a deliberately failing test **cannot** be merged, and the GitHub UI names the failing required check.
- `.github/workflows-staged/` no longer exists.

## Deliverables

- `.github/workflows/ci.yml` in its final location.
- `.github/workflows-staged/` removed.
- `.github/ruleset-no-checks.json` removed.
- The ruleset updated on the repository (an API action, not a file change).

## Notes

Two traps here, both from the workflow playbook. First: applying the required-status-checks rule **before** CI has reported blocks every pull request indefinitely with an unexplained "Expected" state. Second: the four contexts are matched as literal strings against CI job names, so renaming a job in `ci.yml` without updating `.github/ruleset.json` in the same change silently blocks all merges. Never add `paths:` filters to `ci.yml` — a skipped job never reports, which produces the same permanent block.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `chore/fnd-04-activate-ci`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
