**Task id:** `CON-03`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `CON-02`, `ESC-12`
**Branch:** `feature/con-03-consultation-room-ui`
**Labels:** `frontend`, `consultation`

## Goal

The screen where the consultation actually happens. Video quality on Tunisian networks is called out in the feasibility study as a key acceptance criterion, so graceful degradation is a requirement here rather than a refinement.

## Requirements

1. A waiting room before the join window opens: the countdown, who you are meeting, a device check for camera and microphone, and what to do if the other party is late.
2. The room: local and remote video, mute, camera toggle, a connection-quality indicator, and a visible elapsed timer against the booked duration.
3. **Audio-only fallback**, both automatic on sustained poor quality and manually selectable, with a French explanation when it engages. The consultation must remain usable on a weak mobile connection.
4. Reconnection handling: a dropped connection attempts to rejoin with visible status, and the participation record tolerates the gap rather than treating it as a leave.
5. The professional has an end-consultation control with a confirmation; the client has a leave control that makes clear the difference between leaving and ending.
6. After the end: a post-consultation screen explaining the one-hour hold window, when the professional is paid, and a clear route to raise a dispute (DSP-03) inside that window.
7. Permission handling: a browser that denies camera or microphone access gets a French explanation of how to grant it, not a blank screen.
8. Mobile-first, since most consultations will happen on a phone: usable controls at a 375px viewport, and the layout must survive an on-screen keyboard appearing.
9. No recording, no screenshots, and no local persistence of anything from the session. Nothing about the consultation's content is written anywhere.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: the waiting room renders the countdown and the device check, and the join control enables only inside the window.
- Component test: mute and camera toggles call the SDK and reflect state.
- Component test: a simulated sustained quality drop switches to audio-only and shows the explanation.
- Component test: manual audio-only selection works and is reversible.
- Component test: a simulated disconnect shows reconnecting status and rejoins.
- Component test: the professional's end control requires confirmation and calls the end endpoint once.
- Component test: the client's leave control does not call the end endpoint.
- Component test: the post-consultation screen explains the hold window and links to the dispute flow.
- Component test: denied media permissions render the explanatory screen.
- Test asserting nothing is written to `localStorage`, `sessionStorage` or IndexedDB during a session.
- Manual: hold a real consultation between two devices on a throttled connection and confirm the audio-only fallback engages and the consultation stays usable.

## Deliverables

- `apps/web/src/features/consultation/` with the waiting room, room, controls and post-consultation screens.
- A quality-monitoring hook driving the fallback.
- Consultation keys in `fr.ts`.
- Component tests covering every item above, plus a note in the PR describing the manual throttled-network test and its result.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/con-03-consultation-room-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
