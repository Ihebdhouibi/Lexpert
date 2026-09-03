"""Backlog entries for the UX workstream.

Two tracks share this prefix. The `design` label marks work for the designer; the rest is
frontend engineering that consumes what the designer produces. Both are here rather than
split, because the ordering between them is the whole point: tokens before components,
components before screens.

The design issues are written for someone early in their career. Each carries a **Recommended
approach** section with concrete paths, references and the mistakes worth avoiding, because a
requirement list alone ("produce a visual direction") is not actionable to someone who has not
done it before. The grounding for all of them is `docs/design/design_brief.md`.
"""

from __future__ import annotations

ISSUES: list[dict[str, object]] = [
    # ------------------------------------------------------------------ grounding
    {
        "id": "UX-01",
        "title": "Product grounding, competitor teardowns and user conversations",
        "milestone": "MVP",
        "labels": ["design", "ux", "docs"],
        "size": "M",
        "depends": [],
        "branch": "chore/ux-01-grounding",
        "goal": (
            "Understand the product, the market and the three audiences well enough to design "
            "for them, and write down what you learned so the rest of the team shares it. This "
            "comes before any screen, any flow and any colour, because every later decision "
            "either follows from this or is a guess."
        ),
        "requirements": [
            "Read `docs/design/design_brief.md` in full, then `docs/implementation/"
            "lexpert_plan.md` sections 1 and 2. Come back with disagreements -- the brief is a "
            "starting position, not a specification.",
            "**Teardown of three products**, one per row of the reference table in the brief: "
            "Doctolib or Qare (French medical booking and teleconsultation), DabaDoc (the "
            "regional competitor), and one marketplace with a request-and-accept handshake such "
            "as Malt. Walk one full journey in each.",
            "**Five conversations with real people**, minimum: three who would plausibly be "
            "clients (ideally one over 60, and one living abroad), and two professionals in any "
            "of the three verticals. Twenty minutes each is enough.",
            "A written findings document covering, for each of the three audiences: their "
            "context (device, connection, setting), what they are anxious about, and what would "
            "make them abandon the flow.",
            "A specific answer to the trust question: **what would make a Tunisian client "
            "comfortable paying online for a consultation with a stranger?** Ask it directly in "
            "the conversations. It is the product's central bet and we are currently guessing.",
            "A list of the brief's assumptions your research **contradicted**. This is the most "
            "valuable output; a findings document that agrees with everything usually means the "
            "questions were leading.",
        ],
        "recommended": [
            "**How to run a teardown properly.** Walk one journey end to end. Screenshot every "
            "screen, including the errors -- deliberately submit a bad form, deny camera "
            "permission, go offline. Then write one sentence per screen: what decision did the "
            "designer make, and why. A teardown like that is worth more than a mood board, and "
            "the error screens are where you learn the most because nobody polishes them.",
            "**How to find five people without a budget.** Family, neighbours, a pharmacy "
            "queue, a university corridor. This is not statistically valid research and does not "
            "need to be -- five conversations will still surface things nobody in the team "
            "predicted. Do not wait for a proper study.",
            "**How to ask without leading.** Ask about the last time they needed a doctor or a "
            "lawyer and what they actually did. Past behaviour is evidence; \"would you use an "
            "app that...\" is not, because people say yes to be polite. Never demo the product "
            "before asking.",
            "**Where to read about the method.** The GOV.UK Service Manual's user-research "
            "section is free, short and practical, and is written for people doing this for the "
            "first time. Steve Krug's *Rocket Surgery Made Easy* is the other short, practical "
            "option if you want a book.",
            "**Do not produce polished personas.** Photographs and invented names for fictional "
            "people take a day and change no decision. A page of real quotes and observed "
            "contexts is more useful and more honest.",
        ],
        "validation": [
            "The findings document names at least three specific things that would make a client "
            "abandon the flow, each traceable to something a real person said.",
            "At least one brief assumption is contradicted, with the evidence.",
            "The three teardowns each cover the full journey including at least two error states, "
            "with a decision noted per screen.",
            "Every quoted person is anonymous -- no names, no identifying detail. This is a "
            "public repository.",
            "Reviewed with the technical lead and the section 12 questions in the brief are "
            "answered or explicitly deferred.",
        ],
        "deliverables": [
            "`docs/design/research_findings.md` with the audience contexts, the trust findings "
            "and the contradicted assumptions.",
            "`docs/design/competitor_teardowns.md`, or a Figma file linked from it, with the "
            "annotated journeys.",
            "A short list of open questions added to the brief's section 12.",
        ],
        "notes": (
            "This issue is deliberately first and deliberately not a design task. The most "
            "expensive mistake available on this project is to design forty screens for an "
            "audience nobody has spoken to. Two days here saves weeks later.\n\n"
            "It is also the issue most likely to be skipped under time pressure. If it has to be "
            "cut short, cut the teardowns, not the conversations."
        ),
    },
    {
        "id": "UX-09",
        "title": "French UX copy guide and terminology glossary",
        "milestone": "MVP",
        "labels": ["design", "ux", "docs"],
        "size": "M",
        "depends": ["UX-01"],
        "branch": "chore/ux-09-copy-guide",
        "goal": (
            "Decide the French vocabulary and tone before any screen exists. Fifty-three issues "
            "say user-facing strings are French and come from the i18n catalogue, but nothing "
            "says what words to use. Deciding late means rewriting every string in the product."
        ),
        "requirements": [
            "A **glossary** fixing one French term per concept, with the rejected alternatives "
            "and why. At minimum: the escrow itself, consultation, professional (a word that "
            "works for a doctor, a lawyer *and* an expert-comptable), client, request, accept, "
            "decline, hold window, dispute, refund, release, verification, slot, availability.",
            "A decision on **vouvoiement vs tutoiement**, applied consistently. Vouvoiement is "
            "almost certainly right for a health and legal product; confirm it rather than "
            "assume it.",
            "**Client-facing labels for all twelve consultation states.** The system says "
            "`PENDING_ACCEPTANCE`; a person needs plain French. Every state in "
            "`docs/technical_docs/escrow_lifecycle.md` needs a client label, a professional "
            "label where it differs, and never leaks the internal name.",
            "**The escrow, explained in two sentences**, for someone who has never heard of one. "
            "This is the single highest-value paragraph in the product. `séquestre` is the "
            "correct technical term and is probably the wrong word to use -- test alternatives "
            "on real people from UX-01.",
            "**Error message rules**: say what went wrong, then what to do about it. No apology, "
            "no blame, no jargon, no error codes shown to clients. Write five real examples: a "
            "network failure, a taken slot, a declined payment, a denied camera permission, an "
            "expired session.",
            "**Money and date formatting** conventions: how a price is written (comma as the "
            "decimal separator, `DT` or `TND`, where the symbol sits), and how a date and time "
            "are written including the timezone when it differs from the reader's.",
            "The **MVP simulation notice**, in final wording -- it appears on every money "
            "surface and must be unmissable without being frightening.",
            "A rule for **the empty state and the first-run experience** tone: instructive, not "
            "apologetic.",
        ],
        "recommended": [
            "**Start from the states, not from a word list.** Open the escrow lifecycle doc, put "
            "the twelve states in a column, and write the client's version beside each. The "
            "vocabulary you need falls out of that, and you will not miss a state.",
            "**Test the escrow explanation on five people from UX-01.** Read it aloud, then ask "
            "them to explain back what happens to their money. If they cannot, the wording has "
            "failed -- and it is much cheaper to find that out now.",
            "**Read the GOV.UK content design guidance.** It is free, short, and the best "
            "available writing on plain-language service copy and error messages. The principles "
            "transfer directly to French even though the examples are English.",
            "**Prefer the shorter, plainer word every time.** This audience includes people who "
            "are anxious and people who are not confident readers. *Argent bloqué* is likely to "
            "beat *fonds séquestrés* even though the second is more precise.",
            "**Watch for the three-vertical trap.** Words that feel natural for a doctor often "
            "sound wrong for a lawyer. *Patient* is wrong -- it has to be *client* for all "
            "three. Check each term against all three verticals before fixing it.",
            "**Do not write the copy in Figma only.** It ends up in "
            "`apps/web/src/i18n/fr.ts`, so the glossary needs to be a document the implementer "
            "can work from, keyed the way the catalogue is keyed.",
        ],
        "validation": [
            "Every one of the twelve consultation states has a client-facing French label, and "
            "no internal state name appears in any of them.",
            "The escrow explanation was read to at least five people and at least four could "
            "explain back what happens to their money. Record the result, including failures.",
            "Every glossary term is checked against all three verticals and does not sound wrong "
            "for any of them.",
            "The five example error messages each state what happened and what to do next.",
            "Reviewed and approved by the technical lead -- these words are hard to change later.",
        ],
        "deliverables": [
            "`docs/design/copy_guide.md` with the glossary, tone rules, formatting conventions "
            "and error message rules.",
            "The client-facing state label table, in a form the implementer can key into "
            "`fr.ts`.",
            "The final escrow explanation and simulation notice wording, with the test results.",
        ],
        "notes": (
            "Second in the order and deliberately before any screen. Copy is not decoration on "
            "this product -- for a client deciding whether to trust an unfamiliar payment model, "
            "the words *are* the product. It is also the cheapest thing on the roadmap to get "
            "right now and among the most expensive to change once fifty screens reference it."
        ),
    },
    # ------------------------------------------------------------------ structure
    {
        "id": "UX-02",
        "title": "Information architecture and user flows for the three portals",
        "milestone": "MVP",
        "labels": ["design", "ux"],
        "size": "M",
        "depends": ["UX-01"],
        "branch": "chore/ux-02-flows",
        "goal": (
            "Map every screen the MVP needs and how someone moves between them, before anything "
            "is styled. This is what turns fifty-three issues into a picture the whole team "
            "shares, and it is where a missing screen is cheap to discover."
        ),
        "requirements": [
            "A **screen inventory** for each of the three portals -- client, professional, admin "
            "-- derived from the backlog. Every frontend issue in "
            "`docs/implementation/lexpert_issues.md` names its screens; the inventory should "
            "account for all of them.",
            "**Flow diagrams for the five critical journeys**: (1) professional registers, gets "
            "verified and publishes; (2) client searches, requests, and the professional accepts; "
            "(3) the consultation itself, from waiting room to release; (4) the dispute, from "
            "raise to resolution; (5) the four rejection paths -- decline, expiry, withdrawal, "
            "cancellation -- and what the client sees in each.",
            "**Navigation structure per portal**, with what is reachable from where. The three "
            "portals are separate route trees and a client must never see professional "
            "navigation.",
            "Every flow marks its **decision points and failure branches**, not just the happy "
            "path. A flow with no branches is a diagram of an assumption.",
            "The **entry points**: where a client arrives from, what an unauthenticated visitor "
            "can see, and what happens when someone lands on a page they may not view.",
            "A note on any screen the backlog needs but that has **no issue covering it** -- "
            "raise it rather than designing it silently.",
        ],
        "recommended": [
            "**Boxes and arrows only.** No colour, no type choices, no component design. If it "
            "looks pretty, you have started styling too early and will resist changing it.",
            "**FigJam or Figma with plain rectangles** is right for this. Whimsical and Miro are "
            "fine too. The tool does not matter; being able to move things cheaply does.",
            "**Work from the state matrix in the brief, section 6.** Each state that changes what "
            "a user can do next is a branch in a flow. That is how you find the screens nobody "
            "listed -- for instance, what a professional sees when their verification was "
            "rejected and they are mid-way through fixing it.",
            "**Draw the rejection paths in full.** Four of them exist and they are the ones a "
            "team forgets, because nobody demos them. They are also where trust is either kept "
            "or lost, since they all end in the client getting their money back.",
            "**Sanity-check against the request-and-accept handshake.** It is unusual -- most "
            "booking products have no acceptance step -- so the flow diagrams are where the team "
            "will spot if it does not hold together. Read "
            "`docs/implementation/lexpert_plan.md` section 1.1 first.",
            "**Number the screens** and use those numbers in the wireframes later. It makes "
            "review conversations possible without pointing at a picture.",
        ],
        "validation": [
            "Every frontend issue in the backlog maps to at least one screen in the inventory, "
            "and no screen in the inventory lacks an issue -- gaps in either direction are "
            "reported.",
            "All five critical journeys are drawn end to end, including failure branches.",
            "All four rejection paths -- decline, expiry, withdrawal, cancellation -- appear with "
            "what the client sees in each.",
            "Each portal's navigation is drawn and no cross-portal route exists.",
            "Walked through with the technical lead against the plan document, and the handshake "
            "flow specifically confirmed.",
        ],
        "deliverables": [
            "A Figma or FigJam file with the flows, linked from "
            "`docs/design/README.md`.",
            "`docs/design/screen_inventory.md` -- the numbered screen list per portal, mapped to "
            "issue ids.",
            "A list of screens the backlog is missing, raised as comments on the relevant issues.",
        ],
    },
    # ------------------------------------------------------------------ visual
    {
        "id": "UX-03",
        "title": "Visual direction and design tokens",
        "milestone": "MVP",
        "labels": ["design", "ux"],
        "size": "M",
        "depends": ["UX-02", "UX-09"],
        "branch": "chore/ux-03-visual-direction",
        "goal": (
            "Decide what Lexpert looks like, and express it as a small set of named tokens the "
            "code can consume directly. This comes after the flows on purpose: a visual "
            "direction chosen before you know what screens exist tends to survive as decoration "
            "that the screens then fight."
        ),
        "requirements": [
            "**Two or three distinct directions**, each shown on the same two real screens -- "
            "the client search results and the professional's request inbox. Same content, "
            "different treatment, so the comparison is about the direction and not about the "
            "screen.",
            "Each direction articulated in **one sentence about what it is trying to make someone "
            "feel**, and checked against the audiences in the brief. \"Trustworthy and calm\" is "
            "a reasonable target for this product; \"exciting\" is not.",
            "One direction chosen with the technical lead, then developed into the token set.",
            "**Colour tokens**: one accent, a neutral ramp of about five steps, and three "
            "semantic colours (success, warning, danger). Money and escrow states reuse the "
            "semantic set rather than adding their own. Resist going beyond this.",
            "**Type tokens**: two typefaces at most, and a type scale of six or seven steps. The "
            "faces must support French diacritics properly and should have a plausible Arabic "
            "companion for Beta -- check before committing.",
            "**Spacing, radius, border and shadow tokens** on a consistent scale (a 4px base is "
            "conventional and works). Elevation used sparingly and by role, not stamped on every "
            "surface.",
            "**Both light and dark palettes**, defined at token level. Redefining tokens is the "
            "only supported way to theme; the code has no other mechanism.",
            "Tokens **named by role, not appearance**: `color-danger`, never `color-red`.",
            "Exported as JSON via Tokens Studio, ready for `UX-04` to turn into CSS custom "
            "properties.",
            "**Every foreground and background pairing checked for WCAG 2.2 AA contrast** -- 4.5:1 "
            "for body text, 3:1 for large text and for meaningful non-text elements. Record the "
            "measured ratios, do not eyeball them.",
        ],
        "recommended": [
            "**Choose the accent last, and choose it for contrast.** Pick a hue that reaches "
            "4.5:1 against both your light and dark backgrounds at a usable saturation. Many "
            "attractive accents fail this and get quietly lightened until they are grey. Test "
            "the accent before falling in love with it.",
            "**Do not start with a mood board.** Start by putting real content -- a real "
            "professional profile with a real-length French biography -- into a plain layout, "
            "then make decisions about that. Directions built on placeholder text collapse when "
            "the real strings arrive.",
            "**Look at what medical and legal products actually do**, and understand why they are "
            "usually restrained. Blue and green dominate health interfaces partly through "
            "convention and partly because they test as calm. You may deviate -- but knowingly, "
            "and this is not the product to be adventurous with.",
            "**Beware of two AI-and-template defaults** currently everywhere: warm cream with a "
            "serif and a terracotta accent, and near-black with a single acid-green pop. Both "
            "read as generic to anyone who looks at a lot of interfaces.",
            "**Check the typeface for French properly.** Set a paragraph containing "
            "`é è ê ë à â ù û ü ô î ï ç œ` and the guillemets `« »`, at small sizes. Some "
            "otherwise good faces have poor diacritic spacing that only shows in running text.",
            "**Tools for contrast.** The Stark plugin or Figma's own contrast checker; WebAIM's "
            "checker for individual pairs. Check the *worst* case, not the best -- placeholder "
            "text on a disabled input is usually the pairing that fails.",
            "**Keep the ramp small.** Five neutrals is genuinely enough for background, surface, "
            "border, secondary text and primary text. Every extra step is one more decision at "
            "every future screen.",
        ],
        "validation": [
            "Two or three directions were presented on the same two screens and one was chosen "
            "with the technical lead. Record the reasoning, including what was rejected.",
            "Every token is named by role; a review of the names finds no appearance-based name.",
            "Every text and background pairing in both themes meets WCAG 2.2 AA, with the "
            "measured ratio recorded per pair.",
            "The chosen typefaces render French diacritics and guillemets correctly at 14px, "
            "verified in a real paragraph.",
            "The token JSON exports cleanly and `UX-04` can consume it without hand-editing.",
            "The colour set is within the stated budget: one accent, about five neutrals, three "
            "semantic.",
            "Both themes are shown on the same two screens and both are legible.",
        ],
        "deliverables": [
            "A Figma file with the directions explored and the chosen one developed.",
            "`design/tokens.json` -- the Tokens Studio export, committed.",
            "`docs/design/visual_direction.md` -- what was chosen, what was rejected, why, and "
            "the recorded contrast ratios.",
        ],
        "notes": (
            "The contrast requirement is the part most likely to be treated as a formality and "
            "then to cause real rework. An accent that fails AA has to change, and by then it is "
            "in every screen. Measure it on the day you choose it."
        ),
    },
    {
        "id": "UX-04",
        "title": "Token pipeline: Figma tokens to CSS custom properties",
        "milestone": "MVP",
        "labels": ["frontend", "ux", "infra"],
        "size": "S",
        "depends": ["UX-03", "FND-01"],
        "branch": "feature/ux-04-token-pipeline",
        "goal": (
            "Turn the committed `design/tokens.json` into CSS custom properties the web app "
            "consumes, with a check that they cannot drift apart. This is the mechanical join "
            "between design and code, and it is what stops the design saying 16px while the code "
            "ships 15px."
        ),
        "requirements": [
            "A build step turning `design/tokens.json` into "
            "`apps/web/src/styles/tokens.css` as CSS custom properties, run through an npm "
            "script and committed output so a clean clone needs no design tooling.",
            "Light and dark palettes emitted as the three-state structure the app needs: a bare "
            "`:root` carrying the complete light palette, a "
            "`prefers-color-scheme: dark` block guarded so an explicit light choice still wins, "
            "and an explicit `[data-theme]` override.",
            "Tailwind configured to consume the tokens rather than duplicating them, so a "
            "Tailwind class and a token can never disagree.",
            "A CI check that regenerating from `tokens.json` produces no diff, so an edit to "
            "either side without the other fails the build.",
            "A lint rule rejecting a hard-coded colour, spacing or font-size literal in "
            "component CSS. Tokens or nothing.",
            "Document, in the design docs, what a designer changes to alter the palette and what "
            "happens next -- one command, no code edit.",
        ],
        "validation": [
            "`npm run tokens` regenerates `tokens.css` and produces no diff on an unchanged "
            "`tokens.json`.",
            "Changing a colour in `tokens.json` and regenerating changes exactly that custom "
            "property.",
            "CI fails when `tokens.json` is edited without regenerating.",
            "The lint rule fails on a component with `color: #fff` and passes on the real tree.",
            "A component styled only through tokens renders correctly in light, dark and "
            "unstamped-system states -- tested in all three.",
        ],
        "deliverables": [
            "The token build script and its npm entry point.",
            "`apps/web/src/styles/tokens.css`, generated and committed.",
            "Tailwind configuration reading the tokens.",
            "The CI drift check and the lint rule.",
            "A `## Changing the palette` section in `docs/design/README.md`.",
        ],
    },
    {
        "id": "UX-05",
        "title": "Component foundation: Radix primitives, Tailwind and the primitive set",
        "milestone": "MVP",
        "labels": ["frontend", "ux"],
        "size": "L",
        "depends": ["UX-04", "UX-06"],
        "branch": "feature/ux-05-component-foundation",
        "goal": (
            "Build the component layer every screen issue reuses: Radix Primitives for accessible "
            "behaviour, our tokens for appearance, and the primitive set named to match the Figma "
            "library. This replaces the small ad-hoc primitive set that FND-06 would otherwise "
            "invent."
        ),
        "requirements": [
            "Radix Primitives and Tailwind installed and wired to the `UX-04` tokens.",
            "The primitive set, each with every state the design specifies (default, hover, "
            "focus-visible, active, disabled, error, loading): button in its variants, text "
            "input, textarea, select, checkbox, radio, switch, form field with label and error, "
            "dialog, sheet, dropdown menu, tabs, tooltip, toast, badge, avatar, spinner, "
            "skeleton.",
            "The **shared state components** from the brief's state matrix, since every screen "
            "needs them and they are what gets forgotten: loading skeleton, empty state, error "
            "state with retry, offline notice, permission-denied screen.",
            "The domain components the backlog already assumes, so they exist once rather than "
            "three times: money input (dinars and millimes to integer millimes), money display, "
            "date and time display with timezone, a countdown driven by a **server** timestamp, "
            "and a consultation status pill.",
            "**Component names identical to the Figma library names** from `UX-06`. A mismatch "
            "here is a permanent tax on every screen review.",
            "**CSS logical properties throughout** -- `margin-inline-start`, never "
            "`margin-left` -- plus a lint rule rejecting physical properties, so Arabic in Beta "
            "is a translation job rather than a re-layout.",
            "Every interactive component operable by keyboard with a visible focus state that is "
            "designed, not the browser default.",
            "A component gallery route, development-only, rendering every component in every "
            "state on one page. This is what makes visual review and `UX-10`'s regression "
            "harness possible.",
        ],
        "validation": [
            "Every component renders in every documented state on the gallery route.",
            "Keyboard-only walk of the gallery: every interactive component is reachable, "
            "operable, and visibly focused.",
            "`axe` reports no violations on the gallery route.",
            "The logical-property lint rule fails on a component using `margin-left` and passes "
            "on the real tree.",
            "Unit test: the money input converts `45`, `45,5`, `45,500` and `0,001` correctly and "
            "rejects more than three decimal places.",
            "Unit test: the countdown derives from a server timestamp and is unaffected by a "
            "skewed client clock.",
            "A name-parity check between the Figma library and the code components finds no "
            "mismatch.",
            "The gallery renders correctly in light, dark and unstamped-system themes.",
            "At a 375px viewport, no component overflows its container.",
        ],
        "deliverables": [
            "`apps/web/src/components/` with the primitive, state and domain components.",
            "The development-only component gallery route.",
            "The logical-property lint rule.",
            "Component tests for the domain components.",
            "`docs/design/component_map.md` -- Figma name to code path, both directions.",
        ],
        "notes": (
            "Why Radix rather than a full library: the hard parts of accessible components are "
            "focus trapping in dialogs, combobox keyboard semantics and date-picker screen-reader "
            "behaviour. Those are where a small team loses weeks and still ships bugs. Radix "
            "provides them unstyled, so the visual identity stays ours and there is no theme "
            "system to fight. Bundle size matters too -- these users are on variable mobile "
            "networks.\n\n"
            "If velocity turns out to dominate, Mantine is the better full-library alternative "
            "than MUI: lighter, good accessibility, and RTL support built in. Raise it on this "
            "issue rather than switching quietly."
        ),
    },
    {
        "id": "UX-06",
        "title": "Figma component library, mapped to the code components",
        "milestone": "MVP",
        "labels": ["design", "ux"],
        "size": "M",
        "depends": ["UX-03"],
        "branch": "chore/ux-06-component-library",
        "goal": (
            "Build the Figma library the screen designs are assembled from, with every state "
            "designed rather than left to the implementer's judgement, and named so the mapping "
            "to code is obvious."
        ),
        "requirements": [
            "Every component in the `UX-05` list, built from the `UX-03` tokens as Figma "
            "variables -- never a pasted hex value.",
            "**Every state designed**: default, hover, focus-visible, active, disabled, error, "
            "loading. The focus state especially -- if you do not design it, the browser default "
            "ships, and it usually fails contrast against a coloured surface.",
            "The shared state components from the brief's section 6: loading skeleton, empty "
            "state, error with retry, offline, permission denied. Each with real French copy from "
            "`UX-09`, not placeholder text.",
            "The domain components: money display, date and time with timezone, countdown, and a "
            "**consultation status pill for all twelve states** using the `UX-09` labels.",
            "Variants and properties structured so a screen designer picks a component and sets "
            "a state, rather than detaching and editing it.",
            "**Component names identical to the code names** in `UX-05`. Agree the list with the "
            "implementer before building, not after.",
            "Each component annotated with which parts **mirror under RTL** and which do not -- a "
            "back arrow mirrors, a logo does not. Cheap now, expensive to reconstruct in Beta.",
            "Every component tolerating a label 40% longer than the French, since Arabic and "
            "longer French strings both break fixed-width components.",
        ],
        "recommended": [
            "**Build the states before the variants.** It is tempting to build a beautiful "
            "default button and move on. The states are where the work is and where the "
            "implementer has to guess if you skip them.",
            "**Use Figma variables bound to the token names**, so a palette change in `UX-03` "
            "propagates rather than requiring a manual sweep. This is the main reason to do "
            "`UX-03` first.",
            "**Design the focus state deliberately.** A 2px outline in the accent colour with a "
            "2px offset is a reasonable default that usually passes contrast. Check it against "
            "every surface the component sits on, including the accent-coloured ones.",
            "**Put the real French strings in.** A component library full of \"Lorem ipsum\" or "
            "English placeholders hides the fact that French is typically 15-20% longer than "
            "English, which is exactly what breaks buttons.",
            "**Agree the name list with the implementer in a fifteen-minute conversation** before "
            "building anything. Renaming forty components later is miserable and it always gets "
            "half-done.",
            "**Do not build components the MVP does not use.** A carousel, a data grid, a rich "
            "text editor -- if no screen in the inventory needs it, it is wasted work that then "
            "needs maintaining.",
        ],
        "validation": [
            "Every component in the `UX-05` list exists with all seven states.",
            "No component contains a hard-coded colour or spacing value; all bind to variables.",
            "The status pill covers all twelve consultation states with `UX-09` labels.",
            "The name list matches the code component list exactly, agreed with the implementer "
            "in writing.",
            "Every component is annotated for RTL mirroring.",
            "Each component still lays out correctly with its longest label extended by 40%.",
            "All state components carry real French copy, not placeholder text.",
        ],
        "deliverables": [
            "The Figma component library file, published, linked from `docs/design/README.md`.",
            "The agreed component name list, committed to `docs/design/component_map.md`.",
            "The RTL mirroring annotations, in the Figma file.",
        ],
    },
    # ------------------------------------------------------------------ screens
    {
        "id": "UX-07",
        "title": "Client journey screens, every state",
        "milestone": "MVP",
        "labels": ["design", "ux"],
        "size": "L",
        "depends": ["UX-02", "UX-06"],
        "branch": "chore/ux-07-client-screens",
        "goal": (
            "Design every client-facing screen at mobile width, in every state. This is the "
            "surface that decides whether a wary first-time user trusts an unfamiliar payment "
            "model, so it carries the product's central bet."
        ),
        "requirements": [
            "Every client screen in the `UX-02` inventory: register and login, phone "
            "verification, search and filters, professional profile, slot picker, request "
            "checkout, request-sent confirmation, consultations list, consultation detail, "
            "waiting room, consultation room, post-consultation, dispute form and status, "
            "rating.",
            "**Mobile-first: the 375px artboard is the primary one.** Add a desktop layout only "
            "where it changes something meaningful.",
            "**Every state from the brief's section 6 for every screen**, laid out side by side "
            "on a States page per screen. This is the deliverable the implementer works from.",
            "The **money story** made visible: the price breakdown before committing, the money "
            "timeline on a consultation detail, the hold-window countdown, and the refund message "
            "on each of the four rejection paths.",
            "The **request-sent confirmation** treated as a first-class screen, not a toast. It "
            "must convey that the request is sent, the money is held, the professional has until "
            "a stated time, and a decline refunds in full -- without alarming anyone.",
            "The **MVP simulation notice** placed on every money surface, using the `UX-09` "
            "wording, unmissable before the confirm action.",
            "**No fake card-entry form.** The simulated payment step visibly stands in for a real "
            "one without imitating it. This is a hard rule from the brief, section 4.3.",
            "The **consultation room** designed for a weak connection: the connection-quality "
            "indicator, the audio-only fallback as a normal state rather than an error, "
            "reconnecting, and the denied-camera-permission screen.",
            "The **pre-call device check** designed properly. Most failed teleconsultations are "
            "permission or device problems, not network problems, so this screen prevents more "
            "failures than any other.",
            "Timezone display for a diaspora client: their local time primary, the "
            "professional's alongside where it differs.",
        ],
        "recommended": [
            "**Design the states page first for each screen, then the happy path.** Working the "
            "other way round means the happy path becomes precious and the states get squeezed "
            "into it.",
            "**Test the request-and-accept flow on real people.** The acceptance step is unusual, "
            "and \"my money is held but the consultation is not confirmed\" is a genuinely "
            "confusing idea. Show five people the confirmation screen and ask what happens next. "
            "If they say \"I have an appointment\", the screen has failed.",
            "**Study Doctolib's slot picker before designing yours.** It is the most-used "
            "French-language version of exactly this problem, and the constraints -- many slots, "
            "small screen, timezone -- are the same.",
            "**Study Qare or Livi for the waiting room and device check.** These two screens are "
            "specific to teleconsultation and are usually the weakest part of a first attempt.",
            "**For the money timeline, look at how Stripe or Wise show a payment's history**: a "
            "dated vertical list of what happened, in plain language. That pattern transfers "
            "directly and needs no invention.",
            "**Design the empty states as instructions.** A new client with no consultations "
            "should be told what to do next, not apologised to.",
            "**Check every screen at 375px with the real French strings**, not with English "
            "placeholders. French runs longer, and the slot picker and price breakdown are where "
            "that first breaks.",
        ],
        "validation": [
            "Every client screen in the inventory has a States page covering the applicable "
            "states from the brief's section 6.",
            "Five people were shown the request-sent confirmation and at least four correctly "
            "described what happens next and where their money is. Record the results, including "
            "the failures.",
            "The four rejection paths each have a screen with its refund message.",
            "The simulation notice appears on every money surface and is unmissable before the "
            "confirm action.",
            "No screen contains a card-number input or anything card-shaped.",
            "Every screen is designed at 375px with real French copy and nothing overflows.",
            "Every screen uses only `UX-06` components; a review finds no detached or one-off "
            "component.",
            "Contrast re-checked on the composed screens, not only on the isolated components.",
            "Walked through with the technical lead against the relevant backlog issues.",
        ],
        "deliverables": [
            "A Figma file per portal area, with a States page per screen, linked from "
            "`docs/design/README.md`.",
            "A screen-to-issue mapping added to `docs/design/screen_inventory.md`, so the "
            "implementer can find the design for the issue in front of her.",
            "The user-test findings for the request-sent confirmation.",
        ],
        "notes": (
            "The largest design issue and the one most worth spending time on. If something has "
            "to be cut, cut desktop layouts -- not states, and not the user test on the "
            "confirmation screen."
        ),
    },
    {
        "id": "UX-08",
        "title": "Professional and admin portal screens",
        "milestone": "MVP",
        "labels": ["design", "ux", "admin"],
        "size": "L",
        "depends": ["UX-07"],
        "branch": "chore/ux-08-pro-admin-screens",
        "goal": (
            "Design the two portals for repeat users. Both are operated rather than read, so the "
            "craft shifts from reassurance to information density -- and they should not look "
            "like the client app."
        ),
        "requirements": [
            "**Professional portal**: the onboarding wizard for all three verticals with a "
            "per-vertical field set, the verification status screens for all five states, profile "
            "and rate editor, availability editor, the request inbox, the consultation dashboard, "
            "consultation detail, and the earnings view.",
            "**Admin back-office**: the verification review queue and detail, the dispute queue "
            "and mediation screen, and the notification log.",
            "The **onboarding wizard** designed to be genuinely easy. The feasibility study's "
            "cold-start analysis says supply comes first, so this screen is the platform's first "
            "impression on the side that has to be recruited.",
            "The **request inbox** designed for speed: a professional between appointments should "
            "accept or decline in seconds, on a phone, with the deadline and their net earnings "
            "visible without a tap.",
            "The **verification review screen** laid out for comparison: the declared credentials "
            "beside the uploaded document, so the reviewer can read the CNOM number off the "
            "certificate without scrolling or downloading.",
            "The **availability editor** usable on a phone. A seven-column week grid is not; use "
            "a per-day list or accordion.",
            "**Density and desktop-first for the admin portal**, mobile-first for the "
            "professional portal. These are different problems and should look different.",
            "Every state from the brief's section 6, plus the professional-specific ones: not yet "
            "approved, more information requested, rejected and resubmitting.",
            "**Destructive and consequential actions** -- decline, reject, refund, partial split "
            "-- each with a confirmation stating the consequence, and the decline confirmation "
            "stating plainly that the client is refunded in full.",
        ],
        "recommended": [
            "**Design the admin portal denser than feels comfortable.** Someone will use this "
            "screen four hundred times. Generous spacing that reads as calm on a client screen "
            "reads as wasted scrolling here. Look at how an email client or a support tool packs "
            "a queue.",
            "**For the review screen, think about the actual physical task**: eyes moving between "
            "a number on a certificate and a number in a field. Put them close together and at "
            "the same size. A two-pane layout with the document at a readable zoom beats anything "
            "requiring a download.",
            "**For the request inbox, assume one hand and a moving bus.** Large targets, the "
            "decision visible without scrolling, and destructive and safe actions far enough "
            "apart that a thumb cannot confuse them.",
            "**Study an operations tool, not a consumer app**, for the admin side -- Stripe's "
            "dashboard, Linear, or Zendesk. The pattern language for queues, filters and bulk "
            "review is well established.",
            "**Design the wizard's error recovery, not just its steps.** A professional who "
            "uploads the wrong document, or whose file is rejected, is the case that decides "
            "whether they persist or give up.",
            "**Show the professional their net earnings, not the gross**, wherever they make a "
            "decision. What they care about is what arrives.",
        ],
        "validation": [
            "Every professional and admin screen in the inventory has a States page.",
            "The three verticals each render in the onboarding wizard with their own field set, "
            "driven by data rather than three separate designs.",
            "All five verification states have a professional-facing screen.",
            "The review screen shows credentials and document simultaneously without scrolling at "
            "1280px.",
            "The availability editor is usable at 375px, verified in a click-through prototype.",
            "The request inbox shows deadline and net earnings without a tap at 375px.",
            "Every destructive action has a confirmation stating its consequence.",
            "The admin portal is visibly denser than the client portal -- compare a queue against "
            "a client list.",
            "Walked through with the technical lead, and the review screen walked through with "
            "whoever will actually do the reviewing.",
        ],
        "deliverables": [
            "Figma files for the professional and admin portals, with States pages.",
            "The screen-to-issue mapping extended in `docs/design/screen_inventory.md`.",
            "A click-through prototype of the request inbox and the review screen, for the "
            "walkthroughs.",
        ],
    },
    # ------------------------------------------------------------------ quality gates
    {
        "id": "UX-10",
        "title": "Accessibility standard and design quality gates in CI",
        "milestone": "MVP",
        "labels": ["frontend", "ux", "ci", "test"],
        "size": "M",
        "depends": ["UX-05"],
        "branch": "feature/ux-10-design-qa",
        "goal": (
            "Make the accessibility and visual standards mechanical rather than aspirational. "
            "Sixteen frontend issues say \"accessible\"; this is what decides whether that is "
            "true, and it catches a regression on the screen nobody reopened."
        ),
        "requirements": [
            "A written standard: **WCAG 2.2 AA**, with the specific commitments spelled out -- "
            "contrast ratios, visible focus on every interactive element, full keyboard "
            "operation, touch targets at least 44px, no meaning carried by colour alone, and "
            "correct heading order.",
            "`axe-core` running in CI over the component gallery and every route reachable "
            "without a login, failing the build on a violation.",
            "Automated **contrast verification of the token pairings**, so a palette change that "
            "breaks AA fails the build rather than being noticed months later.",
            "**Visual regression** on the component gallery and the key screens, using the "
            "Playwright already arriving with `E2E-02` rather than a second tool. Baselines "
            "committed; a diff fails the build until the baseline is deliberately updated.",
            "A **keyboard-navigation test** over the critical journey: complete a consultation "
            "request without a mouse.",
            "A `prefers-reduced-motion` check: every animation is suppressed when it is set.",
            "The CI job name added to `.github/ruleset.json` in the same change, or "
            "`scripts/check_ruleset_contexts.py` fails the build.",
            "A short accessibility section in `CONTRIBUTING.md` stating the standard and how to "
            "check locally, so it is not only enforced but explained.",
        ],
        "validation": [
            "`axe` runs in CI and fails on a deliberately introduced violation -- an unlabelled "
            "input.",
            "The contrast check fails when a token is changed to break AA.",
            "Visual regression fails on a deliberate one-pixel padding change and passes on the "
            "real tree.",
            "The keyboard test completes a consultation request with no pointer events.",
            "With `prefers-reduced-motion: reduce`, no animation runs.",
            "`python scripts/check_ruleset_contexts.py` passes with the new job in both the "
            "workflow and the ruleset.",
            "Baselines are committed and a fresh clone reproduces them without a local rebuild.",
        ],
        "deliverables": [
            "`docs/design/accessibility_standard.md`.",
            "The `axe` and contrast checks, and the visual regression harness with baselines.",
            "The CI job, added to `ci.yml` and `.github/ruleset.json`.",
            "An `## Accessibility` section in `CONTRIBUTING.md`.",
        ],
        "notes": (
            "Visual regression earns its place here but has one failure mode worth naming: a "
            "flaky baseline gets ignored, then disabled. Keep the screenshot surface small and "
            "deterministic -- the gallery plus a handful of key screens, with animations and "
            "real timestamps frozen. A suite that cries wolf is worse than no suite."
        ),
    },
]
