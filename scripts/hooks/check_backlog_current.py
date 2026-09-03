"""Fail if the generated backlog artifacts do not match their source data.

`docs/implementation/lexpert_issues.md`, `.github/issue-bodies/*.md` and
`scripts/create_issues.sh` are all generated from the data under `scripts/backlog/`. Editing
one of them by hand looks like it works and is then silently discarded by the next
generation -- and if that edit had already been pushed to a GitHub issue body, the issue and
the repository disagree with no sign of it.

This regenerates into a temporary directory and compares, so a stale artifact or a
hand-edited one is caught at commit time.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GENERATED = [
    Path("docs/implementation/lexpert_issues.md"),
    Path("scripts/create_issues.sh"),
]
GENERATED_DIR = Path(".github/issue-bodies")


def snapshot() -> dict[Path, str]:
    state: dict[Path, str] = {}
    for rel in GENERATED:
        path = ROOT / rel
        state[rel] = path.read_text(encoding="utf-8") if path.exists() else ""
    body_dir = ROOT / GENERATED_DIR
    if body_dir.is_dir():
        for path in sorted(body_dir.glob("*.md")):
            state[path.relative_to(ROOT)] = path.read_text(encoding="utf-8")
    return state


def main() -> int:
    before = snapshot()

    result = subprocess.run(
        [sys.executable, "scripts/backlog/generate.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("The backlog generator failed:\n", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return 1

    after = snapshot()

    changed = sorted(
        {str(k).replace("\\", "/") for k in set(before) | set(after) if before.get(k) != after.get(k)}
    )
    if not changed:
        return 0

    print("The generated backlog artifacts were out of date:\n", file=sys.stderr)
    for name in changed:
        print(f"  - {name}", file=sys.stderr)
    print(
        "\nThey have just been regenerated, so `git add` them and commit again.\n"
        "Do not edit them by hand -- edit the data under scripts/backlog/ instead.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
