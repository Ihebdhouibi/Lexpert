# Design documentation

Start with the **[design brief](design_brief.md)**. It is the grounding for everything else:
what the product is, who uses it, what is not negotiable, and where to look for good precedent.
It is written for a designer early in their career and it does not assume you have designed a
marketplace or a health product before.

## The documents

| Document | What it holds | Produced by |
| --- | --- | --- |
| [design_brief.md](design_brief.md) | Product, audiences, constraints, principles, guardrails, references, suggested order of work | Committed up front |
| `research_findings.md` | Audience contexts, the trust findings, and which brief assumptions the research contradicted | `UX-01` |
| `competitor_teardowns.md` | Annotated journeys through Doctolib or Qare, DabaDoc, and one handshake marketplace | `UX-01` |
| `copy_guide.md` | French glossary, tone, the twelve client-facing state labels, error message rules, money and date formatting | `UX-09` |
| `screen_inventory.md` | Numbered screen list per portal, mapped to issue ids and to the Figma frames | `UX-02`, extended by `UX-07` and `UX-08` |
| `visual_direction.md` | What was chosen, what was rejected, why, and the measured contrast ratios | `UX-03` |
| `component_map.md` | Figma component name to code path, both directions | `UX-06`, `UX-05` |
| `accessibility_standard.md` | The WCAG 2.2 AA commitments and how to check them locally | `UX-10` |

## The Figma files

Linked here as they are created. Keep the list current -- a Figma file nobody can find is a
Figma file nobody uses.

| File | Contents | Issue |
| --- | --- | --- |
| _(not yet created)_ | Flows and information architecture | `UX-02` |
| _(not yet created)_ | Visual direction explorations and the chosen direction | `UX-03` |
| _(not yet created)_ | Component library, published | `UX-06` |
| _(not yet created)_ | Client journey screens, with a States page per screen | `UX-07` |
| _(not yet created)_ | Professional and admin portal screens | `UX-08` |

## How design reaches the code

The handoff is **design tokens**, not screenshots.

```
Figma variables  ->  Tokens Studio export  ->  design/tokens.json  (committed)
                                                      |
                                          npm run tokens  (UX-04)
                                                      v
                                   apps/web/src/styles/tokens.css
                                                      |
                                        Tailwind + Radix components  (UX-05)
```

Two conventions make this work, and both belong to the designer:

1. **Name tokens by role, not appearance.** `color-danger`, never `color-red`.
2. **Name Figma components exactly as the code components are named**, so the implementer never
   has to guess the mapping. Agree the list before building, not after.

CI fails if `design/tokens.json` and the generated CSS disagree, so the two cannot drift.

## Changing the palette

Edit the token in Figma, re-export to `design/tokens.json`, then:

```bash
npm --prefix apps/web run tokens
```

Commit both the JSON and the regenerated CSS. No component file is touched. If the change breaks
a WCAG 2.2 AA contrast pairing, the `UX-10` check fails the build rather than letting it ship.

## The rule that matters most

**Every screen ships with its states.** Loading, empty, error, offline, permission denied — plus
the ones specific to this product: not yet approved, pending acceptance, declined, expired,
withdrawn, hold window counting down, disputed, released, refunded.

On Lexpert the states are most of the product. A design that covers only the happy path causes
rework in every single UI issue. See the brief's section 6 for the full matrix.
