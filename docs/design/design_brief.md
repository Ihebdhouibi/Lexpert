# Lexpert — Design Brief

> **Read this first.** It is the grounding for every issue in the `UX` workstream: what the
> product is, who uses it, what is not negotiable, and where to look for good precedent.
>
> It is written for a designer who is early in their career. Nothing here assumes you have
> designed a marketplace or a health product before. Where there is a judgement call, the brief
> says what we recommend **and why**, so you can disagree with the reasoning rather than guess
> at the intent.
>
> If something in here turns out to be wrong once you have talked to real users, say so. This
> document is a starting position, not a specification.

---

## 1. The product in one page

Lexpert (product name **Xpair-Consultation**) is a marketplace where people in Tunisia book paid
video consultations with verified professionals in three fields: **doctors, lawyers and financial
experts**.

The thing that makes it different from a booking site is the **escrow**. When a client requests a
consultation, the money is held rather than paid. It is released to the professional **one hour
after the consultation ends** — leaving an hour in which the client can raise a dispute. If the
professional declines the request, never answers, or the client withdraws, the money goes back in
full.

Read `docs/implementation/lexpert_plan.md` section 1 once for the full journey. The short version:

```
client searches -> requests a slot (money held) -> professional accepts
   -> video consultation -> one hour passes -> professional is paid
```

**In the MVP the escrow is simulated.** No real money moves — the platform is not yet a licensed
payment institution. This has a direct design consequence covered in section 4.

---

## 2. Who uses it

Three audiences with genuinely different needs. Designing one interface for all three would fail
all three.

### The client

Someone with a medical, legal or financial problem. Very likely:

- **On a phone**, on a variable mobile connection, possibly outside a city.
- **Using it once or twice**, not weekly. Nothing can rely on learned behaviour.
- **Anxious.** They have a health worry, a legal dispute, or a tax problem. They are not browsing
  for pleasure.
- **Wary of paying online.** The feasibility study names low trust in online payment as the
  single biggest blocker in this market. Cash culture is strong and card penetration is low.
- Possibly **Tunisian diaspora** in France, Germany, Italy or the Gulf, consulting a professional
  back home, in a different timezone.

What they need: to understand what will happen, what it costs, and where their money is — without
reading anything twice.

### The professional

A doctor, lawyer or expert-comptable using this alongside a real practice. Very likely:

- **Time-poor**, checking between appointments, often on a phone.
- A **repeat user** who will learn the interface, so density is a feature here, not a problem.
- **Cautious about their professional standing.** They are bound by rules from their ordre, and
  they need to be able to decline a consultation outside their competence.

What they need: to see incoming requests and answer them in seconds, and to trust that they will
be paid.

### The admin

Someone at Lexpert reviewing verification files and mediating disputes. Very likely:

- **On a desktop**, doing the same task many times in a row.
- Needs **information density and keyboard efficiency**, not reassurance.

What they need: to compare a claimed licence number against a scanned certificate without
scrolling, and to decide.

> **The most common mistake here** would be to design the admin back-office with the same
> generous spacing and friendly tone as the client app. Back-office tools are read by someone who
> has seen the screen four hundred times. Tighten it up.

---

## 3. What is not negotiable

These come from law, from the market, or from decisions already made. They are constraints, not
preferences.

| Constraint | What it means for design |
| --- | --- |
| **French only** | Every visible word is French. Code and file names stay English. Arabic comes in Beta — see section 7. |
| **Mobile-first** | Design the 375px-wide screen first and widen up. Most users are on a phone, and so is the professional accepting a request. |
| **Three verticals, one system** | A doctor's profile and a lawyer's profile are not the same object, but they must not be three different designs. One component system, vertical-specific content. |
| **WCAG 2.2 AA** | Contrast, focus states, touch targets, keyboard operation. Not optional: older and lower-vision users are a real segment for medical consultations. |
| **Sensitive data** | Health, legal and financial consultation content is sensitive personal data under Tunisian law and the INPDP. It never appears in a notification, a screenshot, or an analytics event. |
| **No dark patterns near money** | Nothing that nudges someone into a payment, hides a cost, or makes cancelling hard. Beyond being wrong, it is a regulatory problem in this domain. |
| **Nothing is "booked" until accepted** | A requested consultation is not confirmed. No screen may imply otherwise. See section 4. |

---

## 4. The trust problem is the design problem

This is the most important section in the brief.

The escrow is implemented in code, but **trust is not created by the implementation — it is
created by the interface**. If a client cannot see where their money is, the escrow provides them
no reassurance whatsoever, and the product's whole differentiator is wasted.

Three things follow.

