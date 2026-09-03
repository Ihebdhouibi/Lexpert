"""Derive the delivery roadmap from the issue data.

Everything here is computed, not written down twice: the parallelisable waves, the critical
path, the per-phase totals, and what each issue unblocks. The only editorial input is
`phases.py`, which says how workstreams group and what each phase can demonstrate.

Two numbers are worth understanding before quoting them.

**Issue-days** are effort, from the S/M/L size on each issue, not calendar days. They do not
account for review, rework, or a person working on one thing at a time.

**The critical path** is the longest dependency chain by issue-days. It is the floor on
elapsed time however many people work, because each link cannot start until the one before
it lands. It is the number that matters for "when could this be done", and the reason the
total effort figure is misleading on its own.
"""

from __future__ import annotations

from phases import EARLY_STARTS, OPEN_DECISIONS, PHASES

# Effort in days per size. Deliberately coarse: the point is relative weight and a defensible
# total, not a schedule. Keep in step with SIZE_LEGEND in generate.py.
SIZE_DAYS = {"S": 0.5, "M": 1.5, "L": 3.5}


def prefix_of(task_id: str) -> str:
    return task_id.rsplit("-", 1)[0]


def build(all_issues: list[dict[str, object]]) -> dict[str, object]:
    """Return the roadmap model. Raises on any inconsistency worth failing a build over."""
    by_id = {str(i["id"]): i for i in all_issues}
    deps = {k: [str(d) for d in v["depends"]] for k, v in by_id.items()}  # type: ignore[union-attr]

    unblocks: dict[str, list[str]] = {k: [] for k in by_id}
    for task_id, ds in deps.items():
        for dep in ds:
            unblocks[dep].append(task_id)

    # --- every MVP workstream must be planned into exactly one phase
    mvp_prefixes = {prefix_of(k) for k, v in by_id.items() if v["milestone"] == "MVP"}
    planned: dict[str, str] = {}
    for phase in PHASES:
        for prefix in phase["prefixes"]:  # type: ignore[union-attr]
            if prefix in planned:
                raise SystemExit(
                    f"workstream {prefix} appears in two phases: "
                    f"{planned[prefix]!r} and {phase['name']!r}"
                )
            planned[str(prefix)] = str(phase["name"])
    unplanned = mvp_prefixes - set(planned)
    if unplanned:
        raise SystemExit(
            f"MVP workstreams missing from phases.py: {sorted(unplanned)}. "
            "Add them to a phase so they cannot go unplanned."
        )
    stray = set(planned) - mvp_prefixes
    if stray:
        raise SystemExit(f"phases.py plans workstreams that have no MVP issues: {sorted(stray)}")

    # --- waves: Kahn levelling. Wave N depends only on waves below it, so a wave is what
    #     *can* run in parallel, not what must.
    wave_of: dict[str, int] = {}
    pending = dict(deps)
    wave = 0
    while pending:
        ready = [k for k, ds in pending.items() if all(d in wave_of for d in ds)]
        if not ready:
            raise SystemExit(f"dependency cycle among {sorted(pending)}")
        for k in ready:
            wave_of[k] = wave
        for k in ready:
            del pending[k]
        wave += 1

    # --- critical path, restricted to MVP: Beta work cannot delay the MVP milestone.
    mvp = {k: v for k, v in by_id.items() if v["milestone"] == "MVP"}
    mvp_deps = {k: [d for d in deps[k] if d in mvp] for k in mvp}
    memo: dict[str, tuple[float, list[str]]] = {}

    def longest(node: str) -> tuple[float, list[str]]:
        if node in memo:
            return memo[node]
        own = SIZE_DAYS[str(mvp[node]["size"])]
        best = (own, [node])
        for dep in mvp_deps[node]:
            cost, path = longest(dep)
            if cost + own > best[0]:
                best = (cost + own, [*path, node])
        memo[node] = best
        return best

    cp_days, cp_chain = max((longest(k) for k in mvp), key=lambda pair: pair[0])
    cp_set = set(cp_chain)

    def days(ids: list[str]) -> float:
        return round(sum(SIZE_DAYS[str(by_id[i]["size"])] for i in ids), 1)

    def issue_view(task_id: str) -> dict[str, object]:
        issue = by_id[task_id]
        goal = str(issue["goal"])
        # First sentence of the goal reads as a one-line deliverable, so the roadmap does not
        # need a second summary field that could drift from the issue body.
        head = goal.split(". ")[0].rstrip(".")
        return {
            "id": task_id,
            "title": issue["title"],
            "one_line": head,
            "size": issue["size"],
            "days": SIZE_DAYS[str(issue["size"])],
            "depends": deps[task_id],
            "unblocks": sorted(unblocks[task_id]),
            "labels": issue["labels"],
            "wave": wave_of[task_id],
            "critical": task_id in cp_set,
            "milestone": issue["milestone"],
        }

    phases_out: list[dict[str, object]] = []
    for index, phase in enumerate(PHASES, 1):
        ids = [
            k
            for k in mvp
            if prefix_of(k) in phase["prefixes"]  # type: ignore[operator]
        ]
        # Order within a phase is dependency order, then id, so the list reads as a work order.
        ids.sort(key=lambda k: (wave_of[k], k))
        phases_out.append(
            {
                "number": index,
                "name": phase["name"],
                "prefixes": phase["prefixes"],
                "what": phase["what"],
                "checkpoint": phase["checkpoint"],
                "days": days(ids),
                "issues": [issue_view(k) for k in ids],
            }
        )

    beta_ids = sorted(k for k, v in by_id.items() if v["milestone"] == "Beta")

    return {
        "totals": {
            "issues": len(by_id),
            "mvp_issues": len(mvp),
            "beta_issues": len(beta_ids),
            "mvp_days": days(list(mvp)),
            "beta_days": days(beta_ids),
            "waves": wave,
        },
        "critical_path": {
            "days": round(cp_days, 1),
            "count": len(cp_chain),
            "chain": cp_chain,
        },
        "phases": phases_out,
        "beta": [issue_view(k) for k in beta_ids],
        "early_starts": [
            {**entry, **issue_view(entry["id"])} for entry in EARLY_STARTS if entry["id"] in by_id
        ],
        "open_decisions": [d for d in OPEN_DECISIONS if d["id"] in by_id],
        "waves": [
            {
                "wave": w,
                "ids": sorted(k for k, v in wave_of.items() if v == w),
            }
            for w in range(wave)
        ],
    }
