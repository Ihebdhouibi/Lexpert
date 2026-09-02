## Summary

<!-- What does this change do and why? Keep it concise. -->

Closes #

## Changes

<!-- Bullet the key changes. -->

-

## How the issue's validation checks were satisfied

<!-- Go through the "Validation / test checks" section of the linked issue and say, for each item,
     what proves it. Name the test or the command. -->

-

## Checklist

- [ ] Branch is `feature/*` or `chore/*` off `develop`, scoped to one issue
- [ ] `pre-commit run --all-files` passes
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass
- [ ] Tests cover the change; coverage stays above the CI gate
- [ ] Every "Validation / test checks" item on the linked issue is satisfied
- [ ] No secrets, credentials, or client data in the diff
- [ ] User-facing strings are French and come from the i18n catalogue
- [ ] No escrow state transition bypasses the ledger and the audit log
