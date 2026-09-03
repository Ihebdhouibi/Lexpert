**Task id:** `FND-04`
**Milestone:** MVP
**Size:** S (half a day or less)
**Depends on:** nothing
**Branch:** `chore/fnd-04-required-checks`
**Labels:** `ci`, `infra`

## Goal

Finish turning CI into a merge gate. The workflow is live and running; what remains is adding its six contexts to the branch ruleset as required status checks, so a red build actually blocks a merge instead of merely being visible.

## Requirements

1. **Owned by the repository owner, not the implementer.** It changes repository settings, not code.
2. Already done, recorded here so the remaining work is unambiguous: the `workflow` OAuth scope was granted; `.github/workflows/ci.yml` is in place and `.github/workflows-staged/` is gone; the six jobs are `repo-checks`, `secrets`, `lint-api`, `test-api`, `lint-web` and `test-web`.
3. Confirm all six contexts have reported on `develop` at least once. A required check that has never reported blocks every pull request indefinitely in an unexplained "Expected" state, so this check is not optional.
4. Apply the full ruleset, which carries the required-status-checks rule with `strict_required_status_checks_policy: true`: `gh api -X PUT "repos/:owner/:repo/rulesets/<id>" --input .github/ruleset.json`.
5. Delete `.github/ruleset-no-checks.json`; it exists only to bridge the gap before CI was live, and leaving it invites someone to apply it by mistake.
6. Verify with a throwaway pull request carrying a deliberately failing check that the merge is blocked and the GitHub UI names the failing context.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- `gh api "repos/:owner/:repo/commits/develop/status" -q '.statuses[].context'` lists all six contexts.
- `gh api "repos/:owner/:repo/rulesets/<id>"` shows a `required_status_checks` rule with `strict_required_status_checks_policy: true` and exactly those six contexts.
- A pull request with a deliberately failing check **cannot** be merged, and the failing context is named in the UI. Test this with the collaborator's account, not the owner's -- the owner has the admin bypass, so their own pull request proves nothing.
- `python scripts/check_ruleset_contexts.py` passes.
- `.github/ruleset-no-checks.json` no longer exists.

## Deliverables

- `.github/ruleset-no-checks.json` removed.
- The ruleset updated on the repository (an API action, not a file change).
- The blocked-merge verification evidenced on the pull request.

## Notes

Two traps, both from the workflow playbook. First: applying the required-status-checks rule **before** CI has reported blocks every pull request indefinitely. Second: contexts are matched as literal strings against job names, so renaming a job without updating `.github/ruleset.json` in the same change silently blocks all merges -- `scripts/check_ruleset_contexts.py` runs in the `repo-checks` job to catch exactly that, and it also rejects a `paths:` filter on `pull_request`, since a skipped job never reports and produces the same block.

Note that the four app jobs currently detect a missing `apps/` directory and pass without doing anything. That is deliberate -- a job-level `if` that evaluates false never reports its status, which would block merges under the strict policy. They become real checks as FND-01 creates the apps, and FND-01's own validation requires them to actually run.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `chore/fnd-04-required-checks`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
