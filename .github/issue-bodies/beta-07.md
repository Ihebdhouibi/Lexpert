**Task id:** `BETA-07`
**Milestone:** Beta
**Size:** L (3 days or more)
**Depends on:** `FND-04`, `BETA-06`
**Branch:** `feature/beta-07-deploy-pipeline`
**Labels:** `infra`, `ci`

## Goal

Get the application deployed reproducibly to a staging and a production environment, with migrations applied safely and secrets handled properly. The branch model already implies the promotion path; this makes it real.

## Requirements

1. Container images for both apps, built in CI, tagged by commit, and reproducible.
2. Two environments mapped to the branch model: `stable-testing` deploys to staging, `main` deploys to production.
3. Migrations run as an explicit, gated step before the new version serves traffic, with a documented rollback. An automatic migration on application start is how a bad deploy becomes a data problem.
4. Secrets from a real secret store, injected at runtime. No secret in an image, in a repository, or in a CI log. The repository is public, so this is not negotiable.
5. A smoke test suite run against each environment after deploy, failing the deploy if the critical path is broken.
6. Database backups with a **tested** restore. An untested backup is not a backup, and the ledger is the data that cannot be reconstructed.
7. A documented deployment and rollback runbook.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- A deploy to staging from `stable-testing` succeeds and the smoke tests pass.
- A deliberately broken smoke test fails the deploy.
- A migration failure aborts the deploy and leaves the previous version serving.
- A rollback to the previous version succeeds, following the runbook exactly as written.
- A restore from backup into a scratch environment succeeds and the ledger balances and the audit chain verifies afterwards.
- A scan confirming no secret appears in any image layer or CI log.

## Deliverables

- Dockerfiles and the build pipeline.
- Deployment workflows for both environments.
- The smoke test suite.
- Backup and restore automation, with the tested restore evidenced in the PR.
- `docs/runbooks/deploy.md` and `docs/runbooks/rollback.md`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-07-deploy-pipeline`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
