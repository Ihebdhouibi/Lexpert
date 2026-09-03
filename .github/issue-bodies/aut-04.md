**Task id:** `AUT-04`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `AUT-02`, `AUT-03`, `FND-06`, `UX-05`, `UX-07`
**Branch:** `feature/aut-04-web-auth`
**Labels:** `frontend`, `auth`

## Goal

The French screens for registering, logging in, verifying a phone and resetting a password, plus the client-side session handling and route guards that keep the three portals apart.

## Requirements

1. Screens, all in French through the i18n catalogue: register (with a client or professional choice), login, forgot password, reset password, verify phone (code entry with resend), verify email landing page.
2. Session handling: the access token in memory, the refresh token in an `httpOnly`-style persisted slot as far as the API allows, silent refresh on 401 with a single retry, and a full logout that clears everything.
3. Route guards: unauthenticated users are redirected to login with a return path; a client cannot reach `/pro` or `/admin`; a professional cannot reach `/admin`.
4. A professional who logs in with verification not yet `APPROVED` lands on their verification status page (KYC-05), not on a dashboard they cannot use.
5. Form validation with inline French error messages, and mapping of API error `code` values to French copy from the catalogue. Never render the API's `message` when a known code has a local translation.
6. Accessible forms: real labels, `aria-describedby` on errors, focus moved to the first invalid field on submit, and the whole flow completable by keyboard.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test per screen: renders, validates, submits, shows the server error.
- Test: a 401 on a protected query triggers exactly one silent refresh and one retry, then logs out if the refresh fails.
- Test: guards redirect correctly for each of the three roles, and the return path is honoured after login.
- Test: a professional with `SUBMITTED` verification is routed to the status page.
- Test: every rendered string comes from the catalogue (the FND-06 check covers this and must stay green).
- Manual: the whole register-verify-login path is completable by keyboard on a 375px viewport.

## Deliverables

- `apps/web/src/features/auth/` with the six screens.
- `apps/web/src/app/guards.tsx` and the session store.
- Auth keys added to `fr.ts`.
- Component tests for each screen and the guards.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/aut-04-web-auth`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
