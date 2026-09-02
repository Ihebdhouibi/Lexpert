**Task id:** `KYC-02`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `KYC-01`
**Branch:** `feature/kyc-02-document-upload`
**Labels:** `kyc-pro`, `backend`, `compliance`

## Goal

Let a professional upload the identity and diploma documents their regulator requires, and let an admin read them — while nobody else can, ever. These are identity documents; a public URL to one is a data-protection incident.

## Requirements

1. A `DocumentStorage` interface with `put`, `get`, `delete` and `presigned_read_url`. A local-filesystem implementation for the MVP, rooted at `LEXPERT_STORAGE_ROOT`, which is git-ignored.
2. `POST /api/v1/verification/documents` (multipart) and `DELETE /api/v1/verification/documents/{id}`, both restricted to the owning professional and only while the file is in `DRAFT` or `MORE_INFO_REQUESTED`.
3. `GET /api/v1/verification/documents/{id}/url` returning a short-lived, single-use read URL. Available to the owning professional and to admins. No other role, no unauthenticated access, and no long-lived or guessable URL.
4. Validation: allowed content types are PDF, JPEG and PNG; maximum 10 MB per file; maximum 10 documents per verification file. Detect the real type from the file's magic bytes, not from the declared `Content-Type` or the extension.
5. Storage keys are opaque and unguessable (a UUID path), never derived from the filename or the user id.
6. Store a SHA-256 checksum and reject an exact duplicate upload within the same verification file.
7. Strip EXIF metadata from images on upload — it can carry GPS coordinates.
8. Deleting a document removes both the row and the stored object, and appends a `VerificationEvent`.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: upload a PDF, then fetch the read URL and retrieve the bytes.
- Integration test: an executable renamed to `.pdf` is rejected by magic-byte detection.
- Integration test: an 11 MB file is rejected; an 11th document is rejected.
- Integration test: professional B cannot fetch professional A's document URL (expect 404).
- Integration test: an unauthenticated request for a document URL is rejected.
- Integration test: an admin can fetch any document URL.
- Integration test: a read URL is rejected after expiry.
- Integration test: uploading while the file is `UNDER_REVIEW` is refused.
- Integration test: an image with GPS EXIF is stored without it.
- Integration test: delete removes the row and the object; a subsequent read is 404.
- Manual check: no storage path or filename appears in any log line.

## Deliverables

- `lexpert_api/core/storage.py` with the interface and the local backend.
- The three document endpoints plus schemas.
- `apps/api/tests/verification/test_documents.py` covering every item above.
- A note in `docs/technical_docs/` on what changes when storage moves to a real object store in Beta.

## Notes

`uploads/` and `storage/` are already git-ignored. Test fixtures must be synthetic documents generated in the test, never real scans of anything.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/kyc-02-document-upload`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
