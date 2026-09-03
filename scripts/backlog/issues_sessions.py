"""Backlog entries for CON, DSP, NOT, CMP and BETA."""

from __future__ import annotations

ISSUES: list[dict[str, object]] = [
    # ------------------------------------------------------------------ CON
    {
        "id": "CON-01",
        "title": "Video provider adapter with room and token issuance",
        "milestone": "MVP",
        "labels": ["consultation", "backend"],
        "size": "M",
        "depends": ["ESC-03"],
        "branch": "feature/con-01-video-provider",
        "goal": (
            "Put the video SDK behind an adapter, the same way ESC-01 does for payments, and "
            "issue the short-lived per-participant tokens that let exactly the right two people "
            "into a consultation. Data residency for video is an open question the feasibility "
            "study flags for later, so the adapter is what keeps the answer changeable."
        ),
        "requirements": [
            "A `VideoProvider` protocol: `create_room(consultation_id)`, "
            "`issue_token(room, participant, role, ttl)`, `end_room(room)`, "
            "`get_room_state(room)`. Provider-agnostic result and error types, exactly as in "
            "ESC-01.",
            "One concrete adapter for the chosen hosted SDK, selected by "
            "`LEXPERT_VIDEO_PROVIDER` through a factory, plus a fake in-memory provider used by "
            "every test. **No test may call the real provider.**",
            "A room is created lazily on the first join, not at booking time, so a cancelled "
            "consultation never provisions one.",
            "Tokens are per participant, per consultation, short-lived (minutes, from settings), "
            "and carry only the permissions that participant needs. A token is never reusable by "
            "the other party.",
            "`POST /api/v1/consultations/{id}/join` returning a room reference and a token, "
            "permitted only to the consultation's client or professional, and only when the "
            "consultation is in `FUNDS_HELD` or `IN_SESSION` and inside the join window "
            "(a configurable number of minutes before the scheduled start until a configurable "
            "number after the scheduled end).",
            "Joining outside the window, joining a cancelled or refunded consultation, and "
            "joining a consultation you are not party to are each refused with distinct, "
            "documented codes.",
            "Provider credentials come from settings and must never appear in a response, a log "
            "line, or an error message.",
            "A contract test suite parameterised over provider implementations, as in ESC-01, so "
            "swapping providers later is a matter of running it against the new adapter.",
        ],
        "validation": [
            "Unit test: the fake provider satisfies the full contract suite.",
            "Unit test: `issue_token` produces distinct tokens for the client and the "
            "professional, with the documented permissions.",
            "Integration test: the client and the professional can each join a `FUNDS_HELD` "
            "consultation inside the window.",
            "Integration test: a third user is refused with 404.",
            "Integration test: joining before the window opens, and after it closes, each return "
            "their documented code.",
            "Integration test: joining a `CANCELLED` consultation is refused.",
            "Integration test: the room is created on first join, and a second join reuses the "
            "same room rather than creating another.",
            "Integration test: an expired token is rejected by the provider fake.",
            "Test asserting no provider credential appears in any response body or captured log "
            "line.",
            "Integration test: an unknown `LEXPERT_VIDEO_PROVIDER` fails at startup.",
        ],
        "deliverables": [
            "`lexpert_api/consultation/provider.py`, `providers/<sdk>.py`, `providers/fake.py`, "
            "`providers/factory.py`.",
            "The join endpoint and its schemas.",
            "`apps/api/tests/consultation/test_video_provider_contract.py` and "
            "`test_join.py`.",
            "`docs/technical_docs/video_provider_boundary.md`, including the data-residency "
            "question left open for Beta.",
        ],
    },
    {
        "id": "CON-02",
        "title": "Session lifecycle and the SESSION_ENDED signal into escrow",
        "milestone": "MVP",
        "labels": ["consultation", "escrow", "backend"],
        "size": "L",
        "depends": ["CON-01", "ESC-06"],
        "branch": "feature/con-02-session-lifecycle",
        "goal": (
            "Track who actually joined a consultation and when, decide when it has ended, and "
            "signal that to the escrow so the one-hour hold window starts. This is the join "
            "between the product's two halves, and it is where a bug means either money never "
            "releases or it releases for a consultation that never happened."
        ),
        "requirements": [
            "A `SessionParticipation` record per participant: consultation id, user id, first "
            "joined at, last left at, total connected seconds. Built from provider webhooks where "
            "available and from the join and leave endpoints otherwise.",
            "Webhook endpoint for the provider's participant-joined, participant-left and "
            "room-finished events, with **signature verification** and replay protection. An "
            "unverified webhook is rejected, not processed.",
            "Webhook handling is idempotent: providers redeliver, and a redelivered event must "
            "not double-count participation or re-transition the consultation.",
            "The first join by either party transitions `FUNDS_HELD -> IN_SESSION`.",
            "A consultation ends, transitioning `IN_SESSION -> SESSION_ENDED` and immediately on "
            "to `HOLD_WINDOW`, when either: the professional explicitly ends it "
            "(`POST /api/v1/consultations/{id}/end`), or the provider reports the room finished, "
            "or a fallback sweeper finds a consultation still `IN_SESSION` past its scheduled end "
            "plus a configurable grace period. All three paths converge on one service function.",
            "The fallback sweeper is not optional. A provider webhook that never arrives must not "
            "leave money held forever; this is the failure mode most likely to occur in "
            "production.",
            "Both parties' participation is exposed to ESC-07's no-show determination: no join at "
            "all by a party, past the grace period, is a no-show by that party.",
            "A consultation where **neither** party joined is not released to the professional; "
            "it goes down the no-show path.",
            "`GET /api/v1/consultations/{id}/session` returning the participation summary to the "
            "two parties and to admins.",
            "**No consultation content is recorded.** No transcript, no recording, no chat log. "
            "Only participation timestamps. Note this explicitly in the module docstring; MVP "
            "recording is out of scope and would change the consent requirements entirely.",
        ],
        "validation": [
            "Integration test: the first join moves `FUNDS_HELD -> IN_SESSION` and records "
            "participation.",
            "Integration test: an explicit end moves through `SESSION_ENDED` to `HOLD_WINDOW` "
            "with the expiry set from the hold-window setting.",
            "Integration test: a provider room-finished webhook produces the same result.",
            "Integration test: the sweeper ends a consultation left `IN_SESSION` past its "
            "scheduled end plus grace, with the clock frozen; and does not end one inside the "
            "grace period.",
            "Integration test: a redelivered join webhook does not double-count participation.",
            "Integration test: a redelivered room-finished webhook does not re-transition or "
            "produce a second audit entry.",
            "Integration test: an unsigned or wrongly-signed webhook is rejected with no state "
            "change.",
            "Integration test: a replayed webhook outside the freshness window is rejected.",
            "Integration test: a consultation neither party joined is routed to the no-show path, "
            "not released.",
            "Integration test: a professional no-show (only the client joined) refunds the client "
            "per ESC-07.",
            "Integration test: the end-to-end path, with a frozen clock, from booking through "
            "join, end, hold window and ESC-06 auto-release, leaves a balanced ledger and a "
            "gapless audit chain.",
            "Test asserting no field on any session model can hold consultation content.",
        ],
        "deliverables": [
            "`lexpert_api/consultation/models.py`, `service.py`, `webhooks.py`, "
            "`jobs/session_sweeper.py`.",
            "The end and session endpoints, and the webhook route.",
            "`apps/api/tests/consultation/test_session_lifecycle.py`, `test_webhooks.py`, "
            "`test_end_to_end_flow.py`.",
            "A `## Session lifecycle` section in `docs/technical_docs/escrow_lifecycle.md` "
            "showing all three end paths converging.",
        ],
        "notes": (
            "The end-to-end test in this issue is the closest thing the project has to a proof "
            "that the MVP works. Keep it readable and keep it fast enough to run on every PR; it "
            "is the test most likely to catch a regression in any of the modules it crosses."
        ),
    },
    {
        "id": "CON-03",
        "title": "Consultation room interface with audio-only fallback",
        "milestone": "MVP",
        "labels": ["frontend", "consultation"],
        "size": "L",
        "depends": ["CON-02", "ESC-12"],
        "branch": "feature/con-03-consultation-room-ui",
        "goal": (
            "The screen where the consultation actually happens. Video quality on Tunisian "
            "networks is called out in the feasibility study as a key acceptance criterion, so "
            "graceful degradation is a requirement here rather than a refinement."
        ),
        "requirements": [
            "A waiting room before the join window opens: the countdown, who you are meeting, a "
            "device check for camera and microphone, and what to do if the other party is late.",
            "The room: local and remote video, mute, camera toggle, a connection-quality "
            "indicator, and a visible elapsed timer against the booked duration.",
            "**Audio-only fallback**, both automatic on sustained poor quality and manually "
            "selectable, with a French explanation when it engages. The consultation must remain "
            "usable on a weak mobile connection.",
            "Reconnection handling: a dropped connection attempts to rejoin with visible status, "
            "and the participation record tolerates the gap rather than treating it as a leave.",
            "The professional has an end-consultation control with a confirmation; the client "
            "has a leave control that makes clear the difference between leaving and ending.",
            "After the end: a post-consultation screen explaining the one-hour hold window, when "
            "the professional is paid, and a clear route to raise a dispute (DSP-03) inside that "
            "window.",
            "Permission handling: a browser that denies camera or microphone access gets a "
            "French explanation of how to grant it, not a blank screen.",
            "Mobile-first, since most consultations will happen on a phone: usable controls at a "
            "375px viewport, and the layout must survive an on-screen keyboard appearing.",
            "No recording, no screenshots, and no local persistence of anything from the session. "
            "Nothing about the consultation's content is written anywhere.",
        ],
        "validation": [
            "Component test: the waiting room renders the countdown and the device check, and the "
            "join control enables only inside the window.",
            "Component test: mute and camera toggles call the SDK and reflect state.",
            "Component test: a simulated sustained quality drop switches to audio-only and shows "
            "the explanation.",
            "Component test: manual audio-only selection works and is reversible.",
            "Component test: a simulated disconnect shows reconnecting status and rejoins.",
            "Component test: the professional's end control requires confirmation and calls the "
            "end endpoint once.",
            "Component test: the client's leave control does not call the end endpoint.",
            "Component test: the post-consultation screen explains the hold window and links to "
            "the dispute flow.",
            "Component test: denied media permissions render the explanatory screen.",
            "Test asserting nothing is written to `localStorage`, `sessionStorage` or IndexedDB "
            "during a session.",
            "Manual: hold a real consultation between two devices on a throttled connection and "
            "confirm the audio-only fallback engages and the consultation stays usable.",
        ],
        "deliverables": [
            "`apps/web/src/features/consultation/` with the waiting room, room, controls and "
            "post-consultation screens.",
            "A quality-monitoring hook driving the fallback.",
            "Consultation keys in `fr.ts`.",
            "Component tests covering every item above, plus a note in the PR describing the "
            "manual throttled-network test and its result.",
        ],
    },
    {
        "id": "CON-04",
        "title": "Consent capture and the no-recording policy",
        "milestone": "MVP",
        "labels": ["compliance", "consultation"],
        "size": "S",
        "depends": ["CON-02"],
        "branch": "feature/con-04-consent-capture",
        "goal": (
            "Record that each party consented to a remote consultation, on what terms, and at "
            "what version of those terms. Medical and legal consultations carry professional "
            "confidentiality obligations, and the INPDP requires explicit consent for sensitive "
            "personal data; an unrecorded consent is, for compliance purposes, no consent."
        ),
        "requirements": [
            "A `ConsentRecord`: user id, consultation id, consent type, the version of the "
            "document consented to, granted_at, and the request context (IP and user agent) "
            "captured at the moment of consent.",
            "Consent types the MVP needs: remote-consultation terms, personal-data processing, "
            "and, for the medical vertical, the telemedicine-specific consent the decree implies.",
            "Consent is captured **before** the first join and blocks the join endpoint until "
            "present, for whichever party has not yet given it.",
            "Consent documents are versioned, and the record stores the version. A change to the "
            "terms therefore requires fresh consent rather than silently reinterpreting an old "
            "one.",
            "Consent records are append-only. A withdrawal is a new record, never an edit or a "
            "deletion of the original.",
            "An explicit, stored statement that consultations are **not recorded** in the MVP, "
            "shown as part of the consent copy, so that adding recording in Beta is visibly a "
            "change requiring new consent.",
            "`GET /api/v1/consultations/{id}/consents` for the parties and admins, so a "
            "professional can confirm consent exists before consulting.",
        ],
        "validation": [
            "Integration test: joining without consent is refused with the documented code; "
            "after consent, it succeeds.",
            "Integration test: each party's consent is tracked independently — one party's "
            "consent does not unblock the other.",
            "Integration test: a medical consultation additionally requires the telemedicine "
            "consent; a legal one does not.",
            "Integration test: `UPDATE` and `DELETE` against the consent table, via raw SQL, are "
            "refused.",
            "Integration test: bumping the document version invalidates the old consent for a "
            "new consultation and requires a fresh one.",
            "Integration test: the request context is stored.",
            "Integration test: a third party cannot read the consents.",
            "Component test: the consent screen renders the French copy including the "
            "no-recording statement, and the join control is disabled until it is accepted.",
        ],
        "deliverables": [
            "`lexpert_api/compliance/consent.py` and its models and migration.",
            "The consent capture and read endpoints, and the join-endpoint guard.",
            "Versioned French consent copy in the web catalogue plus a consent screen.",
            "`apps/api/tests/compliance/test_consent.py`.",
            "`docs/technical_docs/consent_and_data_protection.md` listing the consent types, "
            "their versions, and which vertical needs which.",
        ],
    },
    # ------------------------------------------------------------------ DSP
    {
        "id": "DSP-01",
        "title": "Raising a dispute inside the hold window",
        "milestone": "MVP",
        "labels": ["escrow", "backend"],
        "size": "M",
        "depends": ["CON-02", "ESC-06"],
        "branch": "feature/dsp-01-raise-dispute",
        "goal": (
            "Let a client contest a consultation during the one-hour hold window, which pauses "
            "the auto-release and routes the consultation to human mediation. This window is the "
            "reason the escrow exists at all, so the timing rules have to be exact."
        ),
        "requirements": [
            "`Dispute`: id, consultation id, raised-by user id, reason category, a free-text "
            "description, status (`OPEN`, `RESOLVED`), the resolution outcome, resolver id, "
            "raised_at, resolved_at.",
            "Reason categories as an enum: professional did not attend, consultation cut short, "
            "service not as described, technical failure, other. Each with a French label.",
            "`POST /api/v1/consultations/{id}/dispute`, permitted to the **client only**, and "
            "only while the consultation is in `HOLD_WINDOW` and the window has not expired. "
            "Per the feasibility study's recommendation, a dispute must be raised inside the "
            "hour.",
            "Raising a dispute transitions `HOLD_WINDOW -> UNDER_REVIEW`, which is what stops the "
            "ESC-06 auto-release. The two must be verified to interact correctly under a race: a "
            "dispute landing in the same instant the sweeper runs must produce one outcome, not "
            "both.",
            "One open dispute per consultation. A second attempt is a conflict.",
            "A dispute cannot be raised on a consultation already released, refunded or "
            "cancelled; each returns its own documented code.",
            "The description is free text written by a client and may contain sensitive detail. "
            "It must never be logged, and it is readable only by the client, the professional and "
            "admins.",
            "`GET /api/v1/consultations/{id}/dispute` for the parties and admins.",
            "Raising a dispute notifies the professional and the admin queue through the "
            "notification interface.",
        ],
        "validation": [
            "Integration test: a client raises a dispute in `HOLD_WINDOW`; the status becomes "
            "`UNDER_REVIEW` and an audit entry is written.",
            "Integration test: with the clock frozen one second before expiry, a dispute is "
            "accepted; one second after, it is refused.",
            "Race test: the auto-release job and a dispute request against the same consultation "
            "produce exactly one of the two outcomes, never a release **and** an "
            "`UNDER_REVIEW`, and the ledger reflects only what happened.",
            "Integration test: a professional cannot raise a dispute.",
            "Integration test: a second dispute on the same consultation is a conflict.",
            "Integration test: disputing a `RELEASED_TO_PRO` consultation is refused with its own "
            "code, and likewise for `REFUNDED` and `CANCELLED`.",
            "Integration test: a third party cannot read the dispute.",
            "Test asserting the description does not appear in any captured log line.",
            "Integration test: raising a dispute calls the notification interface for the "
            "professional.",
        ],
        "deliverables": [
            "`lexpert_api/disputes/models.py`, `service.py`, `router.py`, `schemas.py`.",
            "The Alembic migration.",
            "`apps/api/tests/disputes/test_raise_dispute.py` including the race test.",
            "Reason categories with French labels in `fr.ts`.",
        ],
    },
    {
        "id": "DSP-02",
        "title": "Admin dispute mediation with release, refund and partial outcomes",
        "milestone": "MVP",
        "labels": ["admin", "escrow", "backend"],
        "size": "M",
        "depends": ["DSP-01"],
        "branch": "feature/dsp-02-dispute-mediation",
        "goal": (
            "The admin's power to resolve a disputed consultation: pay the professional, refund "
            "the client, or split it. The feasibility study leaves partial release and mediation "
            "as policy to define; this issue defines it as a mechanism with an explicit, audited "
            "human decision."
        ),
        "requirements": [
            "`GET /api/v1/admin/disputes` — a paginated queue of open disputes, oldest first, "
            "filterable by status and reason category, showing how long each has been open.",
            "`GET /api/v1/admin/disputes/{id}` — the dispute, the consultation, both parties, the "
            "session participation record from CON-02, the amounts, and the audit trail. The "
            "admin decides from evidence, so it must all be on one screen.",
            "`POST /api/v1/admin/disputes/{id}/resolve` taking an outcome — release in full, "
            "refund in full, or a partial split with an explicit professional amount — plus a "
            "required resolution note.",
            "A partial split is validated to sum exactly to the total held. A split that does not "
            "balance is refused; there is no rounding accommodation.",
            "Resolution transitions `UNDER_REVIEW -> RELEASED_TO_PRO` or "
            "`UNDER_REVIEW -> REFUNDED` through the ESC-03 transition function, posting the "
            "corresponding ledger entries and appending the audit entry with the admin as actor "
            "and the note as the reason.",
            "For a partial outcome, document and implement the ledger posting pattern in "
            "`ledger.md` **before** writing the code, since it is the only posting that splits a "
            "hold three ways.",
            "Resolving an already-resolved dispute is a conflict. A consultation not in "
            "`UNDER_REVIEW` cannot be resolved.",
            "Both parties are notified of the outcome with the resolution note.",
            "Admin-only, via the router-level dependency.",
        ],
        "validation": [
            "Integration test: release in full pays the professional and the platform per the "
            "original split, with balanced ledger entries.",
            "Integration test: refund in full returns everything to the client and leaves the "
            "platform with nothing.",
            "Integration test: a partial split posts the exact stated amounts and balances.",
            "Integration test: a partial split whose amounts do not sum to the total is refused.",
            "Integration test: a resolution without a note is refused.",
            "Integration test: resolving twice is a conflict, and the second attempt posts no "
            "ledger entries.",
            "Integration test: resolving a consultation in `HOLD_WINDOW` (not yet disputed) is "
            "refused.",
            "Integration test: a non-admin is refused on every endpoint.",
            "Integration test: each outcome appends exactly one audit entry with the admin actor "
            "and the note.",
            "Integration test: both parties are notified.",
            "Integration test: after each outcome, the ledger total across all accounts is still "
            "zero.",
        ],
        "deliverables": [
            "`lexpert_api/admin/disputes_router.py` and the mediation service.",
            "The partial-split posting pattern documented in "
            "`docs/technical_docs/ledger.md`.",
            "`apps/api/tests/admin/test_dispute_mediation.py`.",
        ],
    },
    {
        "id": "DSP-03",
        "title": "Dispute screens for the client and the back-office",
        "milestone": "MVP",
        "labels": ["frontend", "admin"],
        "size": "M",
        "depends": ["DSP-02", "CON-03", "ESC-12"],
        "branch": "feature/dsp-03-dispute-ui",
        "goal": (
            "The client's route to raising a dispute in the hour after a consultation, and the "
            "admin's screen for resolving it. The client-side flow has a hard deadline, so the "
            "remaining time has to be visible and honest."
        ),
        "requirements": [
            "On the client's consultation detail, during `HOLD_WINDOW`, a clear dispute entry "
            "point with a **live countdown** of the time remaining. When the window expires, the "
            "control disappears and the screen explains that the funds have been released.",
            "The dispute form: reason category selection with French labels, a description field "
            "with a minimum useful length, and a confirmation step that states plainly what "
            "happens next (review by the platform, payment paused).",
            "After raising it, a status view: raised at, the category, the description, and, once "
            "resolved, the outcome and the resolution note in French.",
            "The countdown must be derived from the server's stored expiry, not from a "
            "client-side clock started at page load. A clock-skewed client must not be shown a "
            "wrong deadline.",
            "Admin dispute queue and detail screens: the queue with age and category, the detail "
            "showing the consultation, both parties, the participation record, the amounts and "
            "the audit trail.",
            "The admin resolution panel: the three outcomes, with the partial option offering an "
            "amount input that validates the split client-side before submitting, a required "
            "note, and a confirmation step. The amounts on both sides of the split are shown as "
            "the admin types.",
            "All copy in French; accessible forms; mobile-first for the client side.",
        ],
        "validation": [
            "Component test: the countdown renders from a server-provided expiry and reaches zero "
            "correctly.",
            "Component test: with the expiry in the past, the dispute control is absent and the "
            "released explanation shows.",
            "Component test: the form blocks submission without a category or with too short a "
            "description.",
            "Component test: submitting calls the endpoint once and shows the status view.",
            "Component test: a resolved dispute renders the outcome and the note.",
            "Component test: the admin queue renders, filters and paginates.",
            "Component test: the partial-split input rejects amounts that do not sum to the "
            "total, before any request is made.",
            "Component test: resolution requires a note and a confirmation.",
            "Manual: raise and resolve a dispute end to end against a running local stack, "
            "checking the ledger and the audit trail afterwards.",
        ],
        "deliverables": [
            "`apps/web/src/features/client/disputes/` and "
            "`apps/web/src/features/admin/disputes/`.",
            "A countdown component driven by a server timestamp, tested.",
            "Dispute keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
    {
        "id": "DSP-04",
        "title": "Ratings and reviews after release",
        "milestone": "MVP",
        "labels": ["backend", "frontend"],
        "size": "M",
        "depends": ["ESC-06", "PRO-02"],
        "branch": "feature/dsp-04-ratings",
        "goal": (
            "Let a client rate a completed consultation, and surface the aggregate on the "
            "professional's profile and in search. The feasibility study ties ratings to trust "
            "and safety and to moderation, so a rating must be tied to a real, paid, completed "
            "consultation and nothing else."
        ),
        "requirements": [
            "`Rating`: consultation id (unique — one rating per consultation), client id, "
            "professional id, a 1-5 score, an optional French comment, created_at.",
            "A rating can only be created by the consultation's client, and only when the "
            "consultation is `RELEASED_TO_PRO`. A refunded, cancelled or disputed-and-refunded "
            "consultation cannot be rated: there is no verified service to rate.",
            "A rating window (for example 30 days after release) after which rating is closed.",
            "Aggregate rating and count stored on the professional's profile, updated on each new "
            "rating, and exposed in the public profile and in search. Recomputing the average "
            "across all ratings on every search query does not scale; a maintained aggregate does "
            "— but it must be derivable, so include a command that recomputes it from the "
            "ratings and a test proving the maintained value matches.",
            "A rating cannot be edited or deleted by the client once submitted. Admins can hide a "
            "rating (a moderation flag) which excludes it from the aggregate but does not delete "
            "it.",
            "Wire the `rating` sort order in PRO-02 to the real aggregate, replacing the hook left "
            "there.",
            "The comment is client-written free text: never logged, and moderated by hiding "
            "rather than editing.",
            "Client-side: a rating prompt on the consultation detail after release, the rating "
            "form, and the display of ratings on the professional's public profile with the "
            "aggregate, the count, and the individual comments.",
        ],
        "validation": [
            "Integration test: the client rates a `RELEASED_TO_PRO` consultation successfully.",
            "Integration test: rating a `REFUNDED`, `CANCELLED` or `HOLD_WINDOW` consultation is "
            "refused, each with its documented code.",
            "Integration test: a second rating on the same consultation is a conflict.",
            "Integration test: the professional, and an unrelated client, cannot rate it.",
            "Integration test: rating after the window closes is refused.",
            "Integration test: a score of 0 and of 6 are both refused.",
            "Integration test: the aggregate updates correctly across several ratings, and the "
            "recompute command produces the identical value.",
            "Integration test: hiding a rating removes it from the aggregate and from the public "
            "list, without deleting the row.",
            "Integration test: sorting search by rating orders correctly, including professionals "
            "with no ratings.",
            "Component test: the rating prompt appears only after release; the form validates and "
            "submits; the profile renders the aggregate and the comments.",
            "Test asserting the comment text does not appear in any captured log line.",
        ],
        "deliverables": [
            "`lexpert_api/profiles/ratings.py`, its models and migration, and the endpoints.",
            "The aggregate recompute command.",
            "The PRO-02 rating sort wired to the real value.",
            "`apps/web/src/features/client/ratings/` and the profile ratings display.",
            "`apps/api/tests/profiles/test_ratings.py` and the component tests.",
        ],
    },
    # ------------------------------------------------------------------ NOT
    {
        "id": "NOT-01",
        "title": "Notification service with email and SMS adapters",
        "milestone": "MVP",
        "labels": ["backend"],
        "size": "M",
        "depends": ["AUT-02"],
        "branch": "feature/not-01-notification-service",
        "goal": (
            "Replace the AUT-02 logging stub with a real notification service: French templates "
            "rendered once and delivered over email or SMS behind adapters. SMS matters "
            "disproportionately here — the feasibility study notes it has the highest open rate "
            "in Tunisia, and it is what will actually get someone to a consultation on time."
        ),
        "requirements": [
            "An `EmailProvider` and an `SmsProvider` protocol, each with one concrete adapter, a "
            "no-op adapter for local development, and a recording fake for tests. Selected by "
            "settings, as with the escrow and video providers.",
            "A template registry: each notification type has a French template per channel, with "
            "a subject where applicable. Templates live in files, not in Python string literals, "
            "and are rendered with escaping appropriate to the channel.",
            "SMS templates must respect the practical single-message length and must be written "
            "as plain text with no HTML entities leaking in. Test the rendered length.",
            "A `NotificationLog` row per send attempt: type, channel, recipient reference, status, "
            "provider reference, attempt count, error, timestamps. **The rendered body is not "
            "stored** — it can contain personal detail, and the type plus the recipient is enough "
            "to debug a delivery.",
            "Retry with backoff on a transient provider failure, a cap on attempts, and a "
            "terminal failed state that is visible to admins.",
            "Sending is asynchronous with respect to the request that triggers it: a failing SMS "
            "provider must never fail a booking. Trigger a background send and let the log carry "
            "the outcome.",
            "Per-user channel preferences, defaulting to both, with a hard rule that "
            "security-relevant notifications (password reset, verification) are always sent "
            "regardless of preference.",
            "Recipient normalisation: Tunisian numbers to E.164, and a rejection path for a "
            "number the provider cannot deliver to.",
            "Replace the AUT-02 stub with this service, leaving the interface unchanged so no "
            "call site moves.",
        ],
        "validation": [
            "Unit test: each template renders with its variables in French, with no unreplaced "
            "placeholders. A test that iterates every registered template and asserts this.",
            "Unit test: every SMS template renders within the tested length limit.",
            "Unit test: the recording fake captures type, channel and recipient for each send.",
            "Integration test: a transient failure retries with backoff and succeeds; the log "
            "shows the attempt count.",
            "Integration test: a persistent failure reaches the cap and lands in the failed "
            "state.",
            "Integration test: a provider raising an exception does not fail the triggering "
            "request.",
            "Integration test: channel preferences suppress a non-security notification and do "
            "**not** suppress a password reset.",
            "Unit test: a local Tunisian number normalises to E.164; an undeliverable number is "
            "rejected with a clear code.",
            "Test asserting no rendered body and no verification token appears in the "
            "notification log or in any captured log line.",
            "Integration test: the AUT-02 flows still work through the new service.",
        ],
        "deliverables": [
            "`lexpert_api/notifications/` with the protocols, adapters, template registry and "
            "log model plus migration.",
            "`lexpert_api/notifications/templates/` with the French templates.",
            "`apps/api/tests/notifications/` covering every item above.",
            "New settings in `.env.example`.",
        ],
    },
    {
        "id": "NOT-02",
        "title": "Lifecycle notifications for the whole consultation journey",
        "milestone": "MVP",
        "labels": ["backend"],
        "size": "M",
        "depends": ["NOT-01", "CON-02", "DSP-02", "ESC-10"],
        "branch": "feature/not-02-lifecycle-notifications",
        "goal": (
            "Trigger the right message at each point in a consultation's life, to the right "
            "party, on the right channel. Reminders in particular are the cheapest available "
            "remedy for the no-show rate the feasibility study names as a KPI to watch."
        ),
        "requirements": [
            "Notifications on: verification approved, rejected or more-info-requested (to the "
            "professional); **consultation requested** (to the professional, stating the "
            "acceptance deadline); **request accepted** (to the client, with the joining "
            "details); **request declined** and **request expired** (to the client, both "
            "stating the full refund); **request withdrawn** (to the professional); a reminder "
            "24 hours before and another 30 minutes before (to both, from settings); "
            "consultation starting now; funds released (to the professional); refund issued "
            "(to the client); dispute raised (to the professional and the admin queue); "
            "dispute resolved (to both); cancellation (to the counterparty).",
            "The new-request notification to the professional is the one that gates the whole "
            "journey: an unnoticed request expires and the client is refunded for a "
            "consultation that could have happened. Send it on both channels and treat SMS as "
            "the primary one.",
            "Reminders are scheduled, deduplicated and idempotent: a reminder is sent exactly "
            "once per consultation per reminder type, even if the scheduler runs twice or is "
            "restarted.",
            "A `PENDING_ACCEPTANCE` consultation gets **no** consultation reminders -- it is "
            "not confirmed. Reminders begin only once the professional has accepted.",
            "A cancelled, declined, expired or refunded consultation stops its pending reminders. "
            "A reminder for a consultation that no longer exists in a joinable state must not "
            "be sent.",
            "Reminders carry the recipient's local time, not UTC and not the professional's zone "
            "for the client. A diaspora client must read the time they will actually join at.",
            "Channel choice per notification type: time-critical ones (reminders, starting now) "
            "prefer SMS; informational ones prefer email; both where it matters.",
            "No notification body contains consultation content, a dispute description, or any "
            "health, legal or financial detail. Reminders name the professional and the time, "
            "nothing more.",
            "An admin view of the notification log, filterable by consultation and status, so a "
            "'I never got the reminder' report is answerable.",
            "Every trigger point is a call from the existing service layer, not a database "
            "trigger or a polling reconciler, except the reminders which are inherently "
            "scheduled.",
        ],
        "validation": [
            "Integration test per notification type: the triggering action results in exactly one "
            "send to the correct party on the correct channel, using the recording fake.",
            "Integration test: running the reminder scheduler twice sends each reminder once.",
            "Integration test: cancelling a consultation prevents its pending reminders, and so "
            "does a decline and an expiry.",
            "Integration test: a `PENDING_ACCEPTANCE` consultation receives no reminders; "
            "after acceptance it does.",
            "Integration test: each of request-received, accepted, declined, expired and "
            "withdrawn sends exactly one notification to the correct party, and the "
            "request-received one goes out on SMS.",
            "Integration test with a frozen clock: the 24-hour and 30-minute reminders fire at "
            "the right times and not before.",
            "Integration test: a reminder to a client in `Europe/Paris` renders the time in that "
            "zone; the same consultation's reminder to the professional renders in "
            "`Africa/Tunis`.",
            "Integration test: a released consultation notifies the professional; a refund "
            "notifies the client.",
            "Integration test: a dispute notifies the professional and produces an admin-queue "
            "notification.",
            "Test asserting no notification body for any type contains a dispute description or a "
            "consultation note (assert over every template's variables).",
            "Integration test: the admin notification-log view filters by consultation and by "
            "status.",
        ],
        "deliverables": [
            "The trigger calls at each service-layer point, plus "
            "`lexpert_api/notifications/jobs/reminders.py`.",
            "The remaining French templates.",
            "The admin notification-log endpoint and view.",
            "`apps/api/tests/notifications/test_lifecycle.py` covering every type.",
            "A table in `docs/technical_docs/notifications.md` mapping event to recipient, "
            "channel and template.",
        ],
    },
    # ------------------------------------------------------------------ CMP
    {
        "id": "CMP-01",
        "title": "Privacy policy, data-processing register and data export",
        "milestone": "MVP",
        "labels": ["compliance", "backend", "docs"],
        "size": "M",
        "depends": ["CON-04", "KYC-02"],
        "branch": "feature/cmp-01-data-protection",
        "goal": (
            "Put the INPDP-facing basics in place: a published privacy policy, an internal "
            "register of what personal data the platform holds and why, and a working data-export "
            "endpoint. The feasibility study lists an INPDP compliance note as a Phase 1 "
            "deliverable; this is its implementation side."
        ),
        "requirements": [
            "A data-processing register in the repository: every category of personal data the "
            "platform stores, where it lives, its legal basis, who can access it, and its "
            "intended retention. Derive it from the actual schema, not from intent — walk the "
            "migrations.",
            "Sensitive categories called out explicitly: KYC-Pro identity documents, and the fact "
            "that a medical consultation's very existence is health data even though its content "
            "is never stored.",
            "A versioned French privacy policy and terms of service, served to the web app so "
            "the version shown matches the version consented to in CON-04.",
            "`GET /api/v1/me/data-export` returning everything the platform holds about the "
            "calling user as a structured file: profile, consultations, ratings, consents, "
            "notification log entries, and a manifest of their KYC documents.",
            "The export excludes the other party's personal data: a client's export names the "
            "professional publicly but does not include the professional's private details, and "
            "vice versa.",
            "Rate-limit the export endpoint and require a fresh authentication (a recent login or "
            "a password re-entry), because it returns everything about an account in one "
            "response.",
            "Deletion is **out of scope here** and belongs to the Beta retention work, because "
            "financial and audit records cannot simply be deleted and the retention rules need "
            "the legal review the study calls for. State this in the policy honestly rather than "
            "promising a deletion the platform cannot yet perform.",
        ],
        "validation": [
            "A test that walks the SQLAlchemy models and fails if a model holding personal data "
            "is absent from the register. This is what keeps the register true as the schema "
            "grows.",
            "Integration test: the export for a seeded client contains their profile, "
            "consultations, ratings and consents.",
            "Integration test: the export contains a document manifest but not the document "
            "bytes.",
            "Integration test: a client's export contains no private field belonging to the "
            "professional they consulted, and the reverse.",
            "Integration test: the export requires fresh authentication and is rate-limited.",
            "Integration test: the policy endpoint returns the same version string that CON-04 "
            "records against a consent.",
            "A review checklist item confirming the register was derived from the migrations, "
            "with the PR listing any model deliberately excluded and why.",
        ],
        "deliverables": [
            "`docs/compliance/data_processing_register.md`.",
            "Versioned French privacy policy and terms, and the endpoint serving them.",
            "The data-export endpoint.",
            "`apps/api/tests/compliance/test_data_export.py` and the register-coverage test.",
            "A `## Data protection` section in `README.md` pointing at the register.",
        ],
        "notes": (
            "This issue produces the artifact a legal advisor reviews. Its value is accuracy, not "
            "completeness of coverage: a register that honestly says 'retention undecided, "
            "pending legal review' for a category is useful, and one that invents a retention "
            "period is worse than useless."
        ),
    },
    {
        "id": "CMP-02",
        "title": "Sensitive-data logging guard",
        "milestone": "MVP",
        "labels": ["compliance", "backend"],
        "size": "M",
        "depends": ["FND-05", "DSP-01"],
        "branch": "feature/cmp-02-logging-guard",
        "goal": (
            "Make it structurally difficult to log something that should never be logged, and "
            "prove in CI that the current code does not. A single logged dispute description or "
            "identity document path is a data-protection incident, and 'we were careful' is not "
            "a control."
        ),
        "requirements": [
            "A redacting log filter applied to the whole application: known-sensitive field names "
            "(password, token, secret, authorization, national id, licence number, dispute "
            "description, consultation note, document path, storage key) are replaced with a "
            "marker wherever they appear in a log record's arguments or extra fields.",
            "A `Sensitive` wrapper type for values that must never be rendered: its `__repr__` "
            "and `__str__` return a marker, so it is safe even in an f-string or a traceback. Use "
            "it for the JWT secret, provider credentials and document storage keys.",
            "Exception handlers must not leak: the error envelope's `details` is built from an "
            "allow-list of safe fields, never from the exception's raw arguments or a database "
            "error's message. A `psycopg` integrity error can contain row values.",
            "Request and response bodies are never logged, at any log level, including debug. If a "
            "developer needs a body while debugging, they do it locally and do not commit it.",
            "A CI check that greps for the patterns that reintroduce this: logging a request "
            "body, logging a whole model instance, an f-string interpolating a known-sensitive "
            "attribute into a log call. Keep the check narrow enough not to produce false "
            "positives that get it disabled.",
            "A documented list of what is considered sensitive, in one place, referenced by both "
            "the filter and the register from CMP-01.",
        ],
        "validation": [
            "Unit test per sensitive field name: a log record containing it is emitted redacted.",
            "Unit test: `repr()` and `str()` of a `Sensitive` value return the marker, and an "
            "f-string interpolation does too.",
            "Unit test: a traceback containing a `Sensitive` value does not reveal it.",
            "Integration test: a database integrity error surfaces as the error envelope with no "
            "row values in `details`.",
            "Integration test: a request with a body is logged with no body content, at debug "
            "level too.",
            "Integration test: raising a dispute logs no part of the description (the DSP-01 test "
            "extended to assert against the whole captured log stream).",
            "Integration test: a KYC document upload logs no filename and no storage key.",
            "The CI check fails on a deliberately added body-logging line and passes on the real "
            "tree.",
            "A full-suite run with log capture, asserting that no captured line matches a set of "
            "canary values seeded into the test data. This is the broadest and most valuable of "
            "these tests.",
        ],
        "deliverables": [
            "`lexpert_api/core/redaction.py` with the filter and the `Sensitive` type.",
            "The error-envelope allow-list in `core/errors.py`.",
            "The CI check script, wired into the `lint-api` job.",
            "`apps/api/tests/core/test_redaction.py` and the suite-wide canary test.",
            "`docs/compliance/sensitive_data.md`.",
        ],
        "notes": (
            "The canary test is the one that will actually catch a future regression: seed "
            "distinctive values into test fixtures for every sensitive field, run the whole suite "
            "with log capture, and fail if any canary appears. It costs one test and covers "
            "every code path the suite exercises."
        ),
    },
    {
        "id": "CMP-03",
        "title": "API documentation and contract tests",
        "milestone": "MVP",
        "labels": ["api", "docs", "test"],
        "size": "M",
        "depends": ["ESC-03", "CON-02", "DSP-02"],
        "branch": "feature/cmp-03-api-contract",
        "goal": (
            "Make the HTTP contract explicit and tested, so the web app can be developed against "
            "a stable surface and a breaking change is caught in CI rather than in the browser. "
            "It is also what a future integration partner will read."
        ),
        "requirements": [
            "Every endpoint documented in OpenAPI: a summary, a description, the response "
            "schemas, and **every** error code it can return, referencing the FND-05 envelope.",
            "A machine-readable list of every error code the API can emit, with its HTTP status "
            "and its French message, generated from the code rather than maintained by hand.",
            "A committed OpenAPI snapshot plus a CI check that regenerates it and fails on an "
            "undeclared difference. A deliberate contract change means updating the snapshot in "
            "the same PR, which makes it visible in review.",
            "Contract tests over the documented critical paths, asserting the response **shape** "
            "rather than reimplementing the business logic: register, publish a profile, list "
            "slots, book, join, end, release, dispute, resolve.",
            "A generated TypeScript client or type definitions for the web app from the OpenAPI "
            "document, so a contract change surfaces as a type error rather than a runtime "
            "surprise.",
            "Documented pagination, filtering and error conventions in one place, so a new "
            "endpoint has a pattern to follow.",
            "The public endpoints (search, slots, profile) are marked as such, and a test asserts "
            "they need no authentication while every other endpoint does — reusing the AUT-03 "
            "route-coverage test.",
        ],
        "validation": [
            "CI check: the generated OpenAPI document matches the committed snapshot.",
            "Test: every route has a summary and at least one documented response, and every "
            "declared error code exists in the error-code registry.",
            "Test: every error code in the registry has a French message in `fr.ts`.",
            "Contract test per critical path: the response matches the documented schema, "
            "including the error envelope on the failure cases.",
            "CI check: the generated TypeScript client compiles and the web app type-checks "
            "against it.",
            "Test: an endpoint whose response schema is changed without updating the snapshot "
            "fails the check.",
            "Test: the public endpoints are reachable unauthenticated; all others are not.",
        ],
        "deliverables": [
            "OpenAPI descriptions across every router, and the error-code registry.",
            "`apps/api/openapi.snapshot.json` and the CI comparison script.",
            "`apps/api/tests/contract/` with the critical-path tests.",
            "The generated client in `apps/web/src/api/generated/` and its generation script.",
            "`docs/technical_docs/api_conventions.md`.",
        ],
    },
    # ------------------------------------------------------------------ BETA
    {
        "id": "BETA-01",
        "title": "Integrate a licensed payment partner behind the EscrowProvider interface",
        "milestone": "Beta",
        "labels": ["escrow", "backend", "compliance"],
        "size": "L",
        "depends": ["ESC-01", "ESC-03", "CMP-03"],
        "branch": "feature/beta-01-payment-partner",
        "goal": (
            "Replace the simulator with a real licensed Tunisian payment provider or bank, so "
            "that actual money moves through the escrow the MVP modelled. This is the single "
            "issue the whole ESC-01 boundary exists to make possible, and it is gated on the "
            "feasibility study's payment and BCT memo confirming which provider can legally "
            "support delayed release and marketplace payouts."
        ),
        "requirements": [
            "**Gate:** the payment and escrow legal memo from feasibility study section 3.2 must "
            "exist and name a provider before this issue starts. Do not begin integration "
            "against a provider whose legal fitness is unconfirmed.",
            "Implement the chosen provider's adapter against the unchanged `EscrowProvider` "
            "protocol, covering pay-in authorization, hold, release to a payee, and refund, with "
            "genuine idempotency keys.",
            "Run the ESC-01 contract test suite against the new adapter in the provider's sandbox. "
            "Passing it unchanged is the acceptance criterion. A change to the protocol required "
            "by the provider is a finding to discuss, not a change to make quietly.",
            "Webhook handling for the provider's asynchronous outcomes, with signature "
            "verification, replay protection and idempotency, following the CON-02 pattern.",
            "Reconciliation: a scheduled job comparing the provider's hold and payout state "
            "against the local ledger, reporting every discrepancy rather than auto-correcting. A "
            "money system that silently self-heals hides the bug that caused the discrepancy.",
            "Remove the MVP simulation notices from the UI, in the same change that makes them "
            "untrue, and not before.",
            "The simulator remains in the codebase and stays the provider used in tests and local "
            "development. It must not be deleted.",
            "A documented, tested rollback: how to return to the simulator if the provider "
            "integration has to be switched off.",
        ],
        "validation": [
            "The ESC-01 contract suite passes against the real adapter in sandbox, unchanged.",
            "Sandbox end-to-end: book, hold, consult, auto-release, and confirm the provider "
            "shows the payout and the ledger agrees to the millime.",
            "Sandbox end-to-end: a refund path, likewise reconciled.",
            "Sandbox: a partial dispute resolution reconciles.",
            "Test: an unsigned or replayed provider webhook is rejected.",
            "Test: a redelivered webhook does not double-release.",
            "Test: the reconciliation job detects a deliberately introduced discrepancy and "
            "reports rather than corrects it.",
            "Test: switching `LEXPERT_ESCROW_PROVIDER` back to `simulator` restores the MVP "
            "behaviour with no code change.",
            "Confirmation in the PR that the simulation notices were removed in this change.",
        ],
        "deliverables": [
            "The provider adapter and its webhook handler.",
            "The reconciliation job and its report.",
            "The contract suite run output, attached to the PR.",
            "`docs/technical_docs/escrow_provider_boundary.md` updated with the live provider and "
            "the rollback procedure.",
            "A record of the legal memo that gated this work, referenced from the PR.",
        ],
    },
    {
        "id": "BETA-02",
        "title": "Local payment methods: D17, Flouci, Konnect and Paymee",
        "milestone": "Beta",
        "labels": ["escrow", "frontend", "backend"],
        "size": "L",
        "depends": ["BETA-01"],
        "branch": "feature/beta-02-local-wallets",
        "goal": (
            "Accept the payment methods Tunisians actually use. The feasibility study names low "
            "card penetration and a cash culture as headwinds, and local wallets as the "
            "mitigation; a card-only checkout will not convert."
        ),
        "requirements": [
            "Support the wallet and card rails the chosen partner exposes, each behind the same "
            "pay-in operation so the escrow flow is method-agnostic.",
            "Method selection in checkout with the method's real constraints surfaced (limits, "
            "fees where the user bears them, expected confirmation time).",
            "Asynchronous confirmation: several of these methods confirm out of band, so a "
            "booking must be able to sit in a pending-payment state and either progress to "
            "`FUNDS_HELD` or expire. This is a genuine addition to the state machine and needs "
            "its own transition matrix tests.",
            "A pending-payment expiry that releases the held slot, so an abandoned payment does "
            "not block a professional's calendar.",
            "Per-method failure handling with honest French messaging.",
        ],
        "validation": [
            "Sandbox test per method: a successful pay-in reaches `FUNDS_HELD`.",
            "Test: the pending-payment state transitions are exhaustively covered, as in ESC-03.",
            "Test: an expired pending payment releases the slot and cancels the consultation.",
            "Test: a slot held by a pending payment is not offered to another client.",
            "Test per method: a declined or abandoned payment leaves no ledger movement.",
            "Component test: method selection renders each method's constraints.",
        ],
        "deliverables": [
            "Per-method support in the provider adapter.",
            "The pending-payment state and its expiry job.",
            "Checkout method selection.",
            "Tests as listed above.",
        ],
    },
    {
        "id": "BETA-03",
        "title": "Diaspora payments and foreign-exchange constraints",
        "milestone": "Beta",
        "labels": ["escrow", "compliance", "backend"],
        "size": "L",
        "depends": ["BETA-01"],
        "branch": "feature/beta-03-diaspora-fx",
        "goal": (
            "Let a Tunisian abroad pay a professional at home. The feasibility study identifies "
            "the diaspora as a major demand segment and BCT foreign-exchange controls as the "
            "obstacle, so this is a compliance issue with a technical component rather than the "
            "reverse."
        ),
        "requirements": [
            "**Gate:** written confirmation of a compliant cross-border flow, from the same "
            "advisory work as BETA-01. This cannot be designed from the technical side alone.",
            "Multi-currency pay-in with the exchange rate captured at booking and stored on the "
            "consultation, so the client's total is fixed at the moment they agree to it.",
            "Ledger support for a second currency without breaking the balance invariant: "
            "entries balance within a currency, and conversion is an explicit two-transaction "
            "operation with the rate recorded.",
            "Payout to the professional in dinars regardless of the pay-in currency.",
            "Whatever declarations or limits the confirmed flow requires, enforced in code and "
            "surfaced to the client before they pay.",
            "Startup Act status, if obtained, may change what is permitted — keep the constraints "
            "configurable rather than hard-coded.",
        ],
        "validation": [
            "Test: a multi-currency consultation stores the rate and the total does not move "
            "afterwards.",
            "Test: the ledger balances within each currency, and a conversion is two balanced "
            "transactions with the rate recorded.",
            "Property test: the balance invariant holds per currency across generated "
            "transactions.",
            "Test: a payout is in dinars for a foreign-currency pay-in, and the amounts "
            "reconcile.",
            "Test: each configured limit or declaration requirement is enforced and surfaced.",
            "Sandbox end-to-end for at least one foreign currency.",
        ],
        "deliverables": [
            "Multi-currency ledger support and its migration.",
            "Rate capture and the conversion posting pattern documented in `ledger.md`.",
            "The compliance constraints as configuration.",
            "Tests as listed above, and the legal confirmation referenced from the PR.",
        ],
    },
    {
        "id": "BETA-04",
        "title": "Professional subscription tiers and featured listings",
        "milestone": "Beta",
        "labels": ["backend", "frontend", "escrow"],
        "size": "L",
        "depends": ["BETA-01", "PRO-02"],
        "branch": "feature/beta-04-subscriptions",
        "goal": (
            "The second and third revenue streams from the business model: a premium plan for "
            "professionals with better visibility, analytics and a lower commission, and paid "
            "promotion in search results."
        ),
        "requirements": [
            "Subscription plans with a recurring charge through the payment partner, a lifecycle "
            "(active, past due, cancelled) and a lower commission rate applied to consultations "
            "booked while active.",
            "The commission rate used for a consultation is the one in force at booking, stored "
            "on the consultation, so a later plan change does not retroactively alter a held or "
            "released amount.",
            "Featured placement in PRO-02 search results, clearly and honestly labelled as "
            "promoted. An unlabelled paid ranking is a trust problem for a platform selling "
            "trust.",
            "A professional analytics view: consultation volume, earnings over time, conversion "
            "from profile views to bookings.",
            "Plan changes, cancellation and dunning, each with the corresponding notifications.",
        ],
        "validation": [
            "Test: an active subscription applies the reduced commission to a new booking, and "
            "the stored breakdown reflects it.",
            "Test: cancelling a plan does not change the commission on an existing consultation.",
            "Test: a past-due subscription reverts to the standard commission.",
            "Test: featured results are ranked ahead and are labelled in the response.",
            "Test: the analytics figures match the underlying ledger and consultation data.",
            "Component test: promoted results are visibly labelled.",
        ],
        "deliverables": [
            "Subscription models, the billing integration and its migration.",
            "Featured placement in the search query, with labelling.",
            "The analytics endpoint and view.",
            "Tests as listed above.",
        ],
    },
    {
        "id": "BETA-05",
        "title": "Data retention, deletion and the INPDP compliance package",
        "milestone": "Beta",
        "labels": ["compliance", "backend", "docs"],
        "size": "L",
        "depends": ["CMP-01", "CMP-02"],
        "branch": "feature/beta-05-retention-deletion",
        "goal": (
            "Complete what CMP-01 deliberately left open: how long each category of personal data "
            "is kept, what happens on a deletion request, and how that reconciles with financial "
            "and audit records that cannot be deleted. This needs the legal review the "
            "feasibility study calls for and cannot be decided from the code."
        ),
        "requirements": [
            "**Gate:** a retention schedule reviewed by a Tunisian data-protection advisor, per "
            "category, with its legal basis. Implement the reviewed schedule, not an invented "
            "one.",
            "A deletion request flow that distinguishes what can be erased (profile, biography, "
            "ratings text, uploaded documents past their retention) from what must be retained "
            "(ledger entries, audit chain, the fact a consultation occurred), and pseudonymises "
            "the retained records rather than deleting them.",
            "The audit chain must survive pseudonymisation with its hash verification intact. "
            "This is the hard technical constraint in this issue and it must be solved "
            "deliberately, not discovered late.",
            "Automated retention enforcement: a job deleting KYC documents past their retention "
            "and reporting what it did.",
            "An INPDP notification or registration package, if the reviewed advice says one is "
            "required.",
            "A breach-response runbook.",
        ],
        "validation": [
            "Test: a deletion request erases every erasable category and pseudonymises the rest.",
            "Test: the audit chain still verifies after pseudonymisation.",
            "Test: the ledger still balances after pseudonymisation.",
            "Test: the retention job deletes only documents past retention, with the clock "
            "frozen, and reports its actions.",
            "Test: a deleted user's data is absent from search, from the professional's earnings "
            "view, and from a counterparty's data export.",
            "The register from CMP-01 updated with the reviewed retention periods.",
        ],
        "deliverables": [
            "The deletion and pseudonymisation service, and the retention job.",
            "The reviewed retention schedule in `docs/compliance/`.",
            "The breach-response runbook.",
            "Tests as listed above.",
        ],
    },
    {
        "id": "BETA-06",
        "title": "Observability: structured logging, metrics, tracing and alerting",
        "milestone": "Beta",
        "labels": ["infra", "backend"],
        "size": "M",
        "depends": ["CMP-02"],
        "branch": "feature/beta-06-observability",
        "goal": (
            "Be able to tell, from outside the system, that it is working — and be told when it "
            "is not. The MVP's most dangerous failure is silent: the auto-release job not "
            "running, which strands money without any user-visible error until a professional "
            "complains."
        ),
        "requirements": [
            "Metrics for the things that matter operationally: consultations by state, "
            "auto-release job runs and outcomes, hold-window breaches, provider call latency and "
            "error rates, disputes open and their age, notification delivery failures.",
            "Alerts on the silent failures specifically: the auto-release job not having run "
            "within its expected interval, any consultation past its hold expiry still in "
            "`HOLD_WINDOW`, any ledger imbalance, and any reconciliation discrepancy.",
            "Distributed tracing across a request, with the FND-05 request id as the correlation "
            "key, so a user report maps to a trace.",
            "Log shipping and retention that honours the CMP-02 redaction rules. Shipping logs to "
            "a third party is itself a data-processing activity and belongs in the CMP-01 "
            "register.",
            "A health and readiness surface suitable for an orchestrator, distinguishing 'alive' "
            "from 'able to serve'.",
            "A dashboard covering the escrow lifecycle end to end, because that is what will "
            "actually be watched during the pilot.",
        ],
        "validation": [
            "Test: each metric is emitted on the action it measures.",
            "Test: a ledger imbalance introduced deliberately triggers the alert condition.",
            "Test: a stalled auto-release job triggers the alert condition, with the clock "
            "frozen.",
            "Test: a consultation past its hold expiry still in `HOLD_WINDOW` is detected.",
            "Test: a trace spans a request and carries the request id.",
            "Test: shipped log records are redacted, verified with the CMP-02 canary values.",
            "The log-shipping destination added to the CMP-01 register.",
        ],
        "deliverables": [
            "Metrics instrumentation and the alert rules as code.",
            "Tracing wiring.",
            "The dashboard definition, committed.",
            "Tests as listed above.",
        ],
    },
    {
        "id": "BETA-07",
        "title": "Deployment pipeline, environments and secret management",
        "milestone": "Beta",
        "labels": ["infra", "ci"],
        "size": "L",
        "depends": ["FND-04", "BETA-06"],
        "branch": "feature/beta-07-deploy-pipeline",
        "goal": (
            "Get the application deployed reproducibly to a staging and a production environment, "
            "with migrations applied safely and secrets handled properly. The branch model "
            "already implies the promotion path; this makes it real."
        ),
        "requirements": [
            "Container images for both apps, built in CI, tagged by commit, and reproducible.",
            "Two environments mapped to the branch model: `stable-testing` deploys to staging, "
            "`main` deploys to production.",
            "Migrations run as an explicit, gated step before the new version serves traffic, "
            "with a documented rollback. An automatic migration on application start is how a bad "
            "deploy becomes a data problem.",
            "Secrets from a real secret store, injected at runtime. No secret in an image, in a "
            "repository, or in a CI log. The repository is public, so this is not negotiable.",
            "A smoke test suite run against each environment after deploy, failing the deploy if "
            "the critical path is broken.",
            "Database backups with a **tested** restore. An untested backup is not a backup, and "
            "the ledger is the data that cannot be reconstructed.",
            "A documented deployment and rollback runbook.",
        ],
        "validation": [
            "A deploy to staging from `stable-testing` succeeds and the smoke tests pass.",
            "A deliberately broken smoke test fails the deploy.",
            "A migration failure aborts the deploy and leaves the previous version serving.",
            "A rollback to the previous version succeeds, following the runbook exactly as "
            "written.",
            "A restore from backup into a scratch environment succeeds and the ledger balances "
            "and the audit chain verifies afterwards.",
            "A scan confirming no secret appears in any image layer or CI log.",
        ],
        "deliverables": [
            "Dockerfiles and the build pipeline.",
            "Deployment workflows for both environments.",
            "The smoke test suite.",
            "Backup and restore automation, with the tested restore evidenced in the PR.",
            "`docs/runbooks/deploy.md` and `docs/runbooks/rollback.md`.",
        ],
    },
    {
        "id": "BETA-08",
        "title": "Raise the coverage gate and add load and resilience testing",
        "milestone": "Beta",
        "labels": ["ci", "test"],
        "size": "M",
        "depends": ["BETA-07"],
        "branch": "chore/beta-08-quality-gates",
        "goal": (
            "Ratchet the quality gates now that the codebase can hold them, and find out what "
            "the system does under load and under partial failure before a pilot with real "
            "professionals does it for us."
        ),
        "requirements": [
            "Raise `fail_under` in steps toward 85%, in its own `chore:` PR, with the escrow, "
            "ledger, audit and state-machine modules held to a higher bar than the average.",
            "Per-module coverage thresholds so a well-covered average cannot hide an "
            "under-tested escrow module.",
            "Load testing of the paths that will actually be hit: search, slot computation, "
            "booking, and the auto-release job over a realistic backlog.",
            "Resilience testing: the payment provider unavailable, the video provider "
            "unavailable, the database failing over mid-transaction, and the auto-release job "
            "killed halfway. Assert the system's state afterwards is consistent in every case.",
            "Fix what the resilience tests find, or document each finding as an accepted risk "
            "with a reason. A found-and-ignored inconsistency in a money system is not an "
            "acceptable outcome.",
            "A documented performance baseline, so a later regression is measurable rather than "
            "a matter of opinion.",
        ],
        "validation": [
            "CI enforces the raised global and per-module thresholds.",
            "Load test results documented against the baseline for each path.",
            "Resilience test: the provider unavailable during booking leaves no held funds and no "
            "orphaned consultation.",
            "Resilience test: the auto-release job killed mid-batch leaves every consultation "
            "either fully released or untouched, never partial.",
            "Resilience test: a database failover mid-transition leaves the ledger balanced and "
            "the audit chain gapless.",
            "Every finding either fixed or recorded as an accepted risk with a rationale.",
        ],
        "deliverables": [
            "Raised thresholds in `pyproject.toml` and the per-module configuration.",
            "The load test suite and its baseline document.",
            "The resilience test suite.",
            "`docs/technical_docs/performance_baseline.md` and the risk record.",
        ],
    },
    {
        "id": "BETA-09",
        "title": "Arabic localization alongside French",
        "milestone": "Beta",
        "labels": ["frontend"],
        "size": "L",
        "depends": ["CMP-03"],
        "branch": "feature/beta-09-arabic-localization",
        "goal": (
            "Add Arabic as a second locale, which the feasibility study lists as optional for "
            "later but which materially widens reach. It is a large change because Arabic is "
            "right-to-left, not because the strings are many."
        ),
        "requirements": [
            "A full Arabic catalogue alongside the French one, with the language selectable and "
            "the choice persisted per user.",
            "Right-to-left layout support throughout: logical CSS properties rather than left and "
            "right, mirrored icons where direction carries meaning, and correct bidirectional "
            "handling where Latin text (a professional's name, a currency code) appears inside "
            "Arabic.",
            "Locale-aware formatting for numbers, dates and currency.",
            "Server-side French and Arabic for notifications, driven by the recipient's "
            "preference, extending the NOT-01 template registry rather than duplicating it.",
            "A test that every catalogue key exists in both locales, failing on either a missing "
            "translation or an orphaned key.",
        ],
        "validation": [
            "Test: the key-parity check passes and fails correctly on a deliberately missing key.",
            "Test: switching locale re-renders and persists the choice.",
            "Test: right-to-left layout is applied and no component uses physical left/right "
            "properties.",
            "Test: a Latin name inside an Arabic sentence renders in the correct order.",
            "Test: notification templates render in both locales per the recipient's preference.",
            "Manual: walk the whole client flow in Arabic on a 375px viewport.",
        ],
        "deliverables": [
            "The Arabic catalogue and the locale switcher.",
            "Right-to-left layout support and the physical-property lint rule.",
            "Arabic notification templates.",
            "Tests as listed above.",
        ],
    },
    {
        "id": "BETA-10",
        "title": "Pilot readiness: support tooling and the KPI dashboard",
        "milestone": "Beta",
        "labels": ["admin", "docs", "backend"],
        "size": "M",
        "depends": ["BETA-06", "BETA-07", "E2E-01"],
        "branch": "feature/beta-10-pilot-readiness",
        "goal": (
            "Everything needed to run the supply-first pilot the feasibility study recommends: "
            "onboard a curated set of professionals in one city, support them, and measure "
            "whether it is working against the KPIs the study names."
        ),
        "requirements": [
            "An admin tool for assisted onboarding, so a professional can be walked through "
            "verification by phone during the pilot without an admin ever holding their "
            "credentials or acting as them.",
            "The KPI dashboard the study asks for: GMV, take rate, no-show rate, dispute rate, "
            "professional retention, client repeat rate, and acquisition cost per side where the "
            "data exists.",
            "Support tooling: look up a user, see their consultations and their audit trail, and "
            "act on a specific consultation — every action logged with the acting admin. Support "
            "access is a privileged read of sensitive data and must be as auditable as a money "
            "movement.",
            "Impersonation, if it is built at all, is read-only, time-boxed, consented to by the "
            "user, and loudly audited. If that is not achievable, do not build it.",
            "Extend the E2E-01 demo seeding to cover the pilot scenarios, rather than building a "
            "second seeder. Still entirely synthetic.",
            "An operational runbook for the pilot: what to watch daily, what to do when a dispute "
            "arrives, and how to handle a professional's payout question.",
        ],
        "validation": [
            "Test: each KPI matches a hand-computed value over a seeded dataset.",
            "Test: every support action is recorded with the acting admin and the target.",
            "Test: assisted onboarding never exposes or sets a professional's credentials.",
            "Test: impersonation, if present, is read-only and expires, and a write attempt "
            "during it is refused.",
            "Test: the extended seeding produces a working pilot environment and still contains no "
            "real personal data.",
            "The runbook walked through once with the owner, and corrected from that walkthrough.",
        ],
        "deliverables": [
            "The admin onboarding assistance and support tooling.",
            "The KPI dashboard and its endpoints.",
            "The pilot scenarios added to the E2E-01 seeding command.",
            "`docs/runbooks/pilot_operations.md`.",
        ],
    },
]
