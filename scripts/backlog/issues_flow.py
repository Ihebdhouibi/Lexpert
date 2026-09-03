"""Backlog entries for the request-and-accept flow, its two portal surfaces, and the
end-to-end acceptance suite that proves the whole MVP journey works.

These exist because the MVP's acceptance criterion is a demonstrable journey -- register,
search, request, accept, consult, get paid -- and the original backlog modelled instant
booking with no professional acceptance step at all.
"""

from __future__ import annotations

ISSUES: list[dict[str, object]] = [
    # ------------------------------------------------------------------ ESC (additions)
    {
        "id": "ESC-10",
        "title": "Consultation request, acceptance, decline and expiry",
        "milestone": "MVP",
        "labels": ["escrow", "backend", "api"],
        "size": "L",
        "depends": ["ESC-03", "SCH-02"],
        "branch": "feature/esc-10-request-acceptance",
        "goal": (
            "A consultation is requested by the client and must be accepted by the "
            "professional before it is confirmed. This issue builds that handshake: the "
            "request endpoint, the professional's accept and decline endpoints, and the job "
            "that expires a request the professional never answers -- each refunding the "
            "client in full where the consultation does not go ahead."
        ),
        "requirements": [
            "The states `PENDING_ACCEPTANCE`, `DECLINED` and `EXPIRED` come from ESC-03's "
            "state machine. This issue builds the endpoints and the job that drive them; it "
            "does not redefine the machine.",
            "`POST /api/v1/consultations` (client) validates the slot, computes the price, "
            "authorizes the escrow hold, and lands the consultation in `PENDING_ACCEPTANCE`. "
            "The client's funds are held from this moment, so the professional is accepting "
            "a consultation that is already funded.",
            "`POST /api/v1/consultations/{id}/accept` (professional only, own consultation "
            "only) transitions `PENDING_ACCEPTANCE -> FUNDS_HELD`. This is the point the "
            "consultation is confirmed and the slot is committed.",
            "`POST /api/v1/consultations/{id}/decline` (professional only) takes an optional "
            "reason from a fixed set of French-labelled categories plus free text, refunds "
            "the client **in full** through the provider, posts the reversing ledger entries, "
            "and transitions to `DECLINED`. A decline never costs the client anything.",
            "A response deadline on every request: `acceptance_deadline_at = requested_at + "
            "LEXPERT_ACCEPTANCE_WINDOW_HOURS`, from settings, and additionally capped so the "
            "deadline never falls after the consultation's own scheduled start.",
            "An expiry job, built on the ESC-06 pattern: select `PENDING_ACCEPTANCE` "
            "consultations past their deadline with `SELECT ... FOR UPDATE SKIP LOCKED`, "
            "refund each in full, transition to `EXPIRED`, process each independently so one "
            "failure does not stop the batch, and make it idempotent so a second run is a "
            "no-op.",
            "A pending request **holds its slot**: the slot is not offered to another client "
            "while a request for it is awaiting acceptance. The ESC-03 overlap constraint "
            "must treat `PENDING_ACCEPTANCE` as non-terminal, and SCH-02 must exclude it.",
            "A client can withdraw a request while it is still `PENDING_ACCEPTANCE`, refunded "
            "in full, transitioning to `CANCELLED`. Withdrawing after acceptance goes through "
            "the ESC-07 cancellation policy instead, because by then the professional has "
            "committed the time.",
            "A professional can only accept if their verification is still `APPROVED` and "
            "their profile still published. A professional suspended between request and "
            "acceptance cannot accept; the request expires and the client is refunded.",
            "Every transition goes through the ESC-03 transition function, so the ledger "
            "posting and the ESC-04 audit entry happen for each of accept, decline, expire "
            "and withdraw, with the correct actor.",
            "Notifications on each event, through the NOT-01 interface: request received "
            "(professional), accepted, declined, expired and withdrawn (the counterparty). "
            "Wired fully in NOT-02.",
        ],
        "validation": [
            "Integration test: a request lands in `PENDING_ACCEPTANCE` with a hold "
            "authorized, a balanced ledger transaction and an audit entry.",
            "Integration test: accept moves to `FUNDS_HELD`; the amounts are unchanged and "
            "no second hold is authorized.",
            "Integration test: decline refunds the client in full, leaves the platform with "
            "nothing, and the ledger nets to zero for that consultation.",
            "Integration test: the same for expiry, with actor `SYSTEM`, and for withdrawal, "
            "with actor `CLIENT`.",
            "Integration test with a frozen clock: the expiry job expires a request one "
            "second past its deadline and leaves one a second before it alone. Test the exact "
            "boundary instant too.",
            "Integration test: the acceptance deadline is capped at the scheduled start when "
            "the configured window would run past it.",
            "Integration test: running the expiry job twice refunds once; the second run "
            "posts no further ledger entries.",
            "Concurrency test: two workers over the same expired set expire each consultation "
            "exactly once.",
            "Concurrency test: an accept and the expiry job racing on the same consultation "
            "produce exactly one outcome, never both a `FUNDS_HELD` and an `EXPIRED`.",
            "Concurrency test: accept and decline racing produce one outcome and one "
            "rejection.",
            "Integration test: while a request is `PENDING_ACCEPTANCE`, its slot is absent "
            "from `GET /professionals/{id}/slots`, and a second request for it is refused "
            "with a conflict.",
            "Integration test: after a decline or an expiry, that slot becomes bookable "
            "again.",
            "Integration test: a different professional cannot accept or decline; a client "
            "cannot accept their own request.",
            "Integration test: accepting an already-accepted, declined or expired "
            "consultation is refused, each with its documented code.",
            "Integration test: a professional whose verification was revoked after the "
            "request cannot accept.",
            "Integration test: withdrawal after acceptance is routed to the ESC-07 policy, "
            "not refunded unconditionally.",
            "Integration test: after every path, the ledger total across all accounts is "
            "still zero.",
        ],
        "deliverables": [
            "The request, accept, decline and withdraw endpoints in "
            "`lexpert_api/booking/router.py`, with their service functions.",
            "`lexpert_api/booking/jobs/expire_requests.py` and its CLI entry point.",
            "The decline-reason categories with French labels in `fr.ts`.",
            "`LEXPERT_ACCEPTANCE_WINDOW_HOURS` added to `.env.example`.",
            "`apps/api/tests/booking/test_request_acceptance.py` and "
            "`test_request_expiry.py`, including the concurrency and boundary tests.",
            "The handshake documented in `docs/technical_docs/escrow_lifecycle.md`, with the "
            "diagram updated.",
        ],
        "notes": (
            "**A design decision worth confirming before implementing.** The escrow hold is "
            "authorized when the client *requests*, not when the professional accepts. That "
            "keeps the feasibility study's promise that the professional sees funds confirmed "
            "before committing time, and it needs no second client action after acceptance. "
            "The cost is that a client's funds are held briefly for a consultation that may "
            "be declined -- which is why a decline, an expiry and a withdrawal all refund in "
            "full, and why the acceptance window is short.\n\n"
            "The alternative -- request first, pay after acceptance -- means the professional "
            "accepts an unfunded consultation and the client has to return to pay, which "
            "loses the escrow guarantee and adds a drop-off point. If the owner prefers it, "
            "say so on this issue before starting: it changes ESC-03, ESC-08 and this issue "
            "together, and is much cheaper to change now than later."
        ),
    },
    {
        "id": "ESC-11",
        "title": "Professional request inbox and consultation dashboard",
        "milestone": "MVP",
        "labels": ["frontend", "escrow", "consultation"],
        "size": "L",
        "depends": ["ESC-10", "PRO-03", "SCH-03"],
        "branch": "feature/esc-11-professional-dashboard",
        "goal": (
            "The professional's home in the application: the requests waiting for their "
            "answer, the consultations coming up, and the route into each session. Without "
            "this a verified professional has nowhere to accept a request from, and the "
            "journey cannot be completed."
        ),
        "requirements": [
            "A dashboard landing screen for `/pro` showing, in priority order: requests "
            "awaiting acceptance (most urgent first by deadline), today's confirmed "
            "consultations, and a summary of what is held and released (reusing the ESC-09 "
            "earnings endpoint rather than a second source of truth).",
            "A request inbox: each pending request shows the client's first name, the "
            "requested date and time **in the professional's timezone**, the duration, what "
            "they will earn net of commission, and a live countdown to the acceptance "
            "deadline.",
            "Accept and decline actions on each request. Decline requires a reason category "
            "and asks for confirmation, stating plainly that the client is refunded in full.",
            "An upcoming-consultations list with each consultation's status in French, and a "
            "join control that becomes active only inside the CON-01 join window -- with a "
            "countdown until it does.",
            "A consultation detail view: the client's first name, when, how long, the "
            "amounts, the consent status from CON-04, and the money timeline. It must not "
            "expose the client's contact details.",
            "A past-consultations list with the outcome of each (released, refunded, "
            "disputed) in client-readable French.",
            "Empty states that tell a new professional what to do next: no requests yet "
            "because availability is not set, or because the profile is not published -- "
            "linking to SCH-03 and PRO-03 respectively. This is the screen a professional "
            "sees on day one, and the cold-start problem makes it matter.",
            "The countdown to an acceptance deadline is derived from the server's stored "
            "deadline, never from a clock started at page load.",
            "Polling or refetch-on-focus so a request that arrives while the tab is open "
            "becomes visible without a manual reload.",
            "Mobile-first: a professional will accept requests from a phone.",
            "All copy in French through the catalogue.",
        ],
        "validation": [
            "Component test: the dashboard renders all three sections against a mocked API, "
            "and the request section is ordered by deadline.",
            "Component test: accept calls the endpoint once and the request leaves the inbox.",
            "Component test: decline requires a reason and a confirmation, and states the "
            "full refund.",
            "Component test: the deadline countdown renders from a server timestamp and "
            "reaches zero; an expired request renders as expired rather than actionable.",
            "Component test: the join control is inactive outside the window and active "
            "inside it, with the clock controlled.",
            "Component test: each empty state renders with the correct next-step link, for "
            "each precondition independently.",
            "Component test: the detail view shows no client contact detail.",
            "Component test: times render in the professional's timezone, verified against a "
            "client request made in another zone.",
            "Component test: a 409 on accept (already expired or declined) shows a French "
            "message and refetches.",
            "Manual: accept a real request end to end against a running local stack, then "
            "join the consultation from this screen.",
        ],
        "deliverables": [
            "`apps/web/src/features/professional/dashboard/` with the landing screen, request "
            "inbox, upcoming list and consultation detail.",
            "A reusable server-timestamp countdown component, shared with DSP-03.",
            "Professional dashboard keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
    {
        "id": "ESC-12",
        "title": "Client consultations list and detail",
        "milestone": "MVP",
        "labels": ["frontend", "escrow"],
        "size": "M",
        "depends": ["ESC-10", "ESC-08"],
        "branch": "feature/esc-12-client-consultations",
        "goal": (
            "The client's view of their own consultations: what they have requested, what has "
            "been accepted, what is coming up, and where their money is. DSP-03 and CON-03 "
            "both assume a client consultation detail screen exists; this is the issue that "
            "creates it."
        ),
        "requirements": [
            "A consultations list under the client portal, grouped into awaiting acceptance, "
            "upcoming, and past, each entry showing the professional, the date and time in "
            "the client's timezone, the duration and the total paid.",
            "Status in plain French from the client's point of view -- awaiting the "
            "professional's answer, confirmed, in progress, being reviewed, paid out, "
            "refunded -- never the internal state name.",
            "For a `PENDING_ACCEPTANCE` request: the acceptance deadline countdown, an "
            "explanation that the money is held and fully refunded if the professional does "
            "not accept, and a withdraw action with confirmation.",
            "For a confirmed consultation: a join control active only inside the join window, "
            "with a countdown, and a cancel action that shows the ESC-07 policy outcome -- "
            "what will be refunded and what retained -- **before** the client confirms.",
            "For a consultation in `HOLD_WINDOW`: the release countdown and the dispute entry "
            "point from DSP-03.",
            "A detail view with the money timeline in client-readable French: held on this "
            "date, consultation on this date, released or refunded on this date and why.",
            "The rating prompt from DSP-04 appears here once a consultation is released.",
            "An empty state pointing a new client at search.",
            "The MVP simulation notice wherever an amount is shown.",
            "Mobile-first, French throughout, accessible.",
        ],
        "validation": [
            "Component test: the three groups render and each status maps to its French "
            "client-facing label, with no internal state name reaching the DOM.",
            "Component test: a pending request shows the deadline countdown and the withdraw "
            "action; withdrawing calls the endpoint once after confirmation.",
            "Component test: the cancel flow shows the policy outcome returned by the API "
            "before confirmation, and does not compute it client-side.",
            "Component test: the join control respects the window, with the clock controlled.",
            "Component test: a `HOLD_WINDOW` consultation shows the release countdown and the "
            "dispute entry point.",
            "Component test: the money timeline renders each event in French.",
            "Component test: the rating prompt appears only for a released consultation.",
            "Component test: the empty state renders and links to search.",
            "Component test: times render in the client's timezone including across a DST "
            "boundary.",
            "Manual: walk the whole client side on a 375px viewport, keyboard only.",
        ],
        "deliverables": [
            "`apps/web/src/features/client/consultations/` with the list and detail views.",
            "The client-facing status label mapping, tested.",
            "Client consultation keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
    # ------------------------------------------------------------------ E2E
    {
        "id": "E2E-01",
        "title": "Demo seeding for a reproducible MVP walkthrough",
        "milestone": "MVP",
        "labels": ["backend", "test", "infra"],
        "size": "M",
        "depends": ["KYC-06", "PRO-01", "SCH-01"],
        "branch": "feature/e2e-01-demo-seeding",
        "goal": (
            "One command that produces a database you can demonstrate the MVP from: verified "
            "professionals in all three verticals with availability and rates, client "
            "accounts, and consultations sitting in each interesting state. Without it, every "
            "walkthrough and every manual test starts with twenty minutes of clicking."
        ),
        "requirements": [
            "A `seed-demo` management command, idempotent and safe to re-run, which refuses "
            "to run when `LEXPERT_ENV` is `production`.",
            "Professionals: at least two per vertical -- medical, legal, financial -- fully "
            "verified and `APPROVED`, with published profiles, distinct rates, specialities, "
            "cities and languages, and weekly availability that yields bookable slots in the "
            "next few days relative to **now**, not fixed dates that go stale.",
            "One professional per vertical left deliberately in a non-approved state "
            "(`SUBMITTED`, `MORE_INFO_REQUESTED`, `REJECTED`) so the admin review queue and "
            "the invisible-until-approved rule can both be demonstrated.",
            "Clients: several, including one with a foreign timezone so the diaspora case is "
            "visible in the UI, and one with no consultations for the empty state.",
            "Consultations covering every state that can be pre-built: "
            "`PENDING_ACCEPTANCE` (one near its deadline), `FUNDS_HELD` upcoming, "
            "`RELEASED_TO_PRO` past, `REFUNDED`, `DECLINED`, `EXPIRED`, `CANCELLED`, and one "
            "in `UNDER_REVIEW` with an open dispute. Each with its correct ledger entries and "
            "audit chain, produced by calling the real service functions -- never by "
            "inserting rows directly.",
            "**Entirely synthetic data.** No real names, no real licence numbers, no real "
            "identity documents, no real consultation content. Documents are generated PDFs "
            "and images. Passwords are a single well-known development value, and the command "
            "prints the credentials it created.",
            "A `reset-demo` command that tears the demo data down without touching the "
            "schema, so a walkthrough can be repeated from a known state.",
            "The generated ledger must balance and every audit chain must verify -- the seeder "
            "asserting this itself, so bad seed data fails loudly rather than producing a "
            "confusing demo.",
            "Documented in `CONTRIBUTING.md`: how to bring up a full local environment and "
            "seed it, in the order the commands must run.",
        ],
        "validation": [
            "Integration test: the command runs against an empty database and produces the "
            "documented set of users, profiles and consultations.",
            "Integration test: running it twice leaves the same row counts.",
            "Integration test: it refuses to run with `LEXPERT_ENV=production`.",
            "Integration test: after seeding, the ledger total across all accounts is zero and "
            "every consultation's audit chain verifies.",
            "Integration test: every seeded consultation state in the list above exists.",
            "Integration test: the approved professionals appear in search; the non-approved "
            "ones do not.",
            "Integration test: the seeded availability yields bookable slots within the next "
            "seven days, computed relative to the current time.",
            "Integration test: `reset-demo` removes the demo data and leaves the schema and "
            "the reference data intact.",
            "A test asserting no seeded string matches a list of real-data canaries (a real "
            "Tunisian licence-number format, a real name list), so the synthetic-only rule is "
            "enforced rather than trusted.",
        ],
        "deliverables": [
            "`apps/api/src/lexpert_api/seed/demo.py` with the `seed-demo` and `reset-demo` "
            "commands.",
            "Synthetic document generation for the KYC files.",
            "`apps/api/tests/seed/test_demo_seed.py`.",
            "A `## Local demo environment` section in `CONTRIBUTING.md`.",
        ],
        "notes": (
            "Build the seed data by calling the real service functions -- register, submit, "
            "approve, request, accept -- rather than inserting rows. It is slower, and it is "
            "the only way the seeded ledger and audit chain are correct. It also means the "
            "seeder is itself a test of the whole flow, which is why it is worth doing before "
            "E2E-02 rather than after."
        ),
    },
    {
        "id": "E2E-02",
        "title": "End-to-end acceptance suite for the MVP journey",
        "milestone": "MVP",
        "labels": ["test", "ci"],
        "size": "L",
        "depends": ["ESC-11", "ESC-12", "CON-03", "DSP-03", "E2E-01"],
        "branch": "feature/e2e-02-acceptance-suite",
        "goal": (
            "Automate the walkthrough that defines the MVP as done: register, get verified, "
            "search, request, accept, consult, and watch the money release. Every issue so "
            "far tests its own layer; nothing yet drives a real browser through the whole "
            "journey, and that journey is the acceptance criterion."
        ),
        "requirements": [
            "Playwright against a real stack: the API, the web app, PostgreSQL, and the fake "
            "video and simulated escrow providers. Real browser, real HTTP, no mocked API.",
            "**The primary journey, as one test.** A professional registers, submits a "
            "verification file, an admin approves it, the professional publishes a profile and "
            "sets availability; a client registers, searches, finds that professional, "
            "requests a slot and pays into the simulated escrow; the professional accepts; "
            "both join the consultation; the professional ends it; the hold window is "
            "advanced; the auto-release job runs; the professional sees the funds released and "
            "the client can rate. Assert the ledger balances and the audit chain verifies at "
            "the end.",
            "Run that journey **once per vertical** -- medical, legal, financial -- since each "
            "has its own verification rule set, and a rule set that rejects a real "
            "professional is exactly the bug this catches.",
            "The dispute journey: request, accept, consult, end, client raises a dispute "
            "inside the hold window, an admin refunds, the client sees the refund and the "
            "auto-release job leaves it alone.",
            "The rejection journeys, each as its own test: the professional declines (client "
            "refunded in full); the request expires unanswered (client refunded); the client "
            "withdraws before acceptance; the client cancels after acceptance and the ESC-07 "
            "policy outcome is what the UI showed them beforehand.",
            "The invisibility rule: a professional whose verification is not `APPROVED` cannot "
            "be found in search and cannot be booked by URL manipulation.",
            "Time control. The suite must advance the clock -- the hold window, the acceptance "
            "deadline -- rather than waiting an hour. Expose a test-only time control or run "
            "the jobs with an injected clock; whichever is chosen, it must be impossible to "
            "enable outside a test environment, and there must be a test asserting that.",
            "Deterministic and independently runnable: each test seeds what it needs and "
            "cleans up, so a single test can be run alone and the suite can be re-run without "
            "a manual reset.",
            "Runs in CI as its own job on every pull request, with a trace and a screenshot "
            "retained on failure. A flaky end-to-end suite gets ignored, so quarantine a flaky "
            "test loudly rather than adding a retry that hides it.",
            "The job name must be added to `.github/ruleset.json` in the same change, or the "
            "drift check in `scripts/check_ruleset_contexts.py` will fail the build.",
            "A short `docs/technical_docs/mvp_acceptance.md` mapping each MVP exit-condition "
            "clause to the test that proves it, so 'is the MVP done?' has a mechanical answer.",
        ],
        "validation": [
            "The primary journey passes for all three verticals.",
            "The dispute journey passes and ends in a refund.",
            "Each of the four rejection journeys passes and ends with the documented refund "
            "amount.",
            "The invisibility test passes, including the direct-URL attempt.",
            "After every journey, an assertion that the ledger nets to zero and each audit "
            "chain verifies.",
            "The suite passes three consecutive CI runs with no retries, evidenced in the "
            "pull request. Flakiness is a finding to fix, not to tolerate.",
            "A single test can be run in isolation and passes.",
            "The suite passes when run twice in a row without resetting the database.",
            "A test asserting the time control cannot be enabled when `LEXPERT_ENV` is "
            "`production`.",
            "`python scripts/check_ruleset_contexts.py` passes with the new job name present "
            "in both the workflow and the ruleset.",
            "Every clause of the MVP milestone's exit condition appears in "
            "`mvp_acceptance.md` against a named test.",
        ],
        "deliverables": [
            "`e2e/` with the Playwright configuration, fixtures and specs.",
            "A compose file or CI service definition bringing up the full stack.",
            "The test-only time control, with its production guard.",
            "The `e2e` CI job, added to `ci.yml` and to `.github/ruleset.json`.",
            "`docs/technical_docs/mvp_acceptance.md`.",
        ],
        "notes": (
            "This is the last MVP issue and the one that says whether the milestone is "
            "finished. Two things make or break it. First, time control: without it the "
            "hold-window tests either sleep for an hour or get skipped, and skipped is what "
            "actually happens. Second, honesty about flakiness -- a retried end-to-end test "
            "is a test that has stopped telling you anything, and in a system that moves money "
            "that is worse than having no test."
        ),
    },
]