### 4.1 Money state must be visible, in plain French

At every point a client should be able to answer: *has my money been taken, is it being held, and
when does it go to the professional?* That means:

- A **money timeline** on each consultation: held on this date, consultation on this date,
  released or refunded on this date, and why.
- **Plain-French status words**, never internal state names. The system calls a state
  `PENDING_ACCEPTANCE`; a person needs something closer to *"en attente de la réponse du
  professionnel"*. The word *séquestre* is the technical term for escrow and is **not** the word
  to put in front of a nervous first-time user — part of `UX-09` is finding one that works.
- A visible **countdown** during the one-hour dispute window, so the client knows the window is
  real and finite.

### 4.2 The request is not a booking

Most booking interfaces say *"Confirmed!"* the moment you pay. This one must not, because the
professional has not agreed yet. The confirmation screen after a request has to convey four
things without alarming anyone:

1. Your request has been sent.
2. Your money is held, not spent.
3. The professional has until *(a stated time)* to accept.
4. If they decline or do not answer, you get everything back automatically.

Getting this copy right matters more than getting the layout right.

### 4.3 The MVP must say it is a simulation

Because no real money moves yet, **every client-facing surface that touches money must state
plainly, in French, that this is a demonstration and no real payment is taken.** A visible
banner, not fine print.

And a hard rule: **do not design a fake card-entry form.** A screen that collects card-shaped
data under false pretences is the one thing this MVP must not do, even as a mock. The simulated
payment step should visibly stand in for a real one without imitating it.

---

## 5. Design principles for this product

Five principles, each with a consequence you can check a screen against.

1. **Explain, then ask.** Every consequential action states what will happen before the button,
   not in a toast afterwards. Cancelling shows the refund amount *first*.
2. **Say where the money is.** If a screen involves a consultation, it says the money state.
3. **Never imply more certainty than exists.** A pending request is pending. An unverified
   professional is not "verified soon". An estimate is not a price.
4. **Degrade honestly.** Weak connection, denied camera permission, expired session: each gets a
   real screen explaining what happened and what to do — not a spinner or a generic error.
5. **Density where it is earned.** Reassurance and space for the client. Compression and speed
   for the professional and the admin.

---

## 6. The state matrix — the deliverable that matters most

If you design only the happy path, every screen will be rebuilt. The engineering issues already
require these states; the design has to cover them.

For **every** screen:

| State | Why it matters here |
| --- | --- |
| Loading | Slow mobile connections are normal |
| Empty | A new professional has no requests; a new client has no consultations |
| Error | Network failure must be distinguishable from a rejection |
| Offline | Common on Tunisian mobile networks |
| Permission denied | A client reaching a professional's page |

Plus these, which are specific to Lexpert and are **most of the product**:

| State | Where it appears |
| --- | --- |
| Professional not yet approved | The professional's own portal, before an admin approves them |
| Request pending acceptance | Client consultations, professional inbox |
| Request declined / expired / withdrawn | Client consultations, each with its refund message |
| Confirmed, before the join window opens | Both portals |
| In session | The consultation room |
| Hold window counting down | Client and professional views |
| Disputed / under review | Client, professional, admin |
| Released / refunded | Client and professional history |

> **Practical tip.** Make a single Figma page called *States* per screen, with every state as a
> frame side by side. It is faster to design them together than to discover them one at a time,
> and it is the artifact the implementer will actually work from.

---

## 7. Arabic is coming, so design for it now

Arabic localisation is a Beta issue (`BETA-09`), but two decisions belong to the MVP because
retrofitting them is expensive:

- **Nothing may depend on text direction.** Icons that point, layouts that assume the label is on
  the left, progress that flows left to right — all of these will need to mirror. Note in your
  Figma components which elements mirror and which do not (a logo does not, a back arrow does).
- **Arabic text runs longer or shorter than French unpredictably.** Design components that
  tolerate a label growing by 40% without breaking. No text baked into fixed-width buttons.

The code side of this is already decided: CSS logical properties, enforced by a lint rule.

---

## 8. Where to look — references worth studying

You do not need to invent these patterns. Study these, and take the specific thing named.

