# Xpair-Consultation — Phase 1: Feasibility, Business & Architecture Study

> **Scope of this document:** Conception & theory only. No implementation, no code.
> **Market:** Tunisia 🇹🇳 — Platform UI/UX strictly in **French**.
> **Status:** Draft v0.1 — to be validated with legal, financial and medical advisors.

---

## 0. Executive Summary

**Xpair-Consultation** is a multi-vertical tele-consulting marketplace connecting Tunisian
clients with verified professionals (doctors, lawyers, financial experts, and other licensed
specialists) for paid online consultations (video / audio / chat).

The key differentiator is a **secure escrow ("on-hold") payment system**: when a client confirms
a consultation, the funds are held by a trusted third party and only released to the professional
**1 hour after** the consultation ends — protecting both sides against fraud, no-shows and disputes.

Two distinct access experiences:
- **Client portal** — discover, book, pay, consult, rate.
- **Professional portal** — onboarding & verification, profile, hourly rate, availability/scheduling,
  consultations, payouts.

**Phase 1 verdict (preliminary):** The idea is **feasible and commercially relevant**, but its
success hinges on **two critical constraints specific to Tunisia**:
1. **Payment & escrow regulation** (Central Bank of Tunisia / BCT, foreign-exchange controls,
   licensed payment institutions).
2. **Regulated professions compliance** (telemedicine decree, medical council rules, bar
   association rules for lawyers).

These two items must be de-risked **before** any build phase.

---

## 1. Problem Statement & Value Proposition

### 1.1 The problem
- Booking a specialist in Tunisia is often slow, phone-based, and geographically constrained.
- Rural & under-served regions have limited access to specialists.
- Diaspora Tunisians abroad want consultations with home-country professionals (legal, fiscal,
  medical second opinions) in French/Arabic.
- Clients fear paying upfront online (trust gap); professionals fear no-shows & unpaid sessions.

### 1.2 The value proposition
| Stakeholder | Value delivered |
|---|---|
| **Client** | Fast access to verified experts, transparent pricing, **money protected in escrow**, remote convenience. |
| **Professional** | New revenue channel, automated scheduling & payments, guaranteed payment after session, professional profile. |
| **Platform** | Commission on each consultation + premium features. |

### 1.3 Why the escrow is the core differentiator
Trust is the #1 blocker for online paid services in Tunisia. The escrow model:
- Reassures the client (refund possible if professional no-shows / quality dispute window).
- Reassures the professional (funds confirmed *before* the session starts).
- Gives the platform a controlled dispute-resolution window (the 1-hour hold).

---

## 2. Market Analysis (Tunisia)

### 2.1 Is it unique in Tunisia?
**Short answer:** The *concept* of online consultation is **not new**, but a **multi-vertical
platform (medical + legal + financial) with a built-in escrow** is **largely unaddressed**.

| Segment | Existing players (to verify with field research) | Gap / Opportunity |
|---|---|---|
| Medical teleconsultation / booking | DabaDoc (regional, also Morocco/Algeria), local clinic portals, some hospital pilots | Mostly **appointment booking**, not full escrow-based paid video consults across verticals |
| Legal online advice | Mostly informal (Facebook groups, law-firm websites) | **No structured marketplace** with payment protection |
| Financial / accounting advice | Cabinets' own sites, informal | **Fragmented**, no marketplace |
| Multi-vertical escrow marketplace | — | **Open space — your positioning** |

> ⚠️ **Action required:** Conduct a formal competitor scan (DabaDoc, local startups, Facebook
> communities, Ordre des Médecins listings) and confirm none combine *multi-vertical + escrow*.
> Treat the table above as hypotheses to validate, not confirmed facts.

### 2.2 Market drivers (tailwinds)
- High smartphone & 4G penetration; growing digital-payment adoption (D17, Flouci, e-Dinar).
- Post-COVID normalization of remote consultations.
- Large Tunisian diaspora (France, Germany, Italy, Gulf) needing home-country expertise.
- Government push toward digitalization & telemedicine framework already exists.

### 2.3 Market barriers (headwinds)
- **Low trust** in online payments → escrow mitigates this.
- **Cash culture** & limited credit-card penetration → must support local wallets (D17, Flouci, etc.).
- **Foreign-exchange controls (BCT)** → cross-border payouts to/from diaspora are complex.
- **Regulatory load** for medical & legal advice.
- Habit/behavioral change needed for professionals to adopt online consulting.

