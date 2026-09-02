**Task id:** `KYC-03`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `KYC-01`
**Branch:** `feature/kyc-03-vertical-rules`
**Labels:** `kyc-pro`, `backend`, `compliance`

## Goal

Encode what each of the three regulators requires, as three declarative rule sets behind one interface, so that adding a fourth vertical later is a new rule set rather than a change to the submission pipeline. This is the issue that makes the platform genuinely multi-vertical rather than medical-with-extras.

## Requirements

1. A `VerticalRuleSet` interface declaring: required fields with their types and validation, required document types, and a `validate(file) -> list[Violation]` method returning every violation rather than raising on the first.
2. **Medical (CNOM):** CNOM registration number with its documented format, medical speciality from the FND-07 list, diploma year, place of practice. Required documents: national ID, diploma, CNOM registration certificate.
3. **Legal (Ordre National des Avocats de Tunisie):** bar registration number, bar section (the regional bar), date sworn in, areas of practice. Required documents: national ID, diploma, bar registration certificate.
4. **Financial (OECT):** OECT membership number, practice type (expert-comptable or comptable), areas of practice. Required documents: national ID, diploma, OECT membership certificate.
5. Validate identifier **format** only. No regulator publishes a verification API, so do not pretend to check a number against a registry; that is what the admin review is for. Where the real format is uncertain, implement a documented permissive check and leave a `TODO` naming the open question — do not invent a strict format that rejects real professionals.
6. Violations carry a machine code and a French message, and name the field or document type they concern, so KYC-05 can render them inline against the right input.
7. A registry mapping vertical to rule set, and a test that fails if a `Vertical` member has no rule set.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test per vertical: a complete, valid file produces no violations.
- Unit test per vertical: each individually missing required field produces exactly one violation naming that field.
- Unit test per vertical: each individually missing required document produces exactly one violation naming that document type.
- Unit test: a file with three problems returns three violations, not one.
- Unit test: a malformed regulator identifier is rejected with the documented code.
- Unit test: submitting a medical file's fields under the legal vertical produces violations, proving the rule sets are not interchangeable.
- Unit test: the registry covers every `Vertical` member.
- Every violation code has a French message in `fr.ts` (the FND-07 label test pattern extended to violation codes).

## Deliverables

- `lexpert_api/verification/rules/` with `base.py`, `medical.py`, `legal.py`, `financial.py`, `registry.py`.
- `apps/api/tests/verification/test_rules_*.py`, one file per vertical.
- `docs/technical_docs/kyc_vertical_requirements.md` tabulating what each regulator requires, with the open questions listed explicitly.
- Violation codes and French messages in `fr.ts`.

## Notes

The exact identifier formats need confirming with each ordre; the feasibility study flags all three as to-verify. Implement permissively, document every assumption in `kyc_vertical_requirements.md`, and raise the open questions on this issue rather than guessing silently. A rule set that rejects a real doctor is worse than one that accepts a typo, because the admin review catches the typo.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/kyc-03-vertical-rules`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
