**Task id:** `CON-02`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `CON-01`, `ESC-06`
**Branch:** `feature/con-02-session-lifecycle`
**Labels:** `consultation`, `escrow`, `backend`

## Goal

Track who actually joined a consultation and when, decide when it has ended, and signal that to the escrow so the one-hour hold window starts. This is the join between the product's two halves, and it is where a bug means either money never releases or it releases for a consultation that never happened.

## Requirements

1. A `SessionParticipation` record per participant: consultation id, user id, first joined at, last left at, total connected seconds. Built from provider webhooks where available and from the join and leave endpoints otherwise.
2. Webhook endpoint for the provider's participant-joined, participant-left and room-finished events, with **signature verification** and replay protection. An unverified webhook is rejected, not processed.
3. Webhook handling is idempotent: providers redeliver, and a redelivered event must not double-count participation or re-transition the consultation.
4. The first join by either party transitions `FUNDS_HELD -> IN_SESSION`.
5. A consultation ends, transitioning `IN_SESSION -> SESSION_ENDED` and immediately on to `HOLD_WINDOW`, when either: the professional explicitly ends it (`POST /api/v1/consultations/{id}/end`), or the provider reports the room finished, or a fallback sweeper finds a consultation still `IN_SESSION` past its scheduled end plus a configurable grace period. All three paths converge on one service function.
6. The fallback sweeper is not optional. A provider webhook that never arrives must not leave money held forever; this is the failure mode most likely to occur in production.
7. Both parties' participation is exposed to ESC-07's no-show determination: no join at all by a party, past the grace period, is a no-show by that party.
8. A consultation where **neither** party joined is not released to the professional; it goes down the no-show path.
9. `GET /api/v1/consultations/{id}/session` returning the participation summary to the two parties and to admins.
10. **No consultation content is recorded.** No transcript, no recording, no chat log. Only participation timestamps. Note this explicitly in the module docstring; MVP recording is out of scope and would change the consent requirements entirely.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: the first join moves `FUNDS_HELD -> IN_SESSION` and records participation.
- Integration test: an explicit end moves through `SESSION_ENDED` to `HOLD_WINDOW` with the expiry set from the hold-window setting.
- Integration test: a provider room-finished webhook produces the same result.
- Integration test: the sweeper ends a consultation left `IN_SESSION` past its scheduled end plus grace, with the clock frozen; and does not end one inside the grace period.
- Integration test: a redelivered join webhook does not double-count participation.
- Integration test: a redelivered room-finished webhook does not re-transition or produce a second audit entry.
- Integration test: an unsigned or wrongly-signed webhook is rejected with no state change.
- Integration test: a replayed webhook outside the freshness window is rejected.
- Integration test: a consultation neither party joined is routed to the no-show path, not released.
- Integration test: a professional no-show (only the client joined) refunds the client per ESC-07.
- Integration test: the end-to-end path, with a frozen clock, from booking through join, end, hold window and ESC-06 auto-release, leaves a balanced ledger and a gapless audit chain.
- Test asserting no field on any session model can hold consultation content.

## Deliverables

- `lexpert_api/consultation/models.py`, `service.py`, `webhooks.py`, `jobs/session_sweeper.py`.
- The end and session endpoints, and the webhook route.
- `apps/api/tests/consultation/test_session_lifecycle.py`, `test_webhooks.py`, `test_end_to_end_flow.py`.
- A `## Session lifecycle` section in `docs/technical_docs/escrow_lifecycle.md` showing all three end paths converging.

## Notes

The end-to-end test in this issue is the closest thing the project has to a proof that the MVP works. Keep it readable and keep it fast enough to run on every PR; it is the test most likely to catch a regression in any of the modules it crosses.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/con-02-session-lifecycle`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
