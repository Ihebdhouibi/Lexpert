"""Delivery phases for the MVP roadmap.

Waves, the critical path, sizes and dependencies are all *derived* from the issue data --
see `roadmap.py`. This file holds the one thing that cannot be: how the workstreams group
into phases a person can plan around, and what each phase is finished enough to demonstrate.

A phase's `checkpoint` is the point of the whole structure. "Eleven issues closed" tells you
nothing about whether the product works; "a doctor, a lawyer and an accountant can each be
verified by an admin" tells you exactly where you are. Write checkpoints as something you can
sit down and watch happen, never as a count.

`prefixes` are workstream prefixes from `workstreams.py`. Every MVP workstream must appear in
exactly one phase; `roadmap.py` fails the build otherwise, so a new workstream cannot quietly
go unplanned.
"""

from __future__ import annotations

PHASES: list[dict[str, object]] = [
    {
        "name": "Foundation",
        "prefixes": ["FND"],
        "what": (
            "The scaffolding every later issue assumes: two apps that build, a database with "
            "migrations, the modular-monolith package layout, and the French-only i18n "
            "catalogue. Nothing here is a feature, which is exactly the point -- no feature "
            "pull request should also have to invent the project structure."
        ),
        "checkpoint": (
            "From a clean clone, both apps build, lint and test; migrations run up and back "
            "down; `/api/v1/health` answers with a live database round-trip."
        ),
    },
    {
        "name": "Accounts",
        "prefixes": ["AUT"],
        "what": (
            "Registration, login and the authorization mechanism every later endpoint leans "
            "on. Phone verification matters more than usual here: SMS has the highest open "
            "rate in Tunisia and is what will actually get someone to a consultation on time."
        ),
        "checkpoint": (
            "Someone can register as a client or a professional, verify their phone by SMS "
            "code, log in, and be refused from a portal that is not theirs."
        ),
    },
    {
        "name": "Verification",
        "prefixes": ["KYC"],
        "what": (
            "The compliance control the whole regulated-professions story rests on, and the "
            "heaviest phase in the MVP. One submission pipeline with three regulator rule sets "
            "behind it. No regulator publishes a verification API, so review is manual by "
            "design -- the workflow's job is to make it fast, auditable and impossible to skip."
        ),
        "checkpoint": (
            "A doctor, a lawyer and an accountant each complete a wizard asking for what "
            "*their* regulator wants, and an admin approves or rejects each with a reason. An "
            "unapproved professional is invisible everywhere."
        ),
    },
    {
        "name": "Discovery",
        "prefixes": ["PRO"],
        "what": (
            "Public profiles, the hourly rate that drives every price the platform computes, "
            "and the search surface where the invisible-until-approved rule is actually "
            "enforced -- in the query itself, not as a filter in Python that some code path can "
            "forget."
        ),
        "checkpoint": (
            "A client searches by vertical, speciality, city, language and price, finds an "
            "approved professional, and sees their rate and the total for each duration. An "
            "unapproved one cannot be found, or reached by guessing the URL."
        ),
    },
    {
        "name": "Scheduling",
        "prefixes": ["SCH"],
        "what": (
            "Where timezone mistakes get baked in for good, so the storage rules are the "
            "substance of it: professional-local times for the weekly rules, UTC for every "
            "instant, conversion at exactly one boundary. A diaspora client in Paris booking a "
            "professional in Tunis is a first-class case, not an edge case."
        ),
        "checkpoint": (
            "A professional sets weekly hours, blocks a holiday and sets a buffer, then sees "
            "the exact slots that produces. A client in `Europe/Paris` sees those slots at the "
            "right local time on both sides of a daylight-saving change."
        ),
    },
    {
        "name": "Money and the handshake",
        "prefixes": ["ESC"],
        "what": (
            "The core of the product and a quarter of the MVP. A double-entry ledger whose "
            "invariant is enforced by the database rather than by good intentions, the "
            "twelve-state consultation machine, the request-and-accept handshake, and the "
            "hour-long hold window that ends in an automatic release. No real money moves: the "
            "simulator sits behind an `EscrowProvider` interface so a licensed partner replaces "
            "it in Beta without the ledger changing."
        ),
        "checkpoint": (
            "A client requests a slot and the funds are held; the professional accepts, "
            "declines or lets it expire; a decline or an expiry refunds in full and frees the "
            "slot. The ledger nets to zero after every path and the audit chain verifies."
        ),
    },
    {
        "name": "Consultation",
        "prefixes": ["CON"],
        "what": (
            "The join between the product's two halves. Video behind an adapter, participation "
            "tracked from provider webhooks, and the `SESSION_ENDED` signal that starts the "
            "hold window. Video quality on Tunisian networks is an acceptance criterion, so "
            "audio-only fallback is a requirement rather than a refinement."
        ),
        "checkpoint": (
            "Both parties join a real video consultation, it degrades to audio on a throttled "
            "connection, the professional ends it, and an hour later the funds land with them "
            "automatically."
        ),
    },
    {
        "name": "Disputes and alerts",
        "prefixes": ["DSP", "NOT"],
        "what": (
            "The hour-long window is the reason the escrow exists, so this is what gives it "
            "teeth: a client can contest inside it, an admin mediates to a release, a refund or "
            "a split. Notifications belong here too -- the request-received SMS gates the whole "
            "journey, since an unnoticed request expires and refunds a consultation that could "
            "have happened."
        ),
        "checkpoint": (
            "A client disputes within the hour, the auto-release stands down, an admin refunds "
            "with a note, both parties are told, and a completed consultation can be rated."
        ),
    },
    {
        "name": "Compliance and acceptance",
        "prefixes": ["CMP", "E2E"],
        "what": (
            "The INPDP-facing basics, a logging guard that makes leaking sensitive content "
            "structurally hard, and the suite that decides whether the MVP is finished. Health, "
            "legal and financial consultation detail is sensitive personal data under Tunisian "
            "law -- \"we were careful\" is not a control."
        ),
        "checkpoint": (
            "A browser drives the whole journey once per vertical, plus the dispute and all "
            "four rejection paths, and `mvp_acceptance.md` maps every clause of the exit "
            "condition to a named test. The milestone is then done by evidence, not opinion."
        ),
    },
]

