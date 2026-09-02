**Task id:** `SCH-01`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `PRO-01`
**Branch:** `feature/sch-01-availability-model`
**Labels:** `scheduling`, `backend`, `database`

## Goal

Model when a professional is available. This is the issue where timezone mistakes get baked in for good, so the rules about what is stored in what zone are the substance of it. Diaspora clients in Paris booking a professional in Tunis is a first-class case, not an edge case.

## Requirements

1. `AvailabilityRule`: professional id, day of week, start time, end time, effective from and optional effective until. Multiple rules per day are allowed and must not overlap.
2. `AvailabilityException`: a specific date made either fully unavailable (a holiday) or available with different hours, overriding the weekly rule for that date.
3. Booking constraints on the professional: buffer minutes between consultations, minimum notice before a booking (for example no bookings inside the next 2 hours), and a maximum horizon (for example no bookings more than 60 days out).
4. **Storage and computation rules, stated once and followed everywhere:** the professional's IANA timezone is stored on their profile; weekly rules are stored as local times in that zone; every instant (consultation start and end, exception dates resolved to instants) is stored in UTC as `timestamptz`. Conversion happens at exactly one boundary.
5. Handle daylight-saving transitions correctly for clients in European zones: a rule at 09:00 Tunis time is a different UTC instant in January and in July. Test both.
6. Overlap validation: creating a rule that overlaps an existing rule for the same day is refused with a clear code, and so is a rule whose end is not after its start.
7. `GET/PUT /api/v1/scheduling/me/rules` and `GET/POST/DELETE /api/v1/scheduling/me/exceptions`, guarded by `require_verified_professional`.
8. Changing availability must not invalidate consultations already booked into a now-unavailable slot. Those stand; the professional cancels them explicitly if needed, through the ESC-07 policy.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: overlapping rules for the same day are refused; adjacent rules (09:00-12:00 and 12:00-15:00) are accepted.
- Unit test: a rule with end at or before start is refused.
- Unit test: a full-day exception removes that date entirely.
- Unit test: a modified-hours exception replaces the weekly rule for that date only, leaving the following week unchanged.
- Unit test: a 09:00 Tunis rule resolves to the correct UTC instant on a January date and on a July date, and the two differ where the zone offset differs.
- Unit test: a rule spanning a DST transition date produces the expected local hours on both sides.
- Unit test: minimum notice and maximum horizon are applied as documented at both boundaries.
- Integration test: another professional cannot read or write these rules.
- Integration test: an existing consultation survives the deletion of the rule that created its slot.
- A `grep` check that no naive `datetime.now()` or `datetime.utcnow()` call exists in the scheduling module; all time comes from an injectable clock so tests can freeze it.

## Deliverables

- `lexpert_api/scheduling/models.py`, `service.py`, `router.py`, `schemas.py`.
- `lexpert_api/core/clock.py` — the injectable clock, used project-wide from here on.
- The Alembic migration.
- `apps/api/tests/scheduling/test_availability.py` including the DST cases.
- `docs/technical_docs/time_and_timezones.md` stating the storage rules in one place.

## Notes

Write `time_and_timezones.md` before the code, not after. Every subsequent issue that touches a timestamp will be reviewed against it, and it is much cheaper to agree the rules now than to find two modules disagreeing during ESC-06.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/sch-01-availability-model`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
