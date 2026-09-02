**Task id:** `NOT-02`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `NOT-01`, `CON-02`, `DSP-02`
**Branch:** `feature/not-02-lifecycle-notifications`
**Labels:** `backend`

## Goal

Trigger the right message at each point in a consultation's life, to the right party, on the right channel. Reminders in particular are the cheapest available remedy for the no-show rate the feasibility study names as a KPI to watch.

## Requirements

1. Notifications on: verification approved, rejected or more-info-requested (to the professional); booking confirmed (to both, with the joining details); a reminder 24 hours before and another 30 minutes before (to both, from settings); consultation starting now; funds released (to the professional); refund issued (to the client); dispute raised (to the professional and the admin queue); dispute resolved (to both); cancellation (to the counterparty).
2. Reminders are scheduled, deduplicated and idempotent: a reminder is sent exactly once per consultation per reminder type, even if the scheduler runs twice or is restarted.
3. A cancelled or refunded consultation stops its pending reminders. A reminder for a consultation that no longer exists in a joinable state must not be sent.
4. Reminders carry the recipient's local time, not UTC and not the professional's zone for the client. A diaspora client must read the time they will actually join at.
5. Channel choice per notification type: time-critical ones (reminders, starting now) prefer SMS; informational ones prefer email; both where it matters.
6. No notification body contains consultation content, a dispute description, or any health, legal or financial detail. Reminders name the professional and the time, nothing more.
7. An admin view of the notification log, filterable by consultation and status, so a 'I never got the reminder' report is answerable.
8. Every trigger point is a call from the existing service layer, not a database trigger or a polling reconciler, except the reminders which are inherently scheduled.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test per notification type: the triggering action results in exactly one send to the correct party on the correct channel, using the recording fake.
- Integration test: running the reminder scheduler twice sends each reminder once.
- Integration test: cancelling a consultation prevents its pending reminders.
- Integration test with a frozen clock: the 24-hour and 30-minute reminders fire at the right times and not before.
- Integration test: a reminder to a client in `Europe/Paris` renders the time in that zone; the same consultation's reminder to the professional renders in `Africa/Tunis`.
- Integration test: a released consultation notifies the professional; a refund notifies the client.
- Integration test: a dispute notifies the professional and produces an admin-queue notification.
- Test asserting no notification body for any type contains a dispute description or a consultation note (assert over every template's variables).
- Integration test: the admin notification-log view filters by consultation and by status.

## Deliverables

- The trigger calls at each service-layer point, plus `lexpert_api/notifications/jobs/reminders.py`.
- The remaining French templates.
- The admin notification-log endpoint and view.
- `apps/api/tests/notifications/test_lifecycle.py` covering every type.
- A table in `docs/technical_docs/notifications.md` mapping event to recipient, channel and template.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/not-02-lifecycle-notifications`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
