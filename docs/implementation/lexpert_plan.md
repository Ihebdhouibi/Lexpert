# Lexpert — Implementation Plan

> Companion to [lexpert_issues.md](lexpert_issues.md) (the backlog) and
> [../Phase1-Feasibility-Business-Architecture.md](../Phase1-Feasibility-Business-Architecture.md)
> (the feasibility study this plan implements).
>
> This document is the narrative: what gets built, in what order, and why. The backlog is the
> executable version of it.

---

## 1. What the MVP is

A working multi-vertical tele-consulting marketplace for Tunisia, in French, in which:

- A professional in **any of the three verticals** — medical, legal, financial — registers,
  submits a verification file against **their own regulator**, and becomes discoverable only after
  a human admin approves it.
- A client searches for a professional, picks a bookable slot, sees a transparent total
  (hourly rate x duration + platform commission), and confirms.
- Confirming the booking moves money into an **escrow hold** — simulated in code, see section 2.
- Both parties join a **video consultation** at the appointed time.
- One hour after the session ends, if nobody raised a dispute, the funds are **released to the
  professional** automatically. If a dispute was raised, an admin mediates it to a release or a
  refund.
- Every step of that money lifecycle is recorded in a **double-entry ledger** and an **immutable
  audit log**.

The MVP exit condition is that whole path working end to end, with CI green and no real funds
moving.

### Explicitly out of MVP scope

Deferred to Beta, and each has a backlog entry there: a real payment provider, local wallet
methods, cross-border and diaspora flows, professional subscription tiers, featured listings,
Arabic localization, e-prescription, session recording, a mobile app, and the full INPDP retention
and deletion regime.

---

## 2. The two constraints that shape everything

### 2.1 The escrow is simulated, and that is a legal position, not a shortcut

Section 3.2 of the feasibility study is unambiguous: in Tunisia, holding client funds as an
intermediary requires being, or partnering with, a licensed payment institution. Lexpert is
neither, yet. So the MVP does not hold money — it **models** holding money.

The design that makes this safe to build now and cheap to change later:

```
 API domain layer                       Adapter layer
 ---------------                        -------------
 Booking service                        SimulatedEscrowProvider   (MVP)
 Escrow state machine  ---> EscrowProvider ---> KonnectProvider / BankProvider   (Beta)
 Double-entry ledger        (interface)
 Audit log
```

The ledger, the state machine, the hold window, the commission split, the cancellation policy and
the dispute rules are **all real code in the domain layer**, fully tested. They are the part that
encodes Lexpert's business policy, and they do not change when a partner arrives. The only thing
the simulator stands in for is the four operations a licensed provider will eventually perform:
authorize a pay-in, hold it, release it to a payee, refund it.

Two rules follow, and both are enforced in review:

1. **No provider-specific concept may leak into the domain layer**, and no ledger or policy logic
   may live in an adapter. If the Beta swap requires touching the ledger, the boundary was drawn
   wrong.
2. **Every client-facing surface that touches money says, in French and unmissably, that this is
   a simulation and no real payment is taken.** An MVP that looks like it charges cards is a
   regulatory problem, not a demo.

### 2.2 Regulated professions need three different verification workflows

Section 3.1 of the study makes professional verification a mandatory feature rather than a
nice-to-have. It is also not one workflow: each vertical answers to a different body with
different identifiers and different rules.

| Vertical | Regulator | Verified against |
| --- | --- | --- |
| Medical | Conseil National de l'Ordre des Medecins de Tunisie (CNOM) | CNOM registration number, speciality, diploma, national ID |
| Legal | Ordre National des Avocats de Tunisie | Bar registration number and section, sworn-in date, diploma, national ID |
| Financial | Ordre des Experts-Comptables de Tunisie (OECT) | OECT membership number, practice type, diploma, national ID |

The MVP treats these as **three rule sets behind one submission pipeline**: shared document
upload, shared review state machine, shared admin queue — with a per-vertical required-field and
validation set. No regulator exposes a public verification API, so review is **manual by design**:
an admin reads the documents and approves or rejects with a reason. The workflow's job is to make
that review fast, auditable, and impossible to skip.

Hard rule: `verification_status != APPROVED` means the professional does not appear in search, has
no public profile, and cannot be booked. This is enforced in the query layer, not in the UI.

---

## 3. Architecture

Per section 6.2 of the study, a **modular monolith**. One deployable FastAPI application with
enforced internal module boundaries, so a module can later become a service without a rewrite.

