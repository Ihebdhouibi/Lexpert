"""Push backlog changes to the GitHub issues that already exist.

`scripts/create_issues.sh` is idempotent by *title*, which means a backlog issue whose title
changes gets created a second time rather than updated -- leaving two open issues for one
task id, and the older one silently stale.

This script matches on the **task id** instead, which never changes, and updates the title,
body, labels and milestone of the issue that already carries it. Run it after every
`python scripts/backlog/generate.py` that changed an existing entry:

    python scripts/sync_issues.py --dry-run
    python scripts/sync_issues.py

It never creates and never closes anything: an id with no issue is reported so that
`create_issues.sh` can make it, and an id with two issues is reported as a duplicate for a
human to resolve. Deciding to close someone's issue is not a script's call.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "backlog"))

from generate import ALL_ISSUES, body  # noqa: E402


# Transient network failures against the GitHub API are common enough that a sync of sixty
# issues will hit one. Retrying is safe: every call this script makes is idempotent.
TRANSIENT = ("dial tcp", "connection reset", "timeout", "TLS handshake", "502", "503")


def gh(*args: str, attempts: int = 4) -> str:
    last = ""
    for attempt in range(1, attempts + 1):
        result = subprocess.run(
            ["gh", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout
        last = result.stderr or result.stdout
        if not any(marker in last for marker in TRANSIENT) or attempt == attempts:
            break
        delay = 2**attempt
        print(f"  transient failure, retrying in {delay}s ({attempt}/{attempts - 1})")
        time.sleep(delay)
    raise SystemExit(f"gh {' '.join(args)} failed:\n{last}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", help="sync a single task id, for example ESC-08")
    args = parser.parse_args()

    raw = gh(
        "issue",
        "list",
        "--state",
        "all",
        "--limit",
        "400",
        "--json",
        "number,title,body,labels,milestone,state",
    )
    live = json.loads(raw)

    # Only open issues participate in matching, for two reasons: a closed duplicate is a
    # resolved duplicate, and a closed issue is finished work that must not be edited or
    # reported as missing -- doing so would invite someone to re-create completed work.
    by_id: dict[str, list[dict]] = {}
    closed_ids: dict[str, int] = {}
    for issue in live:
        task_id = issue["title"].split(" ", 1)[0]
        if issue.get("state") == "OPEN":
            by_id.setdefault(task_id, []).append(issue)
        else:
            closed_ids.setdefault(task_id, issue["number"])

    # The roadmap links to issue numbers and marks finished work, neither of which is in the
    # backlog data. Persist both so `generate.py` needs no network and the pre-commit
    # staleness hook stays deterministic. Closed issues are included -- a completed issue is
    # still worth linking to, and a roadmap that shows finished work as pending is worse than
    # no roadmap.
    numbers: dict[str, dict[str, object]] = {
        task_id: {"number": entries[0]["number"], "open": True}
        for task_id, entries in by_id.items()
        if len(entries) == 1
    }
    for task_id, number in closed_ids.items():
        numbers.setdefault(task_id, {"number": number, "open": False})
    numbers = dict(sorted(numbers.items()))
    numbers_path = ROOT / "scripts" / "backlog" / "issue_numbers.json"
    numbers_path.write_text(
        json.dumps(numbers, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {numbers_path.relative_to(ROOT)} ({len(numbers)} issues)")
    print("run `python scripts/backlog/generate.py` if any number changed\n")

    missing: list[str] = []
    done: list[str] = []
    duplicates: list[str] = []
    stale: list[str] = []
    updated = 0
    unchanged = 0

    for entry in ALL_ISSUES:
        task_id = str(entry["id"])
        if args.only and task_id != args.only:
            continue

        matches = by_id.get(task_id, [])
        if not matches:
            # A closed issue is finished work: never edit it, never report it as missing.
            # Reporting it would invite someone to re-create work already done.
            if task_id in closed_ids:
                done.append(task_id)
            else:
                missing.append(task_id)
            continue
        if len(matches) > 1:
            # Not `numbers` -- that name holds the id-to-number map written above.
            found = ", ".join(f"#{m['number']}" for m in matches)
            duplicates.append(f"{task_id}: {found}")
            continue

        issue = matches[0]
        number = str(issue["number"])
        want_title = f"{task_id} {entry['title']}"
        want_body = body(entry)
        want_labels = sorted(entry["labels"])  # type: ignore[arg-type]
        have_labels = sorted(label["name"] for label in issue["labels"])
        have_milestone = (issue["milestone"] or {}).get("title")

        changes: list[str] = []
        command = ["issue", "edit", number]

        if issue["title"] != want_title:
            changes.append("title")
            command += ["--title", want_title]

        # GitHub normalises line endings on stored bodies, so compare normalised.
        if (issue["body"] or "").replace("\r\n", "\n").strip() != want_body.strip():
            changes.append("body")

        if have_labels != want_labels:
            changes.append(f"labels ({have_labels} -> {want_labels})")
            for label in want_labels:
                command += ["--add-label", label]
            for label in set(have_labels) - set(want_labels):
                command += ["--remove-label", label]

        if have_milestone != entry["milestone"]:
            changes.append(f"milestone ({have_milestone} -> {entry['milestone']})")
            command += ["--milestone", str(entry["milestone"])]

        if not changes:
            unchanged += 1
            continue

        print(f"{'would update' if args.dry_run else 'updating'} #{number} {task_id}: "
              f"{', '.join(changes)}")
        stale.append(task_id)
        if args.dry_run:
            continue

        if "body" in changes:
            path = ROOT / ".github" / "issue-bodies" / f"{task_id.lower()}.md"
            command += ["--body-file", str(path)]
        gh(*command)
        updated += 1

    print()
    verb = "out of date" if args.dry_run else "updated"
    print(f"in sync: {unchanged}   {verb}: {len(stale) if args.dry_run else updated}")

    if done:
        print(f"closed, left alone: {', '.join(sorted(done))}")

    if missing:
        print(f"\nno issue exists yet for: {', '.join(missing)}")
        print("run: bash scripts/create_issues.sh")

    if duplicates:
        print("\nDUPLICATE task ids -- two issues share one id, resolve by hand:")
        for line in duplicates:
            print(f"  {line}")
        print("Keep one, close the other, then re-run this script.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