### 2.4 Target segmentation
- **Primary (launch):** Urban professionals & middle class in Grand Tunis, Sfax, Sousse.
- **Secondary:** Under-served regions (access value), Tunisian diaspora.
- **Verticals to launch first:** Recommend **medical + legal** first (highest demand, clearest
  pain), add **financial/fiscal** in a later wave.

---

## 3. Legal & Regulatory Feasibility (the make-or-break section)

> ⚠️ This is conception-level guidance, **not legal advice**. Engage a Tunisian lawyer and a
> financial/BCT specialist before committing to the build.

### 3.1 Regulated professions
- **Telemedicine:** Tunisia already has a regulatory framework for telemedicine (governmental
  decree on télémédecine). Practitioners must be registered with the **Conseil National de l'Ordre
  des Médecins de Tunisie (CNOM)**. The platform must verify licenses and respect medical
  confidentiality & prescription rules.
- **Lawyers:** Subject to the **Ordre National des Avocats de Tunisie** rules (advertising,
  fee rules, confidentiality). Online legal advice marketplaces may face professional-conduct
  constraints → verify.
- **Financial / accounting experts:** Verify ordre des experts-comptables / regulatory limits on
  financial advice.

➡️ **Mandatory feature:** a strict **professional verification & onboarding (KYC-Pro)** workflow:
license number, ordre registration, ID, diploma, manual review before activation.

### 3.2 Payments, escrow & the BCT
This is the **highest-risk area**. In Tunisia:
- Acting as an **escrow / fund-holding intermediary** typically requires being (or partnering with)
  a **licensed payment institution / bank** — you generally **cannot legally hold client funds**
  on your own without authorization.
- **Foreign-exchange controls** restrict cross-border money movement (relevant for diaspora).
- Card acceptance goes through **Société Monétique Tunisie (SMT / ClicToPay)**; local wallets
  include **D17 (La Poste)**, **Flouci**, **Konnect**, **Paymee**, **e-Dinar**.

**Implication for the escrow:** You most likely will **not** hold funds yourself. Instead, design
the "on-hold" mechanism as one of these patterns:
1. **Partner-as-escrow (recommended):** Integrate a licensed payment provider/bank that supports
   **marketplace split payments + delayed capture/release** (authorize now, capture/release after
   the 1-hour window).
2. **Wallet/ledger model:** Funds sit in a regulated provider's segregated account; your platform
   maintains a **virtual ledger** that records "held" vs "released" balances and instructs the
   provider when to release.
3. **Pre-authorization + delayed capture:** Card is pre-authorized at booking; captured only after
   the session; released to the pro after the hold window (depends on provider support locally).

➡️ **Phase 1 deliverable:** a **payment & escrow feasibility memo** from a BCT/fintech specialist
confirming which provider(s) can legally support delayed release + marketplace payouts in Tunisia.

### 3.3 Data protection
- Comply with the **INPDP** (Instance Nationale de Protection des Données Personnelles) and Tunisian
  personal-data law. Medical data is sensitive → strong consent, encryption, retention policies.

### 3.4 Company structure
- Choose a legal vehicle (SARL / SUARL or SA), consider eligibility for the **Startup Act** label
  (tax & FX advantages — particularly useful for cross-border diaspora payments).

---

## 4. Business Plan (Conceptual)

### 4.1 Business model & revenue streams
| Stream | Description | Priority |
|---|---|---|
| **Commission** | % fee on each consultation (e.g. 10–20%) taken from the escrow at release. | Core |
| **Subscription (Pro)** | Premium plan for professionals (better visibility, analytics, lower commission). | Phase 2 |
| **Featured listing** | Paid promotion in search results. | Phase 2 |
| **No-show / cancellation fee** | Retained portion when client cancels late. | Core |
| **Value-added services** | E-prescription, document storage, follow-up packages. | Later |

### 4.2 Pricing logic
- Professional sets **hourly rate**; platform computes per-session price (rate × duration).
- Platform adds transparent commission. Client sees **total upfront** before funds are held.

### 4.3 Cost structure (high level)
- **Tech:** development, hosting/cloud, video infrastructure, payment fees.
- **Compliance:** legal, KYC verification, data protection.
- **Acquisition:** marketing to both sides (cold-start / two-sided marketplace problem).
- **Operations:** support, dispute resolution, content moderation.