| Product | What to take from it |
| --- | --- |
| **Doctolib** (France) | The reference for French-language medical booking. Study the slot picker, the professional profile hierarchy, and how much information they put before the booking button. Closest thing to our client journey in our language. |
| **Qare** / **Livi** (France) | Teleconsultation specifically. Study the pre-call device check and the waiting room — the two screens that decide whether a consultation happens at all. |
| **DabaDoc** (Morocco, Algeria, Tunisia) | Our nearest regional competitor. Study what a Maghreb audience is already used to, and where it stops at appointment booking rather than paid consultation. |
| **GOV.UK Design System** | The best free reference in existence for accessible forms, error messages and plain-language service design. Free, documented, and its reasoning is written down. If you read one thing on this list, read this. |
| **Malt** (France) | A marketplace with a request-and-accept handshake and held payment, much like ours. Study how they phrase a pending request. |
| **Stripe** or **Wise** dashboards | How to communicate money state clearly: pending, held, paid out, refunded, with dates. Directly applicable to section 4.1. |
| **D17**, **Flouci**, **Konnect** | What paying online already looks and feels like to a Tunisian user. Useful for setting expectations, not for copying. |

**How to study them properly:** walk one journey end to end, screenshot every screen including
the errors, and write one sentence per screen on what decision the designer made and why. A
teardown like that is worth more than a mood board.

---

## 9. Guardrails — things not to do

Learned from projects like this going wrong.

- **Do not start with a colour palette or a logo.** Start with flows and states. Visual direction
  comes after you know what screens exist (`UX-03`, not `UX-01`).
- **Do not design a marketing landing page for the client portal.** People arrive with a problem,
  not to be sold to. A big hero image pushes the search box below the fold on a phone.
- **Do not invent forty colours.** A workable set is: one accent, one neutral ramp of about five
  steps, and three semantic colours (success, warning, danger). Money and escrow states can reuse
  the semantic set. More than that and nothing is consistent.
- **Do not design only at desktop width.** If the first artboard is 1440px, the phone layout
  becomes a compromise. Start at 375px.
- **Do not use colour alone to carry meaning.** A status must also have a word or a shape. This
  is a WCAG requirement and it also matters for a small phone screen in sunlight.
- **Do not put consultation content in any design mock.** Use obviously synthetic placeholder
  text. Never a real name, real licence number, or plausible medical detail.
- **Do not design a custom control where a native one works.** A native date input on mobile
  beats a bespoke calendar for accessibility and for a user who has seen it before.
- **Do not hand over a screen without its states.** See section 6.

---

## 10. How your design reaches the code

The handoff is not a screenshot. It is **design tokens**.

Colour, spacing, type scale, radius and motion get defined once in Figma, exported as JSON
(Tokens Studio is the recommended plugin), and turned into CSS custom properties the code reads.
That is what stops the usual drift where the design says 16px and the code ships 15px, and it
means a palette change does not require touching components.

Two conventions make this work, and both are your responsibility:

1. **Name tokens by role, not by appearance.** `color-danger`, not `color-red`. When the palette
   changes, `color-red-but-actually-orange` is how a design system dies.
2. **Name Figma components exactly as the code components are named.** If the code has
   `MoneyInput`, the Figma component is `MoneyInput`. The implementer should never have to guess
   the mapping.

The component foundation in code is **Radix Primitives + Tailwind**: unstyled, accessible
behaviour underneath, our own visual layer on top. Practically, that means the keyboard and
screen-reader behaviour of dialogs, menus and comboboxes is already handled — you design the
appearance and the states, not the interaction mechanics.

---

## 11. A suggested order of work

The `UX` issues are sequenced this way for a reason. If you are new to this, follow the order.

| Week, roughly | What you are doing | Issue |
| --- | --- | --- |
| 1 | Understand the product and the market. Competitor teardowns, a handful of conversations with real people. | `UX-01` |
| 1–2 | Decide the French vocabulary before any screen exists, so it never has to be rewritten. | `UX-09` |
| 2 | Map the screens and the journeys. Boxes and arrows, no styling. | `UX-02` |
| 3 | Visual direction and tokens. Now that you know what screens exist. | `UX-03` |
| 4 | The component library in Figma, every state. | `UX-06` |
| 5–7 | Client journey screens, all states. | `UX-07` |
| 7–9 | Professional and admin portal screens. | `UX-08` |

The engineering side (`UX-04`, `UX-05`, `UX-10`) happens in parallel and depends on your tokens
and component names, which is why those two conventions in section 10 matter early.

---

## 12. Questions to raise rather than guess

Bring these to the technical lead instead of deciding them alone. Each one has a real cost if
guessed wrong.

- What do we call the escrow in French, for a user who has never heard of one?
- Vouvoiement throughout, presumably — confirm it.
- Is a consultation a *consultation* or a *rendez-vous*? They imply different things.
- How do we refer to a professional generically across all three verticals, without a word that
  sounds wrong for one of them?
- Does the platform have any existing brand — a logo, a colour, a name treatment — or is the
  visual direction genuinely open?
- Are we allowed to show a professional's photograph? The ordres have rules about advertising,
  and it varies by profession.
