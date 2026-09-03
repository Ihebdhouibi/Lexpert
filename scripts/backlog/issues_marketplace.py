"""Backlog entries for PRO, SCH and ESC."""

from __future__ import annotations

ISSUES: list[dict[str, object]] = [
    # ------------------------------------------------------------------ PRO
    {
        "id": "PRO-01",
        "title": "Professional public profile model and hourly rate",
        "milestone": "MVP",
        "labels": ["backend", "database"],
        "size": "M",
        "depends": ["KYC-06", "FND-07"],
        "branch": "feature/pro-01-profile-model",
        "goal": (
            "Model what a client sees when they look at a professional, and the hourly rate that "
            "drives every price the platform computes. The rate is the input to the escrow "
            "amount, so its type and constraints matter more than the rest of the profile."
        ),
        "requirements": [
            "`ProfessionalProfile`: user id, vertical, display title, French biography, "
            "specialities (from FND-07, at least one), spoken languages, city or governorate, "
            "years of experience, hourly rate in millimes, default consultation duration in "
            "minutes, `is_published`, timestamps.",
            "The hourly rate is an **integer number of millimes**. Never a float. Constrain it to "
            "a sane range from settings (a floor and a ceiling) and reject anything outside it "
            "with a clear code.",
            "Allowed consultation durations are a fixed set (for example 15, 30, 45, 60 minutes) "
            "defined once and shared with SCH-02 and ESC-05. Do not accept an arbitrary integer.",
            "A profile can only be published when the owner's verification is `APPROVED` and the "
            "profile is complete (biography, at least one speciality, a rate, a city). Enforce "
            "in the service layer, not only in the UI.",
            "Unpublishing is always allowed and immediately removes the professional from "
            "search, but must not affect consultations already booked.",
            "`GET /api/v1/professionals/{id}` — the public profile. It returns 404 unless the "
            "profile is published **and** verification is `APPROVED`. It never exposes the "
            "email, the phone, or anything from the verification file.",
            "`GET /api/v1/professionals/me` and `PUT /api/v1/professionals/me` for the owner, "
            "guarded by `require_verified_professional`.",
            "Revoking a verification (an admin moving an approved file back to `REJECTED`) must "
            "unpublish the profile. Cover this with a test even though the admin path for it is "
            "thin in the MVP.",
        ],
        "validation": [
            "Integration test: an approved professional creates, completes and publishes a "
            "profile.",
            "Integration test: publishing with verification `SUBMITTED` is refused.",
            "Integration test: publishing an incomplete profile is refused, naming the missing "
            "fields.",
            "Integration test: a rate of 0, a negative rate, and a rate above the ceiling are "
            "all refused.",
            "Unit test: the rate column round-trips large values exactly, with no floating-point "
            "drift.",
            "Integration test: an unsupported duration (for example 37 minutes) is refused.",
            "Integration test: the public endpoint returns 404 for an unpublished profile and for "
            "a published profile whose verification is not approved.",
            "Integration test: the public response contains no email, phone, or verification "
            "field.",
            "Integration test: revoking verification unpublishes the profile.",
            "Integration test: unpublishing leaves an already-booked consultation intact.",
        ],
        "deliverables": [
            "`lexpert_api/profiles/models.py`, `service.py`, `router.py`, `schemas.py`.",
            "The Alembic migration.",
            "`apps/api/tests/profiles/test_profile.py`.",
            "The shared duration and rate-bound constants, referenced by SCH and ESC.",
        ],
    },
    {
        "id": "PRO-02",
        "title": "Professional search and filtering API",
        "milestone": "MVP",
        "labels": ["api", "backend", "database"],
        "size": "M",
        "depends": ["PRO-01"],
        "branch": "feature/pro-02-search-api",
        "goal": (
            "The query clients use to find a professional. It is the surface where the "
            "'unapproved professionals are invisible' rule is actually enforced, and the one "
            "endpoint most likely to be slow, so both get attention here."
        ),
        "requirements": [
            "`GET /api/v1/professionals` with filters: vertical, speciality, city, language, "
            "minimum and maximum hourly rate, and a free-text query over name, title and "
            "biography.",
            "Only published profiles belonging to `APPROVED` professionals are ever returned. "
            "This is a condition in the query itself, not a post-filter in Python, so no code "
            "path can accidentally omit it.",
            "Sorting: by rate ascending or descending, by years of experience, and by rating once "
            "DSP-04 exists (leave the hook, do not fake the value).",
            "Cursor-based pagination with a stable order. Offset pagination on a list that "
            "changes underneath the user produces duplicates and gaps; do not use it.",
            "Full-text search using PostgreSQL `tsvector` with the French configuration, so "
            "French stemming and accent handling work. A stored generated column plus a GIN "
            "index, not a per-query `to_tsvector`.",
            "Indexes for the filter combinations that will actually be used (vertical plus city, "
            "vertical plus speciality). Include the query plan for the common case in the PR "
            "description.",
            "An `available_from` filter is **out of scope here**; availability arrives in SCH-02 "
            "and joining against it now would be premature. Note the intended integration point "
            "in a comment.",
            "The endpoint is public — no authentication — because clients browse before "
            "registering. It must therefore expose nothing beyond the public profile shape from "
            "PRO-01.",
        ],
        "validation": [
            "Integration test per filter: it narrows the result set correctly.",
            "Integration test: filters combine (vertical plus city plus rate range).",
            "Integration test: an unpublished profile and an unapproved professional are both "
            "absent, tested independently.",
            "Integration test: French full-text search matches with different accents and with a "
            "stemmed form (a search for `avocat` matches `avocats`).",
            "Integration test: cursor pagination over 30 seeded profiles returns each exactly "
            "once across pages, with no duplicates or omissions.",
            "Integration test: inserting a profile mid-pagination does not duplicate an already "
            "returned row.",
            "Integration test: each sort order is correct, including ties.",
            "Integration test: the response contains no private fields.",
            "Performance check: with 1000 seeded profiles, `EXPLAIN ANALYZE` for the common "
            "filter uses the index and the endpoint responds in under 200 ms locally. Paste the "
            "plan in the PR.",
        ],
        "deliverables": [
            "The search endpoint, its query builder and its schemas.",
            "The Alembic migration adding the `tsvector` column and the indexes.",
            "A seeding helper that generates synthetic professionals for tests and local use.",
            "`apps/api/tests/profiles/test_search.py`.",
            "The query plan in the PR description.",
        ],
    },
    {
        "id": "PRO-03",
        "title": "Professional profile management screens",
        "milestone": "MVP",
        "labels": ["frontend"],
        "size": "M",
        "depends": ["PRO-01", "AUT-04"],
        "branch": "feature/pro-03-profile-management-ui",
        "goal": (
            "The professional portal screens for editing a profile, setting an hourly rate, and "
            "publishing. Publishing is the moment a professional becomes bookable, so the screen "
            "has to make the preconditions and the consequence obvious."
        ),
        "requirements": [
            "A profile editor in French: title, biography with a character counter, speciality "
            "multi-select from the reference data, languages, city, years of experience.",
            "A rate editor that takes dinars and millimes in a way a person actually types "
            "(`45,500`) and converts to integer millimes for the API, with the conversion covered "
            "by tests. Show the computed price for each allowed duration underneath, so the "
            "professional sees what a client will pay.",
            "A publish control that lists any unmet precondition (verification not approved, "
            "missing biography, no speciality, no rate) and stays disabled until all are met. "
            "Explain, do not just disable.",
            "A live preview of the public profile as a client will see it.",
            "An unpublish control with a confirmation that states plainly what happens: the "
            "professional disappears from search but existing bookings stand.",
            "Dirty-state protection: navigating away with unsaved changes prompts first.",
            "All copy in French through the catalogue; accessible labelled form controls.",
        ],
        "validation": [
            "Unit test: the dinar-and-millime input converts to integer millimes correctly, "
            "including `45`, `45,5`, `45,500` and `0,001`.",
            "Unit test: the same conversion rejects more than three decimal places.",
            "Component test: the publish control is disabled and lists each unmet precondition, "
            "for each precondition independently.",
            "Component test: with everything met, publishing calls the endpoint once and reflects "
            "the new state.",
            "Component test: unpublish requires confirmation.",
            "Component test: the preview renders the same data the public profile endpoint would "
            "return.",
            "Component test: navigating away dirty prompts; clean does not.",
            "Manual: complete the whole editor on a 375px viewport, keyboard only.",
        ],
        "deliverables": [
            "`apps/web/src/features/professional/profile/` with the editor, rate input, publish "
            "panel and preview.",
            "A reusable money input component, tested.",
            "Profile keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
    {
        "id": "PRO-04",
        "title": "Client search and professional profile pages",
        "milestone": "MVP",
        "labels": ["frontend"],
        "size": "L",
        "depends": ["PRO-02", "FND-06"],
        "branch": "feature/pro-04-client-discovery-ui",
        "goal": (
            "The client-facing discovery experience: a search page with filters and a "
            "professional profile page that leads into booking. This is the top of the client "
            "funnel and the first thing a prospective client sees, so it carries the trust "
            "message from the value proposition."
        ),
        "requirements": [
            "A landing and search page: vertical entry points (medical, legal, financial), a "
            "search input, and a filter panel for speciality, city, language and rate range. On "
            "mobile the filters live behind a sheet rather than consuming the viewport.",
            "Results as cards: name, title, vertical and speciality, city, languages, hourly "
            "rate, and the price for the default duration. Loading skeletons, an explicit empty "
            "state with a suggestion to widen the filters, and an error state with a retry.",
            "Filter and query state lives in the URL, so a search is shareable and the back "
            "button behaves.",
            "Infinite scroll or an explicit load-more against the cursor pagination from PRO-02. "
            "Do not build page-number navigation on a cursor API.",
            "A professional profile page: full biography, specialities, languages, experience, "
            "rate, the price per allowed duration, and a prominent booking call to action "
            "(wired to SCH-04 when it lands, a disabled placeholder until then).",
            "A visible trust panel explaining, in French, that the professional is verified "
            "against their ordre and that payment is held in escrow until after the "
            "consultation. This is the platform's core differentiator; do not bury it.",
            "During the MVP, wherever escrow is explained, state plainly that payments are "
            "simulated and no real money is taken. One clear, unmissable notice.",
            "Mobile-first and accessible: real headings, filters usable by keyboard, results "
            "announced to screen readers when they change.",
        ],
        "validation": [
            "Component test: each filter updates the URL and refetches.",
            "Component test: loading, empty and error states each render.",
            "Component test: load-more appends the next cursor page without duplicating rows.",
            "Component test: reloading a filtered URL restores the exact filter state.",
            "Component test: the profile page renders every field and the per-duration prices, "
            "computed from the same helper the API uses.",
            "Component test: the escrow-simulation notice is present on both the profile page "
            "and any price display.",
            "Component test: a 404 from the profile endpoint renders a not-found screen, not a "
            "crash.",
            "Manual: search, filter and open a profile on a 375px viewport, keyboard only.",
        ],
        "deliverables": [
            "`apps/web/src/features/client/search/` and "
            "`apps/web/src/features/client/professional/`.",
            "Card, filter-panel and trust-panel components.",
            "Search and profile keys in `fr.ts`, including the simulation notice.",
            "Component tests covering every item above.",
        ],
    },
    # ------------------------------------------------------------------ SCH
    {
        "id": "SCH-01",
        "title": "Availability model: weekly rules, exceptions and buffers",
        "milestone": "MVP",
        "labels": ["scheduling", "backend", "database"],
        "size": "L",
        "depends": ["PRO-01"],
        "branch": "feature/sch-01-availability-model",
        "goal": (
            "Model when a professional is available. This is the issue where timezone mistakes "
            "get baked in for good, so the rules about what is stored in what zone are the "
            "substance of it. Diaspora clients in Paris booking a professional in Tunis is a "
            "first-class case, not an edge case."
        ),
        "requirements": [
            "`AvailabilityRule`: professional id, day of week, start time, end time, effective "
            "from and optional effective until. Multiple rules per day are allowed and must not "
            "overlap.",
            "`AvailabilityException`: a specific date made either fully unavailable (a holiday) "
            "or available with different hours, overriding the weekly rule for that date.",
            "Booking constraints on the professional: buffer minutes between consultations, "
            "minimum notice before a booking (for example no bookings inside the next 2 hours), "
            "and a maximum horizon (for example no bookings more than 60 days out).",
            "**Storage and computation rules, stated once and followed everywhere:** the "
            "professional's IANA timezone is stored on their profile; weekly rules are stored as "
            "local times in that zone; every instant (consultation start and end, exception "
            "dates resolved to instants) is stored in UTC as `timestamptz`. Conversion happens "
            "at exactly one boundary.",
            "Handle daylight-saving transitions correctly for clients in European zones: a rule "
            "at 09:00 Tunis time is a different UTC instant in January and in July. Test both.",
            "Overlap validation: creating a rule that overlaps an existing rule for the same day "
            "is refused with a clear code, and so is a rule whose end is not after its start.",
            "`GET/PUT /api/v1/scheduling/me/rules` and "
            "`GET/POST/DELETE /api/v1/scheduling/me/exceptions`, guarded by "
            "`require_verified_professional`.",
            "Changing availability must not invalidate consultations already booked into a "
            "now-unavailable slot. Those stand; the professional cancels them explicitly if "
            "needed, through the ESC-07 policy.",
        ],
        "validation": [
            "Unit test: overlapping rules for the same day are refused; adjacent rules "
            "(09:00-12:00 and 12:00-15:00) are accepted.",
            "Unit test: a rule with end at or before start is refused.",
            "Unit test: a full-day exception removes that date entirely.",
            "Unit test: a modified-hours exception replaces the weekly rule for that date only, "
            "leaving the following week unchanged.",
            "Unit test: a 09:00 Tunis rule resolves to the correct UTC instant on a January date "
            "and on a July date, and the two differ where the zone offset differs.",
            "Unit test: a rule spanning a DST transition date produces the expected local hours "
            "on both sides.",
            "Unit test: minimum notice and maximum horizon are applied as documented at both "
            "boundaries.",
            "Integration test: another professional cannot read or write these rules.",
            "Integration test: an existing consultation survives the deletion of the rule that "
            "created its slot.",
            "A `grep` check that no naive `datetime.now()` or `datetime.utcnow()` call exists in "
            "the scheduling module; all time comes from an injectable clock so tests can freeze "
            "it.",
        ],
        "deliverables": [
            "`lexpert_api/scheduling/models.py`, `service.py`, `router.py`, `schemas.py`.",
            "`lexpert_api/core/clock.py` — the injectable clock, used project-wide from here on.",
            "The Alembic migration.",
            "`apps/api/tests/scheduling/test_availability.py` including the DST cases.",
            "`docs/technical_docs/time_and_timezones.md` stating the storage rules in one place.",
        ],
        "notes": (
            "Write `time_and_timezones.md` before the code, not after. Every subsequent issue "
            "that touches a timestamp will be reviewed against it, and it is much cheaper to "
            "agree the rules now than to find two modules disagreeing during ESC-06."
        ),
    },
    {
        "id": "SCH-02",
        "title": "Bookable slot computation",
        "milestone": "MVP",
        "labels": ["scheduling", "backend", "api"],
        "size": "M",
        "depends": ["SCH-01"],
        "branch": "feature/sch-02-slot-computation",
        "goal": (
            "Turn availability rules, exceptions, buffers and existing bookings into the concrete "
            "list of slots a client can pick. This is pure, testable logic and it should stay "
            "that way — no database access inside the computation itself."
        ),
        "requirements": [
            "A pure function taking rules, exceptions, existing consultations, constraints, a "
            "duration, a date range and a clock, and returning slot instants. No I/O inside it.",
            "Slots are generated at the requested duration, aligned to the rule's start, with the "
            "buffer applied after each existing consultation and after each generated slot as "
            "appropriate.",
            "A slot is excluded if it overlaps an existing consultation in any non-terminal "
            "state -- which includes `PENDING_ACCEPTANCE`, so a request awaiting the "
            "professional's answer holds its slot -- if it falls inside the minimum-notice "
            "window, if it is beyond the maximum horizon, or if it extends past the "
            "availability window's end.",
            "`GET /api/v1/professionals/{id}/slots?duration=&from=&to=&tz=` returning slots with "
            "both the UTC instant and a rendering in the requested timezone, so the client never "
            "has to reimplement the conversion.",
            "Cap the requested range (for example 60 days) and reject a longer one rather than "
            "computing it.",
            "The endpoint is public, consistent with PRO-02, but returns slots only for published "
            "and approved professionals.",
            "Concurrency is **not** solved here: two clients can be shown the same slot. The "
            "authoritative check is the booking transaction in ESC-03. Say so in a comment so "
            "nobody adds a reservation mechanism at this layer.",
        ],
        "validation": [
            "Unit test: a single 09:00-12:00 rule with a 60-minute duration and no buffer yields "
            "exactly three slots.",
            "Unit test: the same with a 15-minute buffer yields the documented smaller set.",
            "Unit test: an existing consultation at 10:00 removes the 10:00 slot and, with a "
            "buffer, the adjacent one.",
            "Unit test: a slot that would run past 12:00 is not generated.",
            "Unit test: minimum notice removes today's imminent slots, with the clock frozen.",
            "Unit test: maximum horizon truncates the range.",
            "Unit test: a full-day exception yields no slots for that date.",
            "Unit test: a `CANCELLED`, `DECLINED` or `EXPIRED` consultation does **not** block "
            "its slot; a `FUNDS_HELD` or `PENDING_ACCEPTANCE` one does.",
            "Unit test: slots requested in `Europe/Paris` render at the correct local times "
            "across a DST boundary.",
            "Integration test: an over-long range is refused; an unpublished professional returns "
            "404.",
            "Property test: no returned slot ever overlaps another returned slot or an existing "
            "consultation.",
        ],
        "deliverables": [
            "`lexpert_api/scheduling/slots.py` — the pure computation.",
            "The slots endpoint and its schemas.",
            "`apps/api/tests/scheduling/test_slots.py` with the table-driven and property tests.",
        ],
    },
    {
        "id": "SCH-03",
        "title": "Professional availability management screens",
        "milestone": "MVP",
        "labels": ["frontend", "scheduling"],
        "size": "M",
        "depends": ["SCH-01", "PRO-03"],
        "branch": "feature/sch-03-availability-ui",
        "goal": (
            "The professional portal screens for setting weekly hours, blocking dates, and "
            "configuring buffers and notice. The professional must be able to see immediately "
            "what a client will be offered."
        ),
        "requirements": [
            "A weekly schedule editor: per day, add or remove time ranges, with overlap "
            "prevented client-side before the request is made and the server error rendered if "
            "it still occurs.",
            "An exceptions calendar: pick a date, mark it unavailable or set different hours, and "
            "see the exceptions listed and removable.",
            "A settings panel for buffer minutes, minimum notice and maximum horizon, each with "
            "a French explanation of what it does in practice.",
            "A preview showing the concrete slots the current configuration produces for the next "
            "two weeks, fetched from SCH-02 — so the professional validates the result rather "
            "than the configuration.",
            "The professional's timezone is displayed prominently on every time input, because "
            "everything they enter is in it.",
            "Mobile-first: the weekly editor must be usable on a phone. A seven-column grid is "
            "not; use a per-day accordion or list.",
            "All copy in French; accessible time inputs with labels.",
        ],
        "validation": [
            "Component test: adding a range that overlaps an existing one is blocked client-side "
            "with a French message.",
            "Component test: adding, editing and removing a range calls the API correctly.",
            "Component test: a server overlap error is rendered inline.",
            "Component test: adding and removing an exception works and the list updates.",
            "Component test: the slot preview refetches when the configuration changes.",
            "Component test: the timezone label reflects the profile's timezone.",
            "Manual: configure a full week and one exception on a 375px viewport, keyboard only.",
        ],
        "deliverables": [
            "`apps/web/src/features/professional/availability/` with the weekly editor, "
            "exceptions calendar, settings panel and slot preview.",
            "Scheduling keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
    {
        "id": "SCH-04",
        "title": "Client booking calendar with timezone handling",
        "milestone": "MVP",
        "labels": ["frontend", "scheduling"],
        "size": "M",
        "depends": ["SCH-02", "PRO-04"],
        "branch": "feature/sch-04-booking-calendar-ui",
        "goal": (
            "The slot picker on the professional's profile page: choose a duration, see available "
            "times in your own timezone, pick one, and carry it into checkout. A diaspora client "
            "must never have to do timezone arithmetic in their head."
        ),
        "requirements": [
            "Duration selector from the allowed set, showing the price for each so the choice is "
            "informed.",
            "A date strip or small calendar with the days that have slots, and the slot list for "
            "the selected day.",
            "Times are rendered in the **client's** detected timezone, with the zone named "
            "explicitly and the professional's local time shown alongside when the two differ. "
            "Allow overriding the detected zone.",
            "Loading, empty (no availability in this range) and error states, each with useful "
            "French copy — an empty state should suggest looking further ahead.",
            "Selecting a slot shows a confirmation summary: professional, date and time in both "
            "zones, duration, and the price breakdown (rate x duration + commission = total), "
            "then continues into the ESC-08 checkout.",
            "The escrow explanation and the MVP simulation notice appear on this summary, because "
            "this is the last screen before a client commits.",
            "If the chosen slot is gone by the time checkout is submitted, the resulting conflict "
            "from ESC-03 is handled here: an explicit French message and a refreshed slot list, "
            "never a silent failure or a double booking.",
        ],
        "validation": [
            "Component test: duration selection refetches slots and updates the displayed "
            "prices.",
            "Component test: slots render in a client timezone different from the "
            "professional's, and both times are shown.",
            "Component test: overriding the timezone re-renders the same slots at the new local "
            "times.",
            "Component test: loading, empty and error states each render.",
            "Component test: the summary shows the exact breakdown the API returns, with no "
            "client-side price arithmetic of its own.",
            "Component test: a 409 slot-taken response renders the conflict message and refetches "
            "the slots.",
            "Component test: the simulation notice is present on the summary.",
            "Manual: pick a slot as a client in `Europe/Paris` against a professional in "
            "`Africa/Tunis` and confirm the displayed times are correct on both sides of a DST "
            "boundary.",
        ],
        "deliverables": [
            "`apps/web/src/features/client/booking/` with the duration selector, calendar, slot "
            "list and summary.",
            "A timezone display helper, tested.",
            "Booking keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
    # ------------------------------------------------------------------ ESC
    {
        "id": "ESC-01",
        "title": "EscrowProvider interface and the simulator adapter",
        "milestone": "MVP",
        "labels": ["escrow", "backend"],
        "size": "M",
        "depends": ["FND-05"],
        "branch": "feature/esc-01-escrow-provider",
        "goal": (
            "Define the seam between Lexpert's escrow policy and whoever actually moves money, "
            "and implement the MVP's simulator behind it. Getting this boundary right is what "
            "makes the Beta swap to a licensed partner a contained change instead of a rewrite, "
            "so it is worth doing carefully even though the simulator itself is simple."
        ),
        "requirements": [
            "An `EscrowProvider` protocol with exactly the operations a licensed provider "
            "performs: `authorize_hold(amount, currency, payer_ref, idempotency_key)`, "
            "`release(hold_ref, payee_ref, amount, idempotency_key)`, "
            "`refund(hold_ref, amount, idempotency_key)`, `get_hold(hold_ref)`.",
            "Every operation takes an **idempotency key** and is safe to retry: the same key "
            "returns the same result and does not perform the action twice. Real providers work "
            "this way and code written against a non-idempotent fake will break on the swap.",
            "Operations return a provider-agnostic result object (a reference, a status, an "
            "amount) and raise provider-agnostic errors (`ProviderDeclined`, "
            "`ProviderUnavailable`, `ProviderInvalidState`). No HTTP status, no provider payload, "
            "and no provider vocabulary crosses the boundary.",
            "`SimulatedEscrowProvider`: persists its own hold records in its own table, "
            "transitions them, honours idempotency keys, and is deterministic.",
            "The simulator supports **fault injection** driven by configuration or by the payer "
            "reference in tests: a declined authorization, a provider timeout, and a hold that is "
            "already released. Without these, the domain layer's error handling is untested and "
            "the Beta swap will surface bugs the MVP never exercised.",
            "Provider selection by `LEXPERT_ESCROW_PROVIDER` through a factory, with `simulator` "
            "the only registered value in the MVP and an unknown value failing at startup.",
            "The simulator's own records are the only place the word 'simulated' appears in the "
            "escrow module. The domain layer must not know which provider it has.",
            "A prominent module docstring stating that no real funds move, why (the feasibility "
            "study section 3.2), and what must not leak across the boundary in either direction.",
        ],
        "validation": [
            "Unit test: authorize, then release; the hold's status follows the documented path.",
            "Unit test: authorize, then refund.",
            "Unit test: the same idempotency key replayed on each of the three mutating "
            "operations returns the identical result and creates no second record.",
            "Unit test: releasing an already-released hold raises `ProviderInvalidState`.",
            "Unit test: refunding a released hold raises `ProviderInvalidState`.",
            "Unit test: each injectable fault raises the mapped provider-agnostic error.",
            "Unit test: an unknown `LEXPERT_ESCROW_PROVIDER` fails at startup with a clear "
            "message.",
            "A structural test asserting the protocol's signatures, so a change to the interface "
            "is a deliberate, visible act.",
            "`grep -rn \"simulat\" apps/api/src/lexpert_api` finds matches only in the adapter, "
            "its tests, and docstrings — never in the ledger or the state machine.",
        ],
        "deliverables": [
            "`lexpert_api/escrow/provider.py` (the protocol, the result and error types).",
            "`lexpert_api/escrow/providers/simulator.py` and its migration.",
            "`lexpert_api/escrow/providers/factory.py`.",
            "`apps/api/tests/escrow/test_provider_contract.py` — written so it can later be run "
            "against a real provider adapter unchanged.",
            "`docs/technical_docs/escrow_provider_boundary.md` documenting the seam and the Beta "
            "swap procedure.",
        ],
        "notes": (
            "Write the contract test suite so it is parameterised over provider implementations. "
            "In the MVP it runs against the simulator only; in Beta the same suite runs against "
            "the real adapter in sandbox and is the acceptance criterion for the swap. That is "
            "the highest-leverage thing this issue can produce."
        ),
    },
    {
        "id": "ESC-02",
        "title": "Double-entry ledger with a balance invariant",
        "milestone": "MVP",
        "labels": ["escrow", "database", "backend"],
        "size": "L",
        "depends": ["FND-03"],
        "branch": "feature/esc-02-ledger",
        "goal": (
            "The financial record of the platform: every movement of value recorded as balanced "
            "double-entry postings, from which every balance is derived rather than stored. The "
            "feasibility study calls for an immutable record of every escrow transition for "
            "financial traceability; this is that record's foundation."
        ),
        "requirements": [
            "`LedgerAccount`: id, type (`CLIENT`, `ESCROW_HOLD`, `PROFESSIONAL_PAYABLE`, "
            "`PLATFORM_REVENUE`, `EXTERNAL`), owner reference where applicable, currency. One "
            "escrow-hold account per consultation keeps holds individually traceable.",
            "`LedgerTransaction`: id, an idempotency key (unique), a kind, a reference to the "
            "consultation, a description, created_at. `LedgerEntry`: transaction id, account id, "
            "a signed integer amount in millimes.",
            "**Both tables are append-only.** No `UPDATE` and no `DELETE`, enforced by a database "
            "trigger or rule, not merely by convention in the service layer. A correction is a new, "
            "reversing transaction.",
            "The core invariant: the entries of a transaction sum to exactly zero. Enforce it in "
            "the posting function **and** with a database constraint or trigger, so no code path "
            "can write an unbalanced transaction.",
            "One `post_transaction(kind, entries, idempotency_key, ...)` function is the only way "
            "to write to the ledger. Replaying an idempotency key returns the existing "
            "transaction without writing.",
            "Balance queries derived by summation, with an index that makes per-account "
            "summation fast. Do not cache a balance column in the MVP; a stored balance that can "
            "disagree with the entries is worse than a slower query.",
            "Amounts are integer millimes throughout. A non-integer amount is a programming "
            "error and must raise, not round.",
            "A reversal helper that posts the exact inverse of a prior transaction, referencing "
            "it, for corrections and for refunds.",
            "The ledger module exposes only `post_transaction`, the balance queries and the "
            "reversal helper. Nothing outside `escrow` may import the models.",
        ],
        "validation": [
            "Unit test: a balanced two-entry transaction posts and both entries persist.",
            "Unit test: an unbalanced transaction is refused by the posting function.",
            "Integration test: an unbalanced transaction inserted **directly via SQL**, "
            "bypassing the service, is refused by the database. This is the test that proves the "
            "invariant is real.",
            "Integration test: an `UPDATE` and a `DELETE` against either ledger table are refused "
            "by the database.",
            "Unit test: replaying an idempotency key returns the original transaction and adds no "
            "rows.",
            "Unit test: a balance equals the sum of its account's entries, across several "
            "transactions.",
            "Unit test: a float or Decimal-with-fraction amount raises rather than rounding.",
            "Unit test: a reversal produces exactly inverse entries and references the original.",
            "Property test: over a few hundred randomly generated valid transactions, the sum of "
            "**all** entries across all accounts is always zero.",
            "Integration test: two concurrent posts with the same idempotency key result in "
            "exactly one transaction.",
            "Performance check: with 100000 entries, a per-account balance query uses the index; "
            "paste the plan in the PR.",
        ],
        "deliverables": [
            "`lexpert_api/escrow/ledger/` with `models.py`, `posting.py`, `balances.py`.",
            "The Alembic migration including the append-only and balance constraints or "
            "triggers.",
            "`apps/api/tests/escrow/test_ledger.py` covering every item above, including the "
            "raw-SQL bypass attempts.",
            "`docs/technical_docs/ledger.md` with the account types and the posting patterns for "
            "hold, release, refund and commission.",
        ],
        "notes": (
            "The raw-SQL bypass tests are the point of this issue. A balance invariant enforced "
            "only in Python is an invariant that holds until the first migration script or admin "
            "fix-up query, and the whole value of a ledger is that it cannot be quietly wrong."
        ),
    },
    {
        "id": "ESC-03",
        "title": "Consultation booking and the escrow state machine",
        "milestone": "MVP",
        "labels": ["escrow", "backend", "database"],
        "size": "L",
        "depends": ["ESC-01", "ESC-02", "SCH-02", "ESC-05"],
        "branch": "feature/esc-03-booking-state-machine",
        "goal": (
            "The heart of the product: creating a consultation, holding the funds, and moving it "
            "through the lifecycle from the feasibility study's state machine. Every transition "
            "is validated, ledger-posted and audited, and no two clients can take the same slot."
        ),
        "requirements": [
            "`Consultation`: id, client id, professional id, scheduled start and end (UTC), "
            "duration, timezone captured at booking, status, amounts (professional amount, "
            "commission, total), provider hold reference, hold-window expiry, timestamps.",
            "Implement exactly these transitions and nothing more. They are the feasibility "
            "study's section 5.1 machine plus the request-and-accept handshake the MVP "
            "requires, which the study does not model:\n"
            "    - `BOOKED -> PENDING_ACCEPTANCE` (the client's hold is authorized)\n"
            "    - `BOOKED -> CANCELLED` (the hold was declined by the provider)\n"
            "    - `PENDING_ACCEPTANCE -> FUNDS_HELD` (the professional accepted)\n"
            "    - `PENDING_ACCEPTANCE -> DECLINED` (the professional refused)\n"
            "    - `PENDING_ACCEPTANCE -> EXPIRED` (no answer before the deadline)\n"
            "    - `PENDING_ACCEPTANCE -> CANCELLED` (the client withdrew)\n"
            "    - `FUNDS_HELD -> IN_SESSION`, `FUNDS_HELD -> CANCELLED`, "
            "`FUNDS_HELD -> REFUNDED`\n"
            "    - `IN_SESSION -> SESSION_ENDED`, `SESSION_ENDED -> HOLD_WINDOW`\n"
            "    - `HOLD_WINDOW -> RELEASED_TO_PRO`, `HOLD_WINDOW -> UNDER_REVIEW`\n"
            "    - `UNDER_REVIEW -> RELEASED_TO_PRO`, `UNDER_REVIEW -> REFUNDED`\n"
            "  Every other transition raises. This issue owns the whole machine; ESC-10 builds "
            "the endpoints and the expiry job that drive the handshake states, so keep the "
            "matrix here and do not duplicate it there.",
            "`DECLINED` and `EXPIRED` are terminal, and both require the client to have been "
            "refunded in full. A consultation cannot reach either state with funds still held.",
            "`RELEASED_TO_PRO`, `REFUNDED`, `CANCELLED`, `DECLINED` and `EXPIRED` are terminal. "
            "No transition leaves a terminal state, ever.",
            "One `transition(consultation, to_status, actor, reason)` function is the only way "
            "status changes. It locks the row (`SELECT FOR UPDATE`), validates the transition, "
            "performs the provider call and the ledger posting, appends the audit entry, and "
            "commits — all in one database transaction.",
            "**Slot concurrency is resolved here.** A database-level exclusion or unique "
            "constraint prevents two non-terminal consultations overlapping for the same "
            "professional. `PENDING_ACCEPTANCE` counts as non-terminal, so an unanswered "
            "request holds its slot. Two simultaneous requests for one slot must yield one "
            "success and one conflict error, never two.",
            "Request flow: validate the slot against SCH-02, compute amounts via ESC-05, create "
            "the consultation as `BOOKED`, call `authorize_hold` with an idempotency key "
            "derived from the consultation id, post the hold to the ledger, and transition "
            "to `PENDING_ACCEPTANCE` -- awaiting the professional's answer. If the provider "
            "declines, the consultation ends `CANCELLED` with the reason and no ledger "
            "movement. The accept, decline and expiry paths are ESC-10.",
            "Ledger postings per transition, exactly as documented in `ledger.md`: the hold moves "
            "value from the client account to the consultation's escrow-hold account; release "
            "splits it between professional payable and platform revenue; a refund reverses the "
            "hold.",
            "The provider call and the ledger post must not be able to disagree. Where the "
            "provider succeeds and the local transaction then fails, the idempotency key makes "
            "the retry safe; document this recovery path explicitly.",
            "Endpoints: `POST /api/v1/consultations` (client requests), "
            "`GET /api/v1/consultations` (the caller's own, filtered by status), "
            "`GET /api/v1/consultations/{id}` (client, professional or admin only).",
        ],
        "validation": [
            "Unit test: a table-driven test over the full transition matrix asserts every legal "
            "transition is allowed and **every** illegal one raises. This includes every "
            "transition out of each terminal state.",
            "Integration test: a successful request ends `PENDING_ACCEPTANCE`, with a provider "
            "hold, a balanced ledger transaction, and an audit entry.",
            "Integration test: a provider decline leaves the consultation `CANCELLED` and the "
            "ledger **empty** for it.",
            "Integration test: a provider timeout leaves no partially-booked state; retrying with "
            "the same key does not double-hold.",
            "Concurrency test: two parallel requests for the identical slot produce exactly one "
            "`PENDING_ACCEPTANCE` consultation and one conflict error. Run it enough times "
            "to be meaningful.",
            "Concurrency test: two parallel transitions of the same consultation produce one "
            "success and one rejection, not two.",
            "Integration test: booking a slot outside availability is refused.",
            "Integration test: booking inside the minimum-notice window is refused.",
            "Integration test: a client cannot book on behalf of another client; a professional "
            "cannot book their own slot.",
            "Integration test: after every transition, the ledger's total across all accounts is "
            "still zero.",
            "Integration test: a client requesting another client's consultation gets 404.",
            "Integration test: the full happy path across all states leaves consistent amounts: "
            "professional payable plus platform revenue equals the total held.",
        ],
        "deliverables": [
            "`lexpert_api/booking/models.py`, `lexpert_api/escrow/state_machine.py`, "
            "`lexpert_api/booking/service.py`, `router.py`, `schemas.py`.",
            "The Alembic migration including the overlap-exclusion constraint.",
            "`apps/api/tests/escrow/test_state_machine.py` (the matrix), "
            "`test_booking_flow.py`, `test_booking_concurrency.py`.",
            "The state diagram in `docs/technical_docs/escrow_lifecycle.md`, matching the code.",
        ],
        "notes": (
            "This is the largest and most consequential issue in the MVP. Two things earn special "
            "care in review: the transition matrix test must be exhaustive rather than "
            "representative, and the concurrency tests must actually run in parallel against a "
            "real PostgreSQL. A serialised test proves nothing about the constraint. If this "
            "issue starts feeling too large to review in one pass, say so on the issue and we "
            "will split the transition machinery from the booking endpoint."
        ),
    },
    {
        "id": "ESC-04",
        "title": "Immutable audit log for escrow transitions",
        "milestone": "MVP",
        "labels": ["escrow", "compliance", "database"],
        "size": "M",
        "depends": ["ESC-03"],
        "branch": "feature/esc-04-audit-log",
        "goal": (
            "An append-only record of every escrow state transition: who, when, from what state "
            "to what state, why, and which ledger transaction it produced. The feasibility study "
            "lists this under financial traceability, and it is the artifact a payment partner or "
            "a regulator will ask to see."
        ),
        "requirements": [
            "`EscrowAuditEntry`: id, consultation id, sequence number within that consultation, "
            "from status, to status, actor type (`CLIENT`, `PROFESSIONAL`, `ADMIN`, `SYSTEM`), "
            "actor id, reason, ledger transaction id, provider reference, occurred_at, and a "
            "JSON snapshot of the amounts at that moment.",
            "Append-only at the **database** level: a trigger or rule refusing `UPDATE` and "
            "`DELETE`, as with the ledger.",
            "Written inside the same transaction as the transition it records, so a transition "
            "without an audit entry is impossible. Not a listener, not a background task.",
            "The sequence number is contiguous per consultation and gapless, so a missing entry "
            "is detectable.",
            "A tamper-evidence chain: each entry stores a hash over its own content plus the "
            "previous entry's hash for that consultation. Any retro-edit of an earlier entry "
            "breaks verification for every entry after it.",
            "`GET /api/v1/admin/consultations/{id}/audit` for admins, and a verification function "
            "that walks a consultation's chain and reports whether it is intact.",
            "The reason field carries operational context only. **No consultation content, no "
            "health, legal or financial detail.** Say so in the model docstring.",
            "A test that enumerates every call site of `transition()` and asserts an audit entry "
            "results — so a future transition path cannot skip the log.",
        ],
        "validation": [
            "Integration test: every transition in the happy path produces exactly one entry, "
            "sequence numbers 1..n with no gaps.",
            "Integration test: `UPDATE` and `DELETE` on the audit table, via raw SQL, are "
            "refused.",
            "Integration test: a transition whose surrounding database transaction rolls back "
            "leaves **no** audit entry and no status change.",
            "Unit test: the hash chain verifies on an intact chain.",
            "Integration test: mutating an entry's content in the database (with the trigger "
            "temporarily disabled, inside the test) makes verification fail from that point on.",
            "Integration test: each actor type is recorded correctly, including `SYSTEM` for the "
            "ESC-06 auto-release.",
            "Integration test: the admin endpoint returns the full chain; a client is refused.",
            "The call-site coverage test fails when a transition path without an audit entry is "
            "introduced.",
        ],
        "deliverables": [
            "`lexpert_api/escrow/audit.py` and its models.",
            "The Alembic migration with the append-only trigger.",
            "The admin audit endpoint.",
            "`apps/api/tests/escrow/test_audit.py` covering every item above.",
            "A `## Audit trail` section in `docs/technical_docs/escrow_lifecycle.md`.",
        ],
    },
    {
        "id": "ESC-05",
        "title": "Price computation: rate, duration and commission",
        "milestone": "MVP",
        "labels": ["escrow", "backend", "good-first-issue"],
        "size": "S",
        "depends": ["PRO-01"],
        "branch": "feature/esc-05-price-computation",
        "goal": (
            "One function that turns an hourly rate and a duration into the three numbers "
            "everything else uses: what the client pays, what the professional earns, and what "
            "the platform keeps. Small, pure, and worth getting exactly right — rounding errors "
            "here become ledger imbalances in ESC-03."
        ),
        "requirements": [
            "A pure function `compute_price(hourly_rate_millimes, duration_minutes, "
            "commission_bps) -> PriceBreakdown` with fields `total`, `professional_amount` and "
            "`platform_commission`, all integer millimes.",
            "The invariant, asserted in the function itself: `professional_amount + "
            "platform_commission == total`, always. Any rounding remainder is assigned "
            "deliberately to one side (document which and why) rather than left to float.",
            "Rounding is explicit and documented: the total is derived from the rate and the "
            "duration with a stated rule, and the commission is computed from the total in basis "
            "points with a stated rounding direction.",
            "Integer arithmetic only. No `float` anywhere in the module, and no `Decimal` "
            "conversion that could reintroduce fractions into a stored amount.",
            "Reject invalid input rather than coercing it: a non-positive rate, a duration not in "
            "the allowed set, a commission outside 0..10000.",
            "`GET /api/v1/professionals/{id}/pricing?duration=` returning the breakdown, so the "
            "web app displays the server's numbers rather than recomputing them.",
            "The commission rate comes from `LEXPERT_PLATFORM_COMMISSION_BPS`. The breakdown "
            "stored on a consultation is the one computed at booking time; a later change to the "
            "platform rate must not alter an existing consultation.",
        ],
        "validation": [
            "Unit test: a clean case (60000 millimes per hour, 60 minutes, 1500 bps) produces the "
            "documented breakdown.",
            "Unit test: a case with a rounding remainder (a rate and duration that do not divide "
            "evenly) still satisfies the sum invariant, with the remainder on the documented "
            "side.",
            "Property test: across a wide range of rates, durations and commission rates, "
            "`professional_amount + platform_commission == total` and all three are "
            "non-negative integers.",
            "Unit test: a 15-minute duration is a quarter of the hourly rate, exactly.",
            "Unit test: 0 bps gives the professional everything; 10000 bps gives them nothing and "
            "still balances.",
            "Unit test: each invalid input raises with its documented code.",
            "Unit test: `grep` the module for `float` finds nothing.",
            "Integration test: changing the platform commission setting does not change the "
            "amounts on an already-booked consultation.",
        ],
        "deliverables": [
            "`lexpert_api/escrow/pricing.py` with `compute_price` and `PriceBreakdown`.",
            "The pricing endpoint.",
            "`apps/api/tests/escrow/test_pricing.py` including the property test.",
            "A `## Pricing` section in `docs/technical_docs/ledger.md` stating the rounding rule.",
        ],
        "notes": (
            "Good first issue: small, self-contained, pure, and heavily tested. It is also on the "
            "critical path for ESC-03, so it is a useful early win."
        ),
    },
    {
        "id": "ESC-06",
        "title": "Auto-release job for the one-hour hold window",
        "milestone": "MVP",
        "labels": ["escrow", "backend"],
        "size": "M",
        "depends": ["ESC-03", "ESC-04"],
        "branch": "feature/esc-06-auto-release",
        "goal": (
            "The mechanism that actually implements the product's promise: one hour after a "
            "consultation ends, if nobody disputed it, the funds go to the professional "
            "automatically. It runs unattended and moves money, so idempotency and observability "
            "are the whole job."
        ),
        "requirements": [
            "When a consultation reaches `SESSION_ENDED`, it transitions to `HOLD_WINDOW` with "
            "`hold_window_expires_at = ended_at + LEXPERT_ESCROW_HOLD_WINDOW_MINUTES`, read from "
            "settings so the duration is configurable per the feasibility study.",
            "A periodic worker selecting consultations in `HOLD_WINDOW` whose expiry has passed "
            "and transitioning each to `RELEASED_TO_PRO` via the ESC-03 transition function, with "
            "the actor recorded as `SYSTEM`.",
            "Each consultation is processed **independently**: one failure must not stop the batch "
            "or roll back the others. Failures are logged with the consultation id and retried "
            "on the next tick.",
            "Idempotent by construction: the transition function's state validation means a "
            "second attempt on an already-released consultation is a no-op, not a double "
            "release. Prove this with a test.",
            "Locked selection (`SELECT ... FOR UPDATE SKIP LOCKED`) so two worker instances never "
            "process the same consultation.",
            "A bounded retry with a cap on attempts; after the cap, the consultation is flagged "
            "for admin attention rather than retried forever, and the flag is visible in the "
            "back-office.",
            "Runnable both as a scheduled task and as a one-shot CLI command, so it can be "
            "triggered by hand in a demo and in tests. The MVP does not need a queue "
            "infrastructure; a scheduler plus the CLI is enough.",
            "Structured logs per run: how many were eligible, released, failed, and how long it "
            "took. This job silently not running is the worst failure mode, so make its silence "
            "detectable.",
            "A consultation in `UNDER_REVIEW` (disputed) is **never** touched by this job.",
        ],
        "validation": [
            "Integration test with a frozen clock: a consultation whose window has expired is "
            "released; one whose window has not is left alone. Test both sides of the boundary "
            "and the exact boundary instant.",
            "Integration test: a disputed consultation in `UNDER_REVIEW` is not released.",
            "Integration test: running the job twice releases once; the second run is a no-op "
            "and posts no second ledger transaction.",
            "Integration test: with three eligible consultations, one of which fails, the other "
            "two are still released.",
            "Integration test: the failed one is retried on the next run and succeeds.",
            "Integration test: after the retry cap it is flagged rather than retried again.",
            "Concurrency test: two workers over the same eligible set release each consultation "
            "exactly once.",
            "Integration test: each release produces an audit entry with actor `SYSTEM` and a "
            "balanced ledger transaction splitting the total into payable and revenue.",
            "Integration test: changing the hold-window setting affects new consultations but "
            "not the expiry already stored on existing ones.",
            "Unit test: the run summary log contains the documented counters.",
        ],
        "deliverables": [
            "`lexpert_api/escrow/jobs/auto_release.py` and the CLI entry point.",
            "The scheduler wiring, and documentation of how it is run locally.",
            "`apps/api/tests/escrow/test_auto_release.py` covering every item above.",
            "A `## Hold window and auto-release` section in "
            "`docs/technical_docs/escrow_lifecycle.md`.",
        ],
    },
    {
        "id": "ESC-07",
        "title": "Cancellation and no-show policy engine",
        "milestone": "MVP",
        "labels": ["escrow", "backend"],
        "size": "M",
        "depends": ["ESC-03"],
        "branch": "feature/esc-07-cancellation-policy",
        "goal": (
            "Encode the rules from feasibility study section 5.2 for what happens when a "
            "consultation does not go ahead: who cancelled, how late, who failed to show, and "
            "therefore what portion of the held funds is refunded or retained. These are business "
            "policy, so they belong in one declarative, testable place rather than scattered "
            "across endpoints."
        ),
        "requirements": [
            "A pure policy function taking who is cancelling, the time until the scheduled start, "
            "the consultation state and the amounts, and returning an outcome: refund in full, "
            "refund partially with a stated retained amount, or no refund.",
            "A cancellation while the consultation is still `PENDING_ACCEPTANCE` always "
            "refunds in full, whoever initiates it: the professional has not committed any "
            "time yet, so there is nothing to compensate. ESC-10 owns the endpoints for that "
            "state; this issue owns the rule.",
            "Tiered client cancellation: free outside a configurable window (for example more "
            "than 24 hours before), a configurable retained percentage inside it, and a "
            "different tier very close to the start. All thresholds and percentages come from "
            "settings, not from literals in the code.",
            "Professional cancellation always refunds the client in full, at any notice. The "
            "study is explicit that the platform protects the client here.",
            "No-show handling: a professional no-show refunds the client in full; a client "
            "no-show retains per policy. A no-show is determined from the CON-02 participation "
            "record, not asserted by either party.",
            "A grace period after the scheduled start before a no-show can be declared, from "
            "settings.",
            "Endpoints: `POST /api/v1/consultations/{id}/cancel` for the client and the "
            "professional, which computes the outcome, performs the refund through the provider, "
            "posts the ledger entries and transitions to `CANCELLED` or `REFUNDED`.",
            "Retained amounts are split between professional and platform per a documented rule, "
            "and the ledger postings for every outcome are documented in `ledger.md` before the "
            "code is written.",
            "The policy function is pure and has no database or provider access, so the whole "
            "matrix can be tested exhaustively.",
        ],
        "validation": [
            "Unit test: a table-driven matrix over {client, professional} x {well before, inside "
            "window, just before, after start} x {PENDING_ACCEPTANCE, FUNDS_HELD} asserting "
            "the expected outcome for every cell. Every cell is populated; none is left "
            "implicit.",
            "Unit test: every `PENDING_ACCEPTANCE` cell refunds in full, for both "
            "initiators and at every notice level.",
            "Unit test: each tier boundary is tested on both sides and exactly at the boundary.",
            "Unit test: a professional cancellation refunds in full even one minute before the "
            "start.",
            "Unit test: outcome amounts always sum to the total held, with no millime lost or "
            "created.",
            "Integration test: a client cancellation inside the window refunds the correct "
            "partial amount, posts balanced ledger entries, and audits the transition.",
            "Integration test: cancelling a consultation already `IN_SESSION` is refused.",
            "Integration test: cancelling an already-cancelled consultation is refused.",
            "Integration test: a third party cannot cancel someone else's consultation.",
            "Integration test: a client no-show inside the grace period cannot yet be declared; "
            "after it, it can.",
            "Integration test: a professional no-show refunds the client fully and records the "
            "outcome.",
            "Integration test: after every cancellation path, the ledger total across all "
            "accounts is still zero.",
        ],
        "deliverables": [
            "`lexpert_api/escrow/policy.py` — the pure policy function and its outcome type.",
            "The cancel endpoint and the no-show determination service.",
            "New settings for the windows, percentages and grace period, added to `.env.example`.",
            "`apps/api/tests/escrow/test_cancellation_policy.py` with the full matrix.",
            "`docs/technical_docs/cancellation_policy.md` — the policy in prose, as the "
            "reference for the French copy in the UI.",
        ],
        "notes": (
            "The specific windows and percentages are business decisions the feasibility study "
            "leaves open. Implement the mechanism with defaults, list the exact numbers you chose "
            "in the PR description, and expect them to be adjusted in review rather than treated "
            "as settled."
        ),
    },
    {
        "id": "ESC-08",
        "title": "Client consultation request checkout with the simulated payment step",
        "milestone": "MVP",
        "labels": ["frontend", "escrow"],
        "size": "M",
        "depends": ["ESC-03", "SCH-04"],
        "branch": "feature/esc-08-checkout-ui",
        "goal": (
            "The screens where a client submits a consultation request and the funds are held. "
            "The professional has not accepted yet, so the copy must not promise a confirmed "
            "consultation. In the MVP there is also no real payment, and this screen carries "
            "the responsibility of saying both things unambiguously while still demonstrating "
            "the real flow."
        ),
        "requirements": [
            "A checkout summary: professional, date and time in the client's timezone, duration, "
            "and the price breakdown exactly as the API returned it (rate x duration, commission, "
            "total). No client-side price arithmetic.",
            "A clear French explanation of the escrow: the money is held, the professional is "
            "paid one hour after the consultation, a dispute can be raised in that hour.",
            "An unmissable simulation notice — a distinct banner, not fine print — stating that "
            "this is a demonstration, that no real payment is taken and no card is charged. It "
            "must be impossible to reach the confirm button without having seen it.",
            "A simulated payment step that visibly stands in for a real one, without imitating a "
            "card form. Do **not** build a fake card-number input: a screen that collects "
            "card-shaped data under false pretenses is the one thing this MVP must not do.",
            "Explicit consent checkboxes before confirming: the cancellation policy (linking to "
            "the ESC-07 copy) and the platform terms. Unchecked means the confirm button stays "
            "disabled.",
            "On confirm, call `POST /consultations` and handle every documented outcome: success "
            "goes to a confirmation screen; a slot conflict returns to the calendar with a French "
            "explanation; a provider decline explains and offers a retry; a network failure is "
            "distinguishable from a decline.",
            "Double-submit protection: the confirm button disables on click and the request "
            "carries an idempotency-safe path, so a double click cannot create two "
            "consultations.",
            "A confirmation screen that is honest about what has happened: the request was sent, "
            "the money is held, the professional has until a stated deadline to accept, and "
            "the client is refunded in full if they decline or do not answer. It must not say "
            "the consultation is confirmed, and it links to the ESC-12 consultations list "
            "rather than to a join control that does not work yet.",
        ],
        "validation": [
            "Component test: the summary renders the API's breakdown verbatim, and no arithmetic "
            "is performed client-side (assert against a breakdown whose numbers do not follow the "
            "naive formula).",
            "Component test: the simulation banner is present and is not visually dismissible "
            "before confirming.",
            "Component test: confirm is disabled until both consents are checked.",
            "Component test: a successful submit calls the endpoint once and navigates to the "
            "request-sent screen, whose copy states the acceptance deadline and the "
            "full-refund guarantee and does not claim the consultation is confirmed.",
            "Component test: a double click results in exactly one request.",
            "Component test: a 409 conflict, a provider decline and a network error each render "
            "their own distinct French message.",
            "Component test: no input in the flow collects card-like data (assert on the rendered "
            "form fields).",
            "Manual: complete a booking end to end against a running local stack and confirm the "
            "consultation appears as `FUNDS_HELD` with a balanced ledger transaction.",
        ],
        "deliverables": [
            "`apps/web/src/features/client/checkout/` with the summary, simulation notice, "
            "consent panel and confirmation screen.",
            "Checkout keys in `fr.ts`, including the escrow explanation and the simulation "
            "notice.",
            "Component tests covering every item above.",
        ],
    },
    {
        "id": "ESC-09",
        "title": "Professional earnings and consultation history views",
        "milestone": "MVP",
        "labels": ["frontend", "escrow"],
        "size": "M",
        "depends": ["ESC-06", "PRO-03"],
        "branch": "feature/esc-09-earnings-ui",
        "goal": (
            "The professional's view of their money: what is held, what has been released, what "
            "was refunded, and why. A professional who cannot see where their money is will not "
            "trust the escrow, which makes this screen part of the core value proposition rather "
            "than a report."
        ),
        "requirements": [
            "An earnings summary: total held (consultations booked or awaiting release), total "
            "released, and total refunded away, each derived from the ledger balances rather than "
            "recomputed in the client.",
            "A consultation list with the status in French, the client's first name, the date, the "
            "gross amount, the commission and the net, filterable by status and date range.",
            "A per-consultation detail view showing the money timeline: held on this date, "
            "consultation on this date, released or refunded on this date and why. This is the "
            "professional-readable projection of the ESC-04 audit trail; it must not expose "
            "internal state names or actor ids.",
            "For a consultation in `HOLD_WINDOW`, show the release countdown explicitly: when the "
            "hold expires and when payment will arrive.",
            "An API endpoint to back these views (`GET /api/v1/professionals/me/earnings`) if one "
            "does not already exist, returning ledger-derived figures. Add it in this issue "
            "rather than assembling the numbers from several calls in the browser.",
            "Empty state for a professional with no consultations yet, with a French pointer "
            "toward completing their profile and availability.",
            "The MVP simulation notice appears here too: these are simulated amounts and no real "
            "payout occurs.",
            "Mobile-first, since a professional will check this on a phone.",
        ],
        "validation": [
            "Integration test: the earnings endpoint's figures equal the ledger balances for a "
            "seeded professional across held, released and refunded consultations.",
            "Integration test: a professional cannot read another professional's earnings.",
            "Component test: the summary renders the endpoint's figures without recomputation.",
            "Component test: status and date filters both narrow the list.",
            "Component test: a `HOLD_WINDOW` consultation shows a countdown to the stored expiry.",
            "Component test: the detail timeline renders each money event in French with no "
            "internal status names leaking.",
            "Component test: the empty state renders for a professional with no consultations.",
            "Component test: the simulation notice is present.",
            "Manual: check the whole view on a 375px viewport.",
        ],
        "deliverables": [
            "`GET /api/v1/professionals/me/earnings` and its tests.",
            "`apps/web/src/features/professional/earnings/` with the summary, list and detail "
            "views.",
            "Earnings keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
]