### 4.4 The "cold start" two-sided marketplace challenge
- Recommend **supply-first**: onboard a curated set of professionals per vertical/city before
  marketing to clients. Consider seeding with a single vertical + single city pilot.

### 4.5 Go-to-market (conceptual)
- **Pilot:** 1 vertical (e.g. medical) + 1 city (Grand Tunis), 20–50 verified professionals.
- Partnerships with clinics, bar associations, professional orders for credibility.
- Diaspora channel via French/Tunisian community groups.

### 4.6 KPIs to define
- GMV (consultation volume × price), take rate, no-show rate, dispute rate, professional retention,
  client repeat rate, CAC/LTV per side.

### 4.7 SWOT
| Strengths | Weaknesses |
|---|---|
| Escrow trust mechanism, multi-vertical, diaspora angle | Regulatory complexity, two-sided cold start, payment friction |
| **Opportunities** | **Threats** |
| Under-served verticals (legal/financial), diaspora demand | BCT/FX constraints, regulated-profession pushback, incumbent (DabaDoc) expansion |

---

## 5. The Escrow ("On-Hold") System — Conceptual Design

### 5.1 Lifecycle (state machine)
```
BOOKED ──(client pays)──► FUNDS_HELD ──(session starts)──► IN_SESSION
   │                          │                                  │
   │                          │                                  ▼
   │                          │                            SESSION_ENDED
   │                          │                                  │
   │                          │                       (1-hour hold window)
   │                          │                                  │
   ▼                          ▼                                  ▼
CANCELLED               REFUNDED ◄──(dispute upheld)──     HOLD_WINDOW
(refund rules)                                                   │
                                          ┌─────────────────────┴─────────────┐
                                   (no dispute)                        (dispute raised)
                                          ▼                                    ▼
                                   RELEASED_TO_PRO                       UNDER_REVIEW
                                                                              │
                                                                  ┌───────────┴───────────┐
                                                                  ▼                       ▼
                                                          RELEASED_TO_PRO            REFUNDED
```

### 5.2 Rules to define (business policy)
- **Hold duration:** 1 hour after `SESSION_ENDED` (configurable).
- **Dispute window:** must the client raise a dispute *within* the 1 hour? (recommended: yes).
- **No-show handling:** professional no-show → auto refund; client no-show → partial/no refund.
- **Cancellation policy:** tiered (free > X hours before; fee inside window).
- **Auto-release:** if no dispute by the end of the hold window → auto-release to professional.
- **Partial release / mediation:** for unresolved disputes, define manual mediation flow.

### 5.3 Trust & safety
- Identity verification on both sides, recording/consent policy, rating system feeding moderation.

> 🔑 **Reminder:** The *technical* hold is enforced by the regulated payment partner (delayed
> capture/release). The platform stores the **ledger + policy**, not the raw funds (subject to §3.2).

---

## 6. Architecture Options (Conceptual)

> No technology lock-in yet. These are candidate patterns to evaluate in Phase 2.

### 6.1 High-level component view
```
                       ┌─────────────────────────────────────────┐
                       │             Xpair-Consultation            │
                       └─────────────────────────────────────────┘
 ┌───────────────┐        ┌───────────────┐         ┌────────────────────┐
 │ Client App     │        │ Professional   │         │ Admin / Back-office │
 │ (web + mobile) │        │ App            │         │ (KYC, disputes)     │
 └──────┬─────────┘        └──────┬─────────┘         └─────────┬──────────┘
        │                         │                              │
        └────────────┬───────────┴───────────────┬──────────────┘
                     ▼                            ▼
              ┌──────────────┐            ┌──────────────────┐
              │  API Gateway  │            │  Auth / Identity  │
              └──────┬───────┘            └──────────────────┘
                     ▼
   ┌───────────────────────────── Core Services ─────────────────────────────┐
   │ Profiles | Scheduling | Booking | Payments&Escrow Ledger | Consultation │
   │ (video)  | Notifications | Ratings/Reviews | Disputes | Admin            │
   └───────────────┬──────────────────────────────┬──────────────────────────┘
                   ▼                               ▼
        ┌────────────────────┐         ┌──────────────────────────────┐
        │ Data stores        │         │ External integrations         │
        │ (DB, cache, files) │         │ Payment provider (escrow),    │
        └────────────────────┘         │ Video (WebRTC/SaaS), SMS/Email │
                                       └──────────────────────────────┘
```

