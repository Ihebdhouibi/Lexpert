"""Generate the Lexpert backlog artifacts from the issue data.

Outputs, all overwritten on every run so they cannot drift apart:

  docs/implementation/lexpert_issues.md   the human-readable backlog
  .github/issue-bodies/<id>.md            one body file per issue, for `gh issue create`
  scripts/create_issues.sh                the bulk-create script

Run from the repository root:

    python scripts/backlog/generate.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from issues_flow import ISSUES as ISSUES_FLOW  # noqa: E402
from issues_foundation import ISSUES as ISSUES_FOUNDATION  # noqa: E402
from issues_marketplace import ISSUES as ISSUES_MARKETPLACE  # noqa: E402
from issues_sessions import ISSUES as ISSUES_SESSIONS  # noqa: E402
from render_roadmap import render as render_roadmap  # noqa: E402
from roadmap import build as build_roadmap  # noqa: E402
from workstreams import WORKSTREAMS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ALL_ISSUES: list[dict[str, object]] = [
    *ISSUES_FOUNDATION,
    *ISSUES_MARKETPLACE,
    *ISSUES_SESSIONS,
    *ISSUES_FLOW,
]

SIZE_LEGEND = {
    "S": "S (half a day or less)",
    "M": "M (1-2 days)",
    "L": "L (3 days or more)",
}

# The labels that exist on the repository. `gh issue create` fails on an unknown label, so
# keeping this list in sync is what stops a bulk create from dying halfway through.
KNOWN_LABELS = {
    "frontend",
    "backend",
    "api",
    "database",
    "auth",
    "escrow",
    "kyc-pro",
    "scheduling",
    "consultation",
    "admin",
    "compliance",
    "infra",
    "ci",
    "docs",
    "test",
    "good-first-issue",
}


def check() -> None:
    """Fail loudly on the mistakes that would otherwise reach GitHub."""
    ids = [str(i["id"]) for i in ALL_ISSUES]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise SystemExit(f"duplicate issue ids: {sorted(duplicates)}")

    known_prefixes = {w["prefix"] for w in WORKSTREAMS}
    known_milestones = {w["milestone"] for w in WORKSTREAMS}
    id_set = set(ids)

    for issue in ALL_ISSUES:
        iid = str(issue["id"])
        prefix = iid.rsplit("-", 1)[0]
        if prefix not in known_prefixes:
            raise SystemExit(f"{iid}: unknown workstream prefix {prefix!r}")
        if issue["milestone"] not in known_milestones:
            raise SystemExit(f"{iid}: unknown milestone {issue['milestone']!r}")
        if issue["size"] not in SIZE_LEGEND:
            raise SystemExit(f"{iid}: unknown size {issue['size']!r}")
        for field in ("goal", "branch", "title"):
            if not issue.get(field):
                raise SystemExit(f"{iid}: missing {field}")
        for field in ("requirements", "validation", "deliverables"):
            items = issue.get(field)
            if not isinstance(items, list) or not items:
                raise SystemExit(f"{iid}: {field} must be a non-empty list")
        for dep in issue["depends"]:  # type: ignore[union-attr]
            if dep not in id_set:
                raise SystemExit(f"{iid}: depends on unknown issue {dep!r}")
        if not re.match(r"^(feature|chore)/", str(issue["branch"])):
            raise SystemExit(f"{iid}: branch must start with feature/ or chore/")
        labels = issue["labels"]
        if not isinstance(labels, list) or not labels:
            raise SystemExit(f"{iid}: at least one label is required")
        unknown = set(labels) - KNOWN_LABELS
        if unknown:
            raise SystemExit(
                f"{iid}: labels do not exist on the repository: {sorted(unknown)}. "
                "Create them with `gh label create` and add them to KNOWN_LABELS."
            )

    # A dependency must not point at a later milestone: MVP work cannot wait on Beta.
    order = {"MVP": 0, "Beta": 1}
    by_id = {str(i["id"]): i for i in ALL_ISSUES}
    for issue in ALL_ISSUES:
        mine = order[str(issue["milestone"])]
        for dep in issue["depends"]:  # type: ignore[union-attr]
            theirs = order[str(by_id[dep]["milestone"])]
            if theirs > mine:
                raise SystemExit(
                    f"{issue['id']} ({issue['milestone']}) depends on "
                    f"{dep} ({by_id[dep]['milestone']}), which is later"
                )

    # A dependency cycle makes the backlog unstartable: every issue in the cycle waits on
    # another. It is easy to introduce by adding one link and impossible to spot by reading.
    graph = {str(i["id"]): list(i["depends"]) for i in ALL_ISSUES}  # type: ignore[arg-type]
    state: dict[str, int] = {}  # 0 = visiting, 1 = done

    def walk(node: str, path: list[str]) -> None:
        if state.get(node) == 1:
            return
        if state.get(node) == 0:
            cycle = path[path.index(node) :] + [node]
            raise SystemExit("dependency cycle: " + " -> ".join(cycle))
        state[node] = 0
        for dep in graph[node]:
            walk(dep, [*path, node])
        state[node] = 1

    for issue_id in graph:
        walk(issue_id, [])

    print(f"checked {len(ALL_ISSUES)} issues, no problems found")


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered(items: list[str]) -> str:
    return "\n".join(f"{n}. {item}" for n, item in enumerate(items, 1))


def body(issue: dict[str, object]) -> str:
    """The GitHub issue body. Requirements, validation and deliverables are the review bar."""
    depends = issue["depends"]
    depends_text = ", ".join(f"`{d}`" for d in depends) if depends else "nothing"  # type: ignore[union-attr]
    labels = ", ".join(f"`{label}`" for label in issue["labels"])  # type: ignore[union-attr]

    parts = [
        f"**Task id:** `{issue['id']}`",
        f"**Milestone:** {issue['milestone']}",
        f"**Size:** {SIZE_LEGEND[str(issue['size'])]}",
        f"**Depends on:** {depends_text}",
        f"**Branch:** `{issue['branch']}`",
        f"**Labels:** {labels}",
        "",
        "## Goal",
        "",
        str(issue["goal"]),
        "",
        "## Requirements",
        "",
        numbered(issue["requirements"]),  # type: ignore[arg-type]
        "",
        "## Validation / test checks",
        "",
        "Every item below must be satisfied, and the pull request must say how.",
        "",
        bullets(issue["validation"]),  # type: ignore[arg-type]
        "",
        "## Deliverables",
        "",
        bullets(issue["deliverables"]),  # type: ignore[arg-type]
    ]

    if issue.get("notes"):
        parts += ["", "## Notes", "", str(issue["notes"])]

    parts += [
        "",
        "---",
        "",
        "## Definition of done",
        "",
        "- [ ] Every requirement above is implemented.",
        "- [ ] Every validation check above passes, and the pull request states how.",
        "- [ ] Every deliverable above exists.",
        "- [ ] `pre-commit run --all-files` passes.",
        "- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.",
        "- [ ] Coverage stays above the CI gate.",
        "- [ ] Branch is `" + str(issue["branch"]) + "`, one pull request into `develop`.",
        "- [ ] The pull request body contains `Closes #<this issue>`.",
        "- [ ] No secrets, credentials, real personal data or real case material in the diff.",
        "- [ ] User-facing strings are French and come from the i18n catalogue.",
        "",
        "If a requirement turns out to be wrong or impossible, say so on this issue before "
        "implementing something different. Do not change the scope silently in the pull "
        "request.",
        "",
        "See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for "
        "how this issue fits the whole.",
    ]
    return "\n".join(parts) + "\n"


def backlog_doc() -> str:
    out: list[str] = [
        "# Lexpert — Issue Backlog",
        "",
        "> Companion to [lexpert_plan.md](lexpert_plan.md). Every issue is scoped to one pull",
        "> request and carries **Requirements**, **Validation / test checks** and",
        "> **Deliverables** — the three sections the pull request is reviewed against.",
        ">",
        "> **This file is generated.** Edit the data under `scripts/backlog/` and run",
        "> `python scripts/backlog/generate.py`. Do not edit this file by hand; the next",
        "> generation will overwrite it.",
        "",
        "**Sizes:** S = half a day or less, M = 1-2 days, L = 3 days or more.",
        "",
        "**Labels in use:** `frontend` `backend` `api` `database` `auth` `escrow` `kyc-pro` "
        "`scheduling` `consultation` `admin` `compliance` `infra` `ci` `docs` "
        "`good-first-issue`",
        "",
    ]

    mvp = [i for i in ALL_ISSUES if i["milestone"] == "MVP"]
    beta = [i for i in ALL_ISSUES if i["milestone"] == "Beta"]
    sizes = {s: sum(1 for i in ALL_ISSUES if i["size"] == s) for s in SIZE_LEGEND}

    out += [
        "## Summary",
        "",
        f"| Milestone | Issues | S | M | L |",
        "| --- | --- | --- | --- | --- |",
        f"| MVP | {len(mvp)} | "
        f"{sum(1 for i in mvp if i['size'] == 'S')} | "
        f"{sum(1 for i in mvp if i['size'] == 'M')} | "
        f"{sum(1 for i in mvp if i['size'] == 'L')} |",
        f"| Beta | {len(beta)} | "
        f"{sum(1 for i in beta if i['size'] == 'S')} | "
        f"{sum(1 for i in beta if i['size'] == 'M')} | "
        f"{sum(1 for i in beta if i['size'] == 'L')} |",
        f"| **Total** | **{len(ALL_ISSUES)}** | **{sizes['S']}** | **{sizes['M']}** | "
        f"**{sizes['L']}** |",
        "",
        "### Workstreams",
        "",
        "| Prefix | Workstream | Milestone | Issues |",
        "| --- | --- | --- | --- |",
    ]
    for ws in WORKSTREAMS:
        count = sum(
            1 for i in ALL_ISSUES if str(i["id"]).rsplit("-", 1)[0] == ws["prefix"]
        )
        out.append(
            f"| `{ws['prefix']}` | {ws['title']} | {ws['milestone']} | {count} |"
        )
    out.append("")

    out += [
        "### Suggested order",
        "",
        "The critical path to a demonstrable product is",
        "`FND` -> `AUT` -> `KYC` -> `PRO` -> `SCH` -> `ESC` -> `CON`. `DSP`, `NOT` and `CMP`",
        "decorate a flow that must exist first. `ESC-01`, `ESC-02` and `ESC-05` have no",
        "scheduling dependency and can be picked up early in parallel.",
        "",
        "Good first issues: "
        + ", ".join(
            f"`{i['id']}`" for i in ALL_ISSUES if "good-first-issue" in i["labels"]  # type: ignore[operator]
        )
        + ".",
        "",
        "---",
        "",
    ]

    for ws in WORKSTREAMS:
        issues = [
            i for i in ALL_ISSUES if str(i["id"]).rsplit("-", 1)[0] == ws["prefix"]
        ]
        if not issues:
            continue
        out += [
            f"## {ws['prefix']} — {ws['title']}",
            "",
            f"*Milestone: {ws['milestone']}.* {ws['summary']}",
            "",
        ]
        for issue in issues:
            depends = issue["depends"]
            depends_text = ", ".join(f"`{d}`" for d in depends) if depends else "—"  # type: ignore[union-attr]
            labels = " ".join(f"`{label}`" for label in issue["labels"])  # type: ignore[union-attr]
            out += [
                f"### {issue['id']} — {issue['title']}",
                "",
                f"- **Labels:** {labels} - **Size:** {issue['size']} - "
                f"**Depends on:** {depends_text} - **Branch:** `{issue['branch']}`",
                f"- **Goal:** {issue['goal']}",
                f"- **Requirements:** {len(issue['requirements'])} items - "  # type: ignore[arg-type]
                f"**Validation checks:** {len(issue['validation'])} items - "  # type: ignore[arg-type]
                f"**Deliverables:** {len(issue['deliverables'])} items"  # type: ignore[arg-type]
                f" - full text in [`.github/issue-bodies/{str(issue['id']).lower()}.md`]"
                f"(../../.github/issue-bodies/{str(issue['id']).lower()}.md)",
                "",
            ]

    out += [
        "---",
        "",
        "## Appendix — bulk create",
        "",
        "The generated script `scripts/create_issues.sh` creates every issue above with its",
        "labels, its milestone and its body file. It is idempotent by title: an issue whose",
        "title already exists is skipped, so it is safe to re-run after adding entries.",
        "",
        "```bash",
        "bash scripts/create_issues.sh          # create anything missing",
        "bash scripts/create_issues.sh --dry-run",
        "```",
        "",
        "Regenerate everything after editing the data:",
        "",
        "```bash",
        "python scripts/backlog/generate.py",
        "```",
        "",
    ]
    return "\n".join(out)


def create_script() -> str:
    lines = [
        "#!/usr/bin/env bash",
        "# Bulk-create the Lexpert backlog as GitHub issues.",
        "#",
        "# GENERATED by scripts/backlog/generate.py - do not edit by hand.",
        "#",
        "# Idempotent by issue title: an existing title is skipped, so re-running after adding",
        "# backlog entries creates only what is missing.",
        "#",
        "#   bash scripts/create_issues.sh",
        "#   bash scripts/create_issues.sh --dry-run",
        "set -euo pipefail",
        "",
        'DRY_RUN="${1:-}"',
        'cd "$(dirname "$0")/.."',
        "",
        "if ! gh auth status >/dev/null 2>&1; then",
        '  echo "gh is not authenticated. Run: gh auth login" >&2',
        "  exit 1",
        "fi",
        "",
        "echo \"Reading existing issue titles...\"",
        'EXISTING="$(gh issue list --state all --limit 400 --json title -q ".[].title")"',
        "",
        "created=0",
        "skipped=0",
        "",
        "create() {",
        '  local id="$1" title="$2" milestone="$3"; shift 3',
        '  local full="$id $title"',
        '  if grep -Fxq "$full" <<< "$EXISTING"; then',
        '    echo "skip    $full"',
        "    skipped=$((skipped + 1))",
        "    return 0",
        "  fi",
        '  if [[ "$DRY_RUN" == "--dry-run" ]]; then',
        '    echo "would   $full"',
        "    return 0",
        "  fi",
        "  local label_args=()",
        '  for label in "$@"; do label_args+=(--label "$label"); done',
        '  gh issue create --title "$full" --milestone "$milestone" \\',
        '    --body-file ".github/issue-bodies/$(echo "$id" | tr "[:upper:]" "[:lower:]").md" \\',
        '    "${label_args[@]}"',
        "  created=$((created + 1))",
        "}",
        "",
    ]

    current_prefix = ""
    for issue in ALL_ISSUES:
        prefix = str(issue["id"]).rsplit("-", 1)[0]
        if prefix != current_prefix:
            ws = next(w for w in WORKSTREAMS if w["prefix"] == prefix)
            lines += ["", f"# --- {prefix}: {ws['title']} ---"]
            current_prefix = prefix
        labels = " ".join(f'"{label}"' for label in issue["labels"])  # type: ignore[union-attr]
        title = str(issue["title"]).replace('"', '\\"')
        lines.append(
            f'create "{issue["id"]}" "{title}" "{issue["milestone"]}" {labels}'
        )

    lines += [
        "",
        'echo ""',
        'echo "created: $created   skipped: $skipped"',
        'if [[ "$DRY_RUN" != "--dry-run" ]]; then',
        '  echo ""',
        '  echo "Current backlog:"',
        "  gh issue list --limit 400 --json number,title,milestone \\",
        "    -q '.[] | \"\\(.number)\\t\\(.milestone.title // \"-\")\\t\\(.title)\"'",
        "fi",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    check()

    bodies_dir = ROOT / ".github" / "issue-bodies"
    bodies_dir.mkdir(parents=True, exist_ok=True)
    for stale in bodies_dir.glob("*.md"):
        stale.unlink()
    for issue in ALL_ISSUES:
        path = bodies_dir / f"{str(issue['id']).lower()}.md"
        path.write_text(body(issue), encoding="utf-8", newline="\n")
    print(f"wrote {len(ALL_ISSUES)} issue bodies to {bodies_dir.relative_to(ROOT)}")

    doc = ROOT / "docs" / "implementation" / "lexpert_issues.md"
    doc.write_text(backlog_doc(), encoding="utf-8", newline="\n")
    print(f"wrote {doc.relative_to(ROOT)}")

    script = ROOT / "scripts" / "create_issues.sh"
    script.write_text(create_script(), encoding="utf-8", newline="\n")
    print(f"wrote {script.relative_to(ROOT)}")

    # The roadmap is derived from the same data. build_roadmap() also validates that every
    # MVP workstream is planned into exactly one phase, so a new workstream cannot quietly
    # go unscheduled.
    roadmap_path = ROOT / "docs" / "implementation" / "roadmap.md"
    roadmap_path.write_text(
        render_roadmap(build_roadmap(ALL_ISSUES)), encoding="utf-8", newline="\n"
    )
    print(f"wrote {roadmap_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