# Issues worth pulling forward when the critical path is blocked, or if a second person joins.
# Each names why it is safe to start early -- a shallow dependency, not a guess.
EARLY_STARTS: list[dict[str, str]] = [
    {
        "id": "ESC-05",
        "why": (
            "Small, pure and heavily tested. The best first taste of the money rules, and it "
            "unblocks ESC-03."
        ),
    },
    {
        "id": "ESC-01",
        "why": (
            "The provider seam. Needed by ESC-03 but with no scheduling dependency, so it can "
            "be built during phases 3 to 5."
        ),
    },
    {
        "id": "ESC-02",
        "why": (
            "The ledger. Same as ESC-01: on the critical path's shoulder, not in its way."
        ),
    },
    {
        "id": "NOT-01",
        "why": (
            "Only needs AUT-02, and it replaces the logging stub that every later flow calls."
        ),
    },
    {
        "id": "FND-07",
        "why": (
            "The other good first issue, and on the critical path -- so pulling it early helps "
            "twice."
        ),
    },
]

# Decisions that are cheap to change now and expensive later. Surfaced at the top of the
# roadmap so they get settled rather than discovered.
OPEN_DECISIONS: list[dict[str, str]] = [
    {
        "id": "ESC-10",
        "title": "When the escrow hold is authorized",
        "detail": (
            "The hold is authorized when the client *requests*, not when the professional "
            "accepts -- so the professional accepts a consultation that is already funded, and "
            "no second payment step can be abandoned. The cost is money briefly held for a "
            "consultation that may be declined, which is why every non-acceptance path refunds "
            "in full. The alternative is recorded on the issue. Changing it now touches three "
            "issues; after ESC-10, ESC-11 and ESC-12 it touches built code."
        ),
    },
    {
        "id": "ESC-07",
        "title": "The cancellation tiers and percentages",
        "detail": (
            "Business policy the feasibility study leaves open. The mechanism ships with "
            "defaults and the chosen figures go in the pull request description, expecting to "
            "be adjusted in review rather than treated as settled."
        ),
    },
    {
        "id": "BETA-01",
        "title": "Which licensed payment partner",
        "detail": (
            "Gated on the payment and BCT legal memo from feasibility study section 3.2 naming "
            "a provider. BETA-03 is likewise gated on a confirmed compliant cross-border flow. "
            "Neither should start before the advice arrives -- they are legal questions with a "
            "technical component, not the reverse."
        ),
    },
]
