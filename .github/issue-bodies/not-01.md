**Task id:** `NOT-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `AUT-02`
**Branch:** `feature/not-01-notification-service`
**Labels:** `backend`

## Goal

Replace the AUT-02 logging stub with a real notification service: French templates rendered once and delivered over email or SMS behind adapters. SMS matters disproportionately here — the feasibility study notes it has the highest open rate in Tunisia, and it is what will actually get someone to a consultation on time.

## Requirements

1. An `EmailProvider` and an `SmsProvider` protocol, each with one concrete adapter, a no-op adapter for local development, and a recording fake for tests. Selected by settings, as with the escrow and video providers.
2. A template registry: each notification type has a French template per channel, with a subject where applicable. Templates live in files, not in Python string literals, and are rendered with escaping appropriate to the channel.
3. SMS templates must respect the practical single-message length and must be written as plain text with no HTML entities leaking in. Test the rendered length.
4. A `NotificationLog` row per send attempt: type, channel, recipient reference, status, provider reference, attempt count, error, timestamps. **The rendered body is not stored** — it can contain personal detail, and the type plus the recipient is enough to debug a delivery.
5. Retry with backoff on a transient provider failure, a cap on attempts, and a terminal failed state that is visible to admins.
6. Sending is asynchronous with respect to the request that triggers it: a failing SMS provider must never fail a booking. Trigger a background send and let the log carry the outcome.
7. Per-user channel preferences, defaulting to both, with a hard rule that security-relevant notifications (password reset, verification) are always sent regardless of preference.
8. Recipient normalisation: Tunisian numbers to E.164, and a rejection path for a number the provider cannot deliver to.
9. Replace the AUT-02 stub with this service, leaving the interface unchanged so no call site moves.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: each template renders with its variables in French, with no unreplaced placeholders. A test that iterates every registered template and asserts this.
- Unit test: every SMS template renders within the tested length limit.
- Unit test: the recording fake captures type, channel and recipient for each send.
- Integration test: a transient failure retries with backoff and succeeds; the log shows the attempt count.
- Integration test: a persistent failure reaches the cap and lands in the failed state.
- Integration test: a provider raising an exception does not fail the triggering request.
- Integration test: channel preferences suppress a non-security notification and do **not** suppress a password reset.
- Unit test: a local Tunisian number normalises to E.164; an undeliverable number is rejected with a clear code.
- Test asserting no rendered body and no verification token appears in the notification log or in any captured log line.
- Integration test: the AUT-02 flows still work through the new service.

## Deliverables

- `lexpert_api/notifications/` with the protocols, adapters, template registry and log model plus migration.
- `lexpert_api/notifications/templates/` with the French templates.
- `apps/api/tests/notifications/` covering every item above.
- New settings in `.env.example`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/not-01-notification-service`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
