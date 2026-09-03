**Task id:** `SCH-02`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `SCH-01`
**Branch:** `feature/sch-02-slot-computation`
**Labels:** `scheduling`, `backend`, `api`

## Goal

Turn availability rules, exceptions, buffers and existing bookings into the concrete list of slots a client can pick. This is pure, testable logic and it should stay that way — no database access inside the computation itself.

## Requirements

1. A pure function taking rules, exceptions, existing consultations, constraints, a duration, a date range and a clock, and returning slot instants. No I/O inside it.
2. Slots are generated at the requested duration, aligned to the rule's start, with the buffer applied after each existing consultation and after each generated slot as appropriate.
3. A slot is excluded if it overlaps an existing consultation in any non-terminal state -- which includes `PENDING_ACCEPTANCE`, so a request awaiting the professional's answer holds its slot -- if it falls inside the minimum-notice window, if it is beyond the maximum horizon, or if it extends past the availability window's end.
4. `GET /api/v1/professionals/{id}/slots?duration=&from=&to=&tz=` returning slots with both the UTC instant and a rendering in the requested timezone, so the client never has to reimplement the conversion.
5. Cap the requested range (for example 60 days) and reject a longer one rather than computing it.
6. The endpoint is public, consistent with PRO-02, but returns slots only for published and approved professionals.
7. Concurrency is **not** solved here: two clients can be shown the same slot. The authoritative check is the booking transaction in ESC-03. Say so in a comment so nobody adds a reservation mechanism at this layer.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: a single 09:00-12:00 rule with a 60-minute duration and no buffer yields exactly three slots.
- Unit test: the same with a 15-minute buffer yields the documented smaller set.
- Unit test: an existing consultation at 10:00 removes the 10:00 slot and, with a buffer, the adjacent one.
- Unit test: a slot that would run past 12:00 is not generated.
- Unit test: minimum notice removes today's imminent slots, with the clock frozen.
- Unit test: maximum horizon truncates the range.
- Unit test: a full-day exception yields no slots for that date.
- Unit test: a `CANCELLED`, `DECLINED` or `EXPIRED` consultation does **not** block its slot; a `FUNDS_HELD` or `PENDING_ACCEPTANCE` one does.
- Unit test: slots requested in `Europe/Paris` render at the correct local times across a DST boundary.
- Integration test: an over-long range is refused; an unpublished professional returns 404.
- Property test: no returned slot ever overlaps another returned slot or an existing consultation.

## Deliverables

- `lexpert_api/scheduling/slots.py` — the pure computation.
- The slots endpoint and its schemas.
- `apps/api/tests/scheduling/test_slots.py` with the table-driven and property tests.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/sch-02-slot-computation`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
