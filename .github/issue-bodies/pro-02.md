**Task id:** `PRO-02`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `PRO-01`
**Branch:** `feature/pro-02-search-api`
**Labels:** `api`, `backend`, `database`

## Goal

The query clients use to find a professional. It is the surface where the 'unapproved professionals are invisible' rule is actually enforced, and the one endpoint most likely to be slow, so both get attention here.

## Requirements

1. `GET /api/v1/professionals` with filters: vertical, speciality, city, language, minimum and maximum hourly rate, and a free-text query over name, title and biography.
2. Only published profiles belonging to `APPROVED` professionals are ever returned. This is a condition in the query itself, not a post-filter in Python, so no code path can accidentally omit it.
3. Sorting: by rate ascending or descending, by years of experience, and by rating once DSP-04 exists (leave the hook, do not fake the value).
4. Cursor-based pagination with a stable order. Offset pagination on a list that changes underneath the user produces duplicates and gaps; do not use it.
5. Full-text search using PostgreSQL `tsvector` with the French configuration, so French stemming and accent handling work. A stored generated column plus a GIN index, not a per-query `to_tsvector`.
6. Indexes for the filter combinations that will actually be used (vertical plus city, vertical plus speciality). Include the query plan for the common case in the PR description.
7. An `available_from` filter is **out of scope here**; availability arrives in SCH-02 and joining against it now would be premature. Note the intended integration point in a comment.
8. The endpoint is public — no authentication — because clients browse before registering. It must therefore expose nothing beyond the public profile shape from PRO-01.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test per filter: it narrows the result set correctly.
- Integration test: filters combine (vertical plus city plus rate range).
- Integration test: an unpublished profile and an unapproved professional are both absent, tested independently.
- Integration test: French full-text search matches with different accents and with a stemmed form (a search for `avocat` matches `avocats`).
- Integration test: cursor pagination over 30 seeded profiles returns each exactly once across pages, with no duplicates or omissions.
- Integration test: inserting a profile mid-pagination does not duplicate an already returned row.
- Integration test: each sort order is correct, including ties.
- Integration test: the response contains no private fields.
- Performance check: with 1000 seeded profiles, `EXPLAIN ANALYZE` for the common filter uses the index and the endpoint responds in under 200 ms locally. Paste the plan in the PR.

## Deliverables

- The search endpoint, its query builder and its schemas.
- The Alembic migration adding the `tsvector` column and the indexes.
- A seeding helper that generates synthetic professionals for tests and local use.
- `apps/api/tests/profiles/test_search.py`.
- The query plan in the PR description.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/pro-02-search-api`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
