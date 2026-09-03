# Lexpert

Lexpert (product name **Xpair-Consultation**) is a multi-vertical tele-consulting marketplace for
the Tunisian market. It connects clients with verified professionals -- doctors, lawyers and
financial experts -- for paid online consultations over video.

Its differentiator is an escrow ("on-hold") payment model: funds are held when a booking is
confirmed and released to the professional one hour after the consultation ends, leaving a dispute
window in between. That protects the client against no-shows and poor service, and the
professional against unpaid sessions.

The product UI is **French only**. Code, comments, commits and issues are English.

## Status

Pre-MVP. Nothing is implemented yet; the backlog is being worked through.

**In the MVP the escrow is simulated in code.** A double-entry ledger and the full state machine
run in the API behind an `EscrowProvider` interface, with a simulator as the implementation. No
real money moves. Under Tunisian law the platform cannot hold client funds itself, so the Beta
milestone replaces the simulator with a licensed payment partner behind that same interface.

All three verticals ship in the MVP, each with its own regulator-specific professional
verification workflow (CNOM for doctors, Ordre National des Avocats for lawyers, OECT for
financial experts). No professional is bookable before a human admin approves their file.

## Stack

| Part | Choice |
| --- | --- |
| Web | React + TypeScript, Vite (`apps/web`) |
| API | Python 3.11 + FastAPI, modular monolith (`apps/api`, package `lexpert_api`) |
| Database | PostgreSQL 16 |
| Video | Hosted WebRTC SDK behind a provider adapter |

## Documentation

| Document | What it covers |
| --- | --- |
| [docs/Phase1-Feasibility-Business-Architecture.md](docs/Phase1-Feasibility-Business-Architecture.md) | Feasibility, market, legal and regulatory study; escrow state machine; architecture options |
| [docs/implementation/lexpert_plan.md](docs/implementation/lexpert_plan.md) | What is built in what order, and why |
| [docs/implementation/lexpert_issues.md](docs/implementation/lexpert_issues.md) | The issue backlog, one entry per pull request |
| [docs/team_workflow_playbook.md](docs/team_workflow_playbook.md) | Branch model, rulesets, PR review loop |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Setup, commit style, PR checklist |
| [CLAUDE.md](CLAUDE.md) | Working agreement for AI assistants and contributors |

## Milestones

- **MVP** -- the whole journey working end to end: a client registers and searches, requests a
  consultation from a verified professional, the professional accepts, they consult over video,
  and the simulated escrow releases the funds an hour later. All three verticals, with KYC-Pro.
  Proven by a browser-driven acceptance suite, not by hand.
- **Beta** -- licensed payment partner behind the escrow interface, local payment methods,
  diaspora flows, INPDP audit, observability and a deploy pipeline.

## Getting started

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: Python 3.11, Node 20, PostgreSQL 16, then
`pre-commit install && pre-commit install --hook-type commit-msg` once per clone.
