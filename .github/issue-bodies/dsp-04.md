**Task id:** `DSP-04`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-06`, `PRO-02`
**Branch:** `feature/dsp-04-ratings`
**Labels:** `backend`, `frontend`

## Goal

Let a client rate a completed consultation, and surface the aggregate on the professional's profile and in search. The feasibility study ties ratings to trust and safety and to moderation, so a rating must be tied to a real, paid, completed consultation and nothing else.

## Requirements

1. `Rating`: consultation id (unique — one rating per consultation), client id, professional id, a 1-5 score, an optional French comment, created_at.
2. A rating can only be created by the consultation's client, and only when the consultation is `RELEASED_TO_PRO`. A refunded, cancelled or disputed-and-refunded consultation cannot be rated: there is no verified service to rate.
3. A rating window (for example 30 days after release) after which rating is closed.
4. Aggregate rating and count stored on the professional's profile, updated on each new rating, and exposed in the public profile and in search. Recomputing the average across all ratings on every search query does not scale; a maintained aggregate does — but it must be derivable, so include a command that recomputes it from the ratings and a test proving the maintained value matches.
5. A rating cannot be edited or deleted by the client once submitted. Admins can hide a rating (a moderation flag) which excludes it from the aggregate but does not delete it.
6. Wire the `rating` sort order in PRO-02 to the real aggregate, replacing the hook left there.
7. The comment is client-written free text: never logged, and moderated by hiding rather than editing.
8. Client-side: a rating prompt on the consultation detail after release, the rating form, and the display of ratings on the professional's public profile with the aggregate, the count, and the individual comments.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: the client rates a `RELEASED_TO_PRO` consultation successfully.
- Integration test: rating a `REFUNDED`, `CANCELLED` or `HOLD_WINDOW` consultation is refused, each with its documented code.
- Integration test: a second rating on the same consultation is a conflict.
- Integration test: the professional, and an unrelated client, cannot rate it.
- Integration test: rating after the window closes is refused.
- Integration test: a score of 0 and of 6 are both refused.
- Integration test: the aggregate updates correctly across several ratings, and the recompute command produces the identical value.
- Integration test: hiding a rating removes it from the aggregate and from the public list, without deleting the row.
- Integration test: sorting search by rating orders correctly, including professionals with no ratings.
- Component test: the rating prompt appears only after release; the form validates and submits; the profile renders the aggregate and the comments.
- Test asserting the comment text does not appear in any captured log line.

## Deliverables

- `lexpert_api/profiles/ratings.py`, its models and migration, and the endpoints.
- The aggregate recompute command.
- The PRO-02 rating sort wired to the real value.
- `apps/web/src/features/client/ratings/` and the profile ratings display.
- `apps/api/tests/profiles/test_ratings.py` and the component tests.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/dsp-04-ratings`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