```
apps/api/src/lexpert_api/
  core/            config, database session, errors, request ids, security primitives
  identity/        users, roles, authentication, sessions
  verification/    KYC-Pro files, documents, per-regulator rule sets, review workflow
  profiles/        professional public profiles, specialities, search
  scheduling/      availability rules, exceptions, slot computation
  booking/         consultations, lifecycle, cancellation and no-show policy
  escrow/          EscrowProvider interface, simulator, ledger, state machine, audit log
  consultation/    video provider adapter, rooms, tokens, session events
  disputes/        disputes, mediation outcomes
  notifications/   email and SMS adapters, French templates
  admin/           back-office endpoints (KYC queue, dispute mediation)

apps/web/src/
  app/             routing, layout, providers
  i18n/            French catalogue (the only locale in the MVP)
  api/             API client, auth interception
  features/        client portal, professional portal, admin back-office
```

Module rules: a module may depend on `core` and on another module's **public interface** only.
Cross-module database joins are not allowed; go through the owning module. The escrow module is
the strictest — nothing outside it writes to the ledger.

### Decisions already made

| Decision | Choice | Why |
| --- | --- | --- |
| Backend | Python 3.12 + FastAPI | Owner's stack; async, typed, OpenAPI for free |
| Frontend | React + TypeScript + Vite | Owner's stack |
| Database | PostgreSQL 16 | Transactional ledger integrity; row locking for state transitions |
| Migrations | Alembic | Every schema change reviewable |
| Typing | mypy strict from day one | Nearly free greenfield, expensive to retrofit |
| Video | Hosted WebRTC SDK behind an adapter | Fastest to a working consultation; data residency is a Beta question |
| Escrow | Simulator behind `EscrowProvider` | See section 2.1 |
| Money | Integer millimes, never floats | TND has three decimal places; floats do not do money |
| Time | UTC in storage, timezone-aware at the edges | Diaspora clients and Tunisian professionals are in different zones |

### Non-functional requirements taken seriously in the MVP

- **Mobile-first**, per section 6.4 — most Tunisian users are on a phone.
- **French only** in the UI, all copy through the i18n catalogue.
- **Sensitive data discipline**: consultation content, health and legal detail never enter logs,
  error payloads, or analytics.
- **Auditability**: the escrow audit log is append-only and covers every transition.

---

## 4. Order of work

Eleven workstreams. The order is a dependency order, not a schedule; work within a stream can
overlap once its first issue lands.

| # | Workstream | Prefix | What it delivers | Depends on |
| --- | --- | --- | --- | --- |
| 1 | Foundation and infra | `FND` | Both apps build, database and migrations, CI green, app skeletons | — |
| 2 | Identity and accounts | `AUT` | Registration, login, roles, guarded routes | FND |
| 3 | Professional verification | `KYC` | Three regulator workflows, document upload, admin review queue | AUT |
| 4 | Profiles and discovery | `PRO` | Public profiles, search and filtering, profile management | KYC |
| 5 | Scheduling | `SCH` | Availability rules, slot computation, calendars | PRO |
| 6 | Booking and escrow | `ESC` | Ledger, state machine, hold window, auto-release, checkout | SCH |
| 7 | Consultation sessions | `CON` | Video rooms, session lifecycle, `SESSION_ENDED` into escrow | ESC |
| 8 | Disputes and back-office | `DSP` | Disputes, mediation, ratings | ESC, CON |
| 9 | Notifications | `NOT` | Email and SMS, French templates, lifecycle triggers | ESC |
| 10 | Compliance | `CMP` | Consent records, log redaction, contract tests | KYC, CON |
| 11 | Beta | `BETA` | Real payment partner, wallets, FX, subscriptions, ops | MVP complete |

The **critical path to a demonstrable product** is FND -> AUT -> KYC -> PRO -> SCH -> ESC -> CON.
Everything on it must land before anything in DSP, NOT or CMP is worth starting, because those
three decorate a flow that has to exist first.

### The one sequencing trap

`ESC` cannot be built meaningfully before `SCH`, because a booking needs a slot, and the escrow
state machine's timers are anchored to a scheduled end time. Resist the temptation to build the
ledger early in isolation: it is the most interesting module and the easiest one to build against
assumptions that the scheduling work then invalidates. `ESC-01` and `ESC-02` (the interface and
the ledger) are the exception — they have no scheduling dependency and can be done in parallel.

---

## 5. How progress is measured

- Every issue carries **Requirements**, **Validation / test checks** and **Deliverables**. The PR
  is reviewed against those three sections, not against intent.
- The coverage gate starts at **70%** and is ratcheted up in a `chore:` PR once the codebase can
  hold more. A permanently red gate gets disabled instead of respected.
- The MVP milestone is done when its exit condition is demonstrable in one sitting: register a
  professional in each vertical, approve all three, book one, consult, watch the auto-release, and
  dispute another one to a refund.
