**Task id:** `CON-04`
**Milestone:** MVP
**Size:** S (half a day or less)
**Depends on:** `CON-02`
**Branch:** `feature/con-04-consent-capture`
**Labels:** `compliance`, `consultation`

## Goal

Record that each party consented to a remote consultation, on what terms, and at what version of those terms. Medical and legal consultations carry professional confidentiality obligations, and the INPDP requires explicit consent for sensitive personal data; an unrecorded consent is, for compliance purposes, no consent.

## Requirements

1. A `ConsentRecord`: user id, consultation id, consent type, the version of the document consented to, granted_at, and the request context (IP and user agent) captured at the moment of consent.
2. Consent types the MVP needs: remote-consultation terms, personal-data processing, and, for the medical vertical, the telemedicine-specific consent the decree implies.
3. Consent is captured **before** the first join and blocks the join endpoint until present, for whichever party has not yet given it.
4. Consent documents are versioned, and the record stores the version. A change to the terms therefore requires fresh consent rather than silently reinterpreting an old one.
5. Consent records are append-only. A withdrawal is a new record, never an edit or a deletion of the original.
6. An explicit, stored statement that consultations are **not recorded** in the MVP, shown as part of the consent copy, so that adding recording in Beta is visibly a change requiring new consent.
7. `GET /api/v1/consultations/{id}/consents` for the parties and admins, so a professional can confirm consent exists before consulting.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: joining without consent is refused with the documented code; after consent, it succeeds.
- Integration test: each party's consent is tracked independently — one party's consent does not unblock the other.
- Integration test: a medical consultation additionally requires the telemedicine consent; a legal one does not.
- Integration test: `UPDATE` and `DELETE` against the consent table, via raw SQL, are refused.
- Integration test: bumping the document version invalidates the old consent for a new consultation and requires a fresh one.
- Integration test: the request context is stored.
- Integration test: a third party cannot read the consents.
- Component test: the consent screen renders the French copy including the no-recording statement, and the join control is disabled until it is accepted.

## Deliverables

- `lexpert_api/compliance/consent.py` and its models and migration.
- The consent capture and read endpoints, and the join-endpoint guard.
- Versioned French consent copy in the web catalogue plus a consent screen.
- `apps/api/tests/compliance/test_consent.py`.
- `docs/technical_docs/consent_and_data_protection.md` listing the consent types, their versions, and which vertical needs which.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/con-04-consent-capture`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