### 6.2 Candidate architectural styles
| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **Modular monolith** | Faster to build, simpler ops, easier for early team | Less independent scaling | **Recommended for MVP** |
| **Microservices** | Independent scaling, team autonomy | Complex ops, premature at MVP | Phase 3+ if scale demands |
| **Serverless-assisted** | Low idle cost, scales with bursts | Vendor lock-in, cold starts | For specific functions (notifications) |

➡️ **Recommendation:** Start as a **modular monolith** with clear internal module boundaries
(profiles, scheduling, payments/escrow, consultation, disputes) so it can be split later.

### 6.3 Key technical building blocks to decide in Phase 2
- **Real-time video:** build on WebRTC vs. use a SaaS (lower regulatory/data-residency burden;
  verify Tunisian data rules) — quality on Tunisian networks is a key acceptance criterion.
- **Payment/escrow integration:** the chosen licensed provider drives much of the design.
- **Scheduling engine:** time zones (diaspora), professional availability, buffers, no-show timers.
- **Notifications:** SMS (high open rate in Tunisia) + email + push.
- **Identity & KYC-Pro:** document upload + manual review workflow.
- **Audit & ledger:** immutable record of every escrow state transition (financial traceability).

### 6.4 Non-functional requirements (to specify)
- **Security/privacy** (medical data), **availability**, **observability**, **scalability**,
  **localization (FR first, AR optional later)**, **mobile-first** (most Tunisian users are mobile).

---

## 7. Phase 1 Deliverables Checklist

| # | Deliverable | Owner | Status |
|---|---|---|---|
| 1 | Market & competitor scan report (validate §2) | Product/Research | ☐ |
| 2 | **Payment & escrow legal/BCT feasibility memo** | Fintech/Legal | ☐ (critical) |
| 3 | Regulated-professions compliance memo (medical/legal/financial) | Legal | ☐ (critical) |
| 4 | Data-protection (INPDP) compliance note | Legal | ☐ |
| 5 | Business model & financial projections (3-yr) | Founders/Finance | ☐ |
| 6 | Escrow business-rules specification (§5) | Product | ☐ |
| 7 | High-level architecture decision record (ADR) | Tech Lead | ☐ |
| 8 | MVP scope definition (verticals, city, feature set) | Product | ☐ |
| 9 | Risk register & mitigation plan | PM | ☐ |
| 10 | Go/No-Go decision document | Founders | ☐ |

---

## 8. Top Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Cannot legally operate escrow | **Blocker** | Partner with licensed payment institution/bank; get written BCT-compliant confirmation early |
| Regulated-profession restrictions | High | KYC-Pro verification, work with the ordres, legal review |
| Two-sided cold start | High | Supply-first pilot, single vertical + city |
| Low online-payment trust | Medium | Escrow + local wallets (D17/Flouci) + clear refund policy |
| FX controls block diaspora | Medium | Startup Act label, compliant cross-border flows, phase diaspora later |
| Video quality on local networks | Medium | Adaptive bitrate, audio-only fallback, SaaS evaluation |
| Data-protection breach (medical) | High | Encryption, consent, INPDP compliance, minimal retention |

---

## 9. Recommended Next Steps (toward Phase 2)

1. **Validate the two critical memos** (§3.2 escrow/BCT, §3.1 professions) — Go/No-Go gate.
2. Run the **competitor scan** to confirm positioning uniqueness.
3. Define the **MVP scope**: which vertical + city, which features are launch-critical.
4. Draft the **escrow business-rules spec** (durations, disputes, cancellation, no-show).
5. Produce **financial projections** and confirm the take-rate model.
6. Only then move to Phase 2: **detailed product spec, UX wireframes, and architecture ADRs.**

---

### Open questions to confirm with you
- Which **verticals** do you want at launch (all, or medical + legal first)?
- **Geography**: Tunisia-only at launch, or include the **diaspora** from day one?
- Do you already have a **target payment partner** in mind (Flouci, Konnect, Paymee, bank)?
- Do you want the next deliverables (e.g., escrow rules spec, MVP scope) **in French** for stakeholders?
```
