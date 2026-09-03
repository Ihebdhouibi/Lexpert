"""Workstream metadata for the Lexpert backlog.

The prefix of an issue id (FND, AUT, ...) is the join key between this backlog, the
implementation plan, the GitHub issue title and the suggested branch name.
"""

from __future__ import annotations

WORKSTREAMS: list[dict[str, str]] = [
    {
        "prefix": "FND",
        "title": "Foundation and infra",
        "milestone": "MVP",
        "summary": (
            "Both apps build and are testable, PostgreSQL and Alembic are wired, CI is green on "
            "develop, and each app has a skeleton the feature work can hang off."
        ),
    },
    {
        "prefix": "UX",
        "title": "Design system and UX foundations",
        "milestone": "MVP",
        "summary": (
            "Runs on the designer's track from day one, in parallel with the engineering. "
            "Research and flows before any pixel, then the French copy decisions, then a visual "
            "direction expressed as tokens the code consumes directly, then the component "
            "library and the screens -- every one of them with its states, because the states "
            "are most of this product. Grounding for all of it is docs/design/design_brief.md."
        ),
    },
    {
        "prefix": "AUT",
        "title": "Identity and accounts",
        "milestone": "MVP",
        "summary": (
            "Registration, login and session handling for the three roles (client, professional, "
            "admin), with route guards on both sides."
        ),
    },
    {
        "prefix": "KYC",
        "title": "Professional verification (KYC-Pro)",
        "milestone": "MVP",
        "summary": (
            "One submission pipeline with three regulator-specific rule sets (CNOM, Ordre "
            "National des Avocats, OECT), private document storage, and a manual admin review "
            "queue. No professional is bookable before approval."
        ),
    },
    {
        "prefix": "PRO",
        "title": "Profiles and discovery",
        "milestone": "MVP",
        "summary": (
            "Public professional profiles, the search and filtering surface clients use to find "
            "one, and the professional's own profile management."
        ),
    },
    {
        "prefix": "SCH",
        "title": "Scheduling",
        "milestone": "MVP",
        "summary": (
            "Weekly availability rules with exceptions and buffers, bookable slot computation, "
            "and the two calendar surfaces. Timezone-correct for diaspora clients."
        ),
    },
    {
        "prefix": "ESC",
        "title": "Booking and simulated escrow",
        "milestone": "MVP",
        "summary": (
            "The core of the product: the EscrowProvider interface and its simulator, a "
            "double-entry ledger, the consultation state machine, the request-and-accept "
            "handshake, the one-hour hold window with auto-release, cancellation and no-show "
            "policy, and the two portal surfaces the journey runs through."
        ),
    },
    {
        "prefix": "CON",
        "title": "Consultation sessions",
        "milestone": "MVP",
        "summary": (
            "Video rooms behind a provider adapter, the session lifecycle, and the SESSION_ENDED "
            "signal that starts the escrow hold window."
        ),
    },
    {
        "prefix": "DSP",
        "title": "Disputes, back-office and ratings",
        "milestone": "MVP",
        "summary": (
            "Raising a dispute inside the hold window, admin mediation to a release or refund, "
            "and post-release ratings."
        ),
    },
    {
        "prefix": "NOT",
        "title": "Notifications",
        "milestone": "MVP",
        "summary": (
            "Email and SMS behind adapters with French templates, triggered on every "
            "consultation lifecycle event."
        ),
    },
    {
        "prefix": "CMP",
        "title": "Compliance and hardening",
        "milestone": "MVP",
        "summary": (
            "Consent records, a logging guard that keeps consultation content out of logs, and "
            "contract tests over the documented API surface."
        ),
    },
    {
        "prefix": "E2E",
        "title": "End-to-end acceptance",
        "milestone": "MVP",
        "summary": (
            "A reproducible demo environment and a browser-driven acceptance suite that "
            "drives the whole MVP journey -- register, verify, search, request, accept, "
            "consult, release -- for each of the three verticals. This is what makes the MVP "
            "exit condition a mechanical question rather than an opinion."
        ),
    },
    {
        "prefix": "BETA",
        "title": "Beta",
        "milestone": "Beta",
        "summary": (
            "Replace the simulator with a licensed payment partner, add local payment methods, "
            "handle diaspora flows, and put the operational and compliance foundations in place "
            "for a pilot with real money."
        ),
    },
]
