**Task id:** `CON-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-03`
**Branch:** `feature/con-01-video-provider`
**Labels:** `consultation`, `backend`

## Goal

Put the video SDK behind an adapter, the same way ESC-01 does for payments, and issue the short-lived per-participant tokens that let exactly the right two people into a consultation. Data residency for video is an open question the feasibility study flags for later, so the adapter is what keeps the answer changeable.

## Requirements

1. A `VideoProvider` protocol: `create_room(consultation_id)`, `issue_token(room, participant, role, ttl)`, `end_room(room)`, `get_room_state(room)`. Provider-agnostic result and error types, exactly as in ESC-01.
2. One concrete adapter for the chosen hosted SDK, selected by `LEXPERT_VIDEO_PROVIDER` through a factory, plus a fake in-memory provider used by every test. **No test may call the real provider.**
3. A room is created lazily on the first join, not at booking time, so a cancelled consultation never provisions one.
4. Tokens are per participant, per consultation, short-lived (minutes, from settings), and carry only the permissions that participant needs. A token is never reusable by the other party.
5. `POST /api/v1/consultations/{id}/join` returning a room reference and a token, permitted only to the consultation's client or professional, and only when the consultation is in `FUNDS_HELD` or `IN_SESSION` and inside the join window (a configurable number of minutes before the scheduled start until a configurable number after the scheduled end).
6. Joining outside the window, joining a cancelled or refunded consultation, and joining a consultation you are not party to are each refused with distinct, documented codes.
7. Provider credentials come from settings and must never appear in a response, a log line, or an error message.
8. A contract test suite parameterised over provider implementations, as in ESC-01, so swapping providers later is a matter of running it against the new adapter.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: the fake provider satisfies the full contract suite.
- Unit test: `issue_token` produces distinct tokens for the client and the professional, with the documented permissions.
- Integration test: the client and the professional can each join a `FUNDS_HELD` consultation inside the window.
- Integration test: a third user is refused with 404.
- Integration test: joining before the window opens, and after it closes, each return their documented code.
- Integration test: joining a `CANCELLED` consultation is refused.
- Integration test: the room is created on first join, and a second join reuses the same room rather than creating another.
- Integration test: an expired token is rejected by the provider fake.
- Test asserting no provider credential appears in any response body or captured log line.
- Integration test: an unknown `LEXPERT_VIDEO_PROVIDER` fails at startup.

## Deliverables

- `lexpert_api/consultation/provider.py`, `providers/<sdk>.py`, `providers/fake.py`, `providers/factory.py`.
- The join endpoint and its schemas.
- `apps/api/tests/consultation/test_video_provider_contract.py` and `test_join.py`.
- `docs/technical_docs/video_provider_boundary.md`, including the data-residency question left open for Beta.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/con-01-video-provider`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
