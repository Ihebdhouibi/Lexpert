**Task id:** `KYC-07`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `KYC-06`, `AUT-04`, `UX-08`
**Branch:** `feature/kyc-07-admin-review-ui`
**Labels:** `frontend`, `admin`, `kyc-pro`

## Goal

The back-office screens an admin uses to review verification files. Review quality depends on how easily the reviewer can see the documents next to the claimed credentials, so the layout is the substance of this issue, not decoration.

## Requirements

1. A queue screen: table of pending files with applicant name, vertical, submission date and age, plus status and vertical filters and pagination. Oldest first by default.
2. A detail screen laid out for comparison: the declared fields on one side, a document viewer on the other, so the reviewer can read the CNOM number off the certificate while looking at what was typed. Inline PDF and image viewing; no forced download.
3. The decision panel: claim, approve, reject with a required reason, request more information with a required message. Approve and reject both require an explicit confirmation step, because both are consequential and hard to walk back.
4. The event history rendered as a timeline with the reviewer's name and timestamps.
5. Any current rule violations shown prominently — the reviewer should not have to re-derive what the automated check already found.
6. Optimistic-free mutations: after a decision, refetch and show the resulting state rather than assuming success.
7. A conflict on claim (another admin got there first) shows a clear French message and refreshes the queue rather than appearing to succeed.
8. All copy in French through the catalogue.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: the queue renders, filters and paginates against a mocked API.
- Component test: the detail screen renders fields, documents and violations.
- Component test: approve requires confirmation and then calls the endpoint once.
- Component test: reject with an empty reason is blocked client-side; with a reason it submits.
- Component test: `request-info` with an empty message is blocked.
- Component test: a 409 on claim renders the conflict message and triggers a refetch.
- Component test: a PDF and an image document both render inline.
- Manual: review a real submitted file end to end in a running local environment for each of the three verticals.

## Deliverables

- `apps/web/src/features/admin/verification/` with the queue, detail and decision panel.
- A reusable document viewer component.
- Admin keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/kyc-07-admin-review-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
