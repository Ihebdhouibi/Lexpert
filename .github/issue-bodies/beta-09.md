**Task id:** `BETA-09`
**Milestone:** Beta
**Size:** L (3 days or more)
**Depends on:** `CMP-03`
**Branch:** `feature/beta-09-arabic-localization`
**Labels:** `frontend`

## Goal

Add Arabic as a second locale, which the feasibility study lists as optional for later but which materially widens reach. It is a large change because Arabic is right-to-left, not because the strings are many.

## Requirements

1. A full Arabic catalogue alongside the French one, with the language selectable and the choice persisted per user.
2. Right-to-left layout support throughout: logical CSS properties rather than left and right, mirrored icons where direction carries meaning, and correct bidirectional handling where Latin text (a professional's name, a currency code) appears inside Arabic.
3. Locale-aware formatting for numbers, dates and currency.
4. Server-side French and Arabic for notifications, driven by the recipient's preference, extending the NOT-01 template registry rather than duplicating it.
5. A test that every catalogue key exists in both locales, failing on either a missing translation or an orphaned key.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Test: the key-parity check passes and fails correctly on a deliberately missing key.
- Test: switching locale re-renders and persists the choice.
- Test: right-to-left layout is applied and no component uses physical left/right properties.
- Test: a Latin name inside an Arabic sentence renders in the correct order.
- Test: notification templates render in both locales per the recipient's preference.
- Manual: walk the whole client flow in Arabic on a 375px viewport.

## Deliverables

- The Arabic catalogue and the locale switcher.
- Right-to-left layout support and the physical-property lint rule.
- Arabic notification templates.
- Tests as listed above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-09-arabic-localization`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
