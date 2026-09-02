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
            "double-entry ledger, the consultation state machine, the one-hour hold window with "
            "auto-release, cancellation and no-show policy, and the client checkout."
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
