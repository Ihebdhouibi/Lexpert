# CLAUDE.md — Working agreement for Lexpert

Guidance for AI coding assistants (Claude Code, Copilot, etc.) and human contributors in this
repo. Read this before making changes.

## Project

Lexpert (product name: Xpair-Consultation) is a multi-vertical tele-consulting marketplace for
the Tunisian market. It connects clients with verified professionals — doctors, lawyers and
financial experts — for paid online consultations over video. Its differentiator is an escrow
("on-hold") payment model: funds are held when a booking is confirmed and released to the
professional one hour after the consultation ends, leaving a dispute window in between.

Currently being built: the **MVP**. Two things about MVP scope are load-bearing and must not be
quietly changed:

1. **The escrow is simulated in code.** There is no licensed payment institution and no real
   money movement. A double-entry ledger and the full state machine live in the API behind an
   `EscrowProvider` interface; the MVP implementation is a simulator. Under Tunisian law the
   platform cannot hold client funds itself (see the feasibility study, section 3.2), so the Beta
   milestone swaps in a licensed partner behind that same interface. **Never write code that
   assumes the platform holds real funds, and never let ledger logic leak into the provider
   adapter or vice versa.**
2. **All three verticals ship in the MVP**, each with its own regulator-specific KYC-Pro
   verification workflow: doctors against the CNOM, lawyers against the Ordre National des
   Avocats de Tunisie, financial experts against the OECT. No professional is discoverable or
   bookable before a human admin has approved their file.
3. **A consultation is requested, not booked.** The client requests a slot and the escrow hold
   is authorized at that moment; the professional then accepts or declines. A decline, an
   expired acceptance window, or a withdrawal before acceptance all refund the client in full
   and free the slot. A professional is never committed to a time they did not agree to, and no
   screen may describe a `PENDING_ACCEPTANCE` consultation as confirmed.

- Feasibility, business and architecture study: `docs/Phase1-Feasibility-Business-Architecture.md`
- Design docs (UI/UX): `docs/design/` — start with `docs/design/design_brief.md`
- Technical design docs: `docs/technical_docs/`
- Implementation plan and issue backlog: `docs/implementation/`
- Collaboration workflow (branches, PRs, rulesets): `docs/team_workflow_playbook.md`

Stack: React + TypeScript with Vite (`apps/web`); Python 3.11 + FastAPI as a modular monolith
(`apps/api`, package `lexpert_api`); PostgreSQL. Video consultations run on a hosted WebRTC SDK
behind a provider adapter.

**The product UI is French only.** All user-facing copy, labels, emails and SMS are in French.
Code, comments, commit messages, issues and documentation are in English.

## Rules (must follow)

1. **No AI attribution.** Never add "Generated with Claude", "Co-authored-by: Claude", Copilot, or
   any similar mention in commit messages, PR descriptions, or code. Describe the change only.
2. **No emojis.** Anywhere: code, comments, commit messages, PR descriptions, docs.
3. **Always end a task with a summary**, covering: What was done, Why, What to expect, and Edge
   cases to handle.
4. **Commit convention:** `<type>(<scope>): <short imperative subject>`. Types: `feat`, `chore`,
   `docs`, `tests`, `bug`, `ci`. Scope is optional and is one of `web`, `api`, `infra`. Keep the
   subject short; add a body only when needed.
5. **Pre-commit must pass** before every commit (ruff + mypy for the API, eslint + prettier for
   the web app, hygiene hooks, conventional commit-msg). Do not bypass with `--no-verify`.
6. **The repository is public.** Never commit secrets, credentials, client data, or real case
   material. Configuration comes from environment variables; `.env` is git-ignored and
   `.env.example` is the committed template.
7. **Every escrow state transition is appended to an immutable audit log.** Financial traceability
   is a regulatory requirement, not a nice-to-have. No transition may be performed by a direct
   `UPDATE` that bypasses the ledger and the audit entry.
8. **Treat health, legal and financial consultation content as sensitive personal data** under
   Tunisian law and the INPDP. Do not log it, do not include it in error payloads, and do not add
   it to analytics events.

## Branching & PRs

- Model: `main` (protected, release) <- `stable-testing` (release candidate) <- `develop`
  (integration) <- `feature/*` or `chore/*` (one branch per issue).
- One issue = one branch = one PR into `develop`. Squash-merge. No direct commits to protected
  branches.
- Use the terminal git CLI for all version-control operations.

## Definition of done

Code + tests, pre-commit clean, CI green, PR links its issue, reviewed.
