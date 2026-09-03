"""Fail if the branch ruleset's required status checks do not match the CI job names.

The ruleset matches required status checks against CI job names as literal strings. Renaming a
job in the workflow without updating `.github/ruleset.json` in the same change silently blocks
every merge on a check that will never report -- with no error anywhere, just pull requests stuck
in "Expected" forever.

This script turns that into a CI failure. Run it from the repository root:

    python scripts/check_ruleset_contexts.py

It also validates that every JSON and YAML config in the repository parses, so a malformed
ruleset payload is caught before someone tries to apply it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

RULESET = ROOT / ".github" / "ruleset.json"

# `workflows/` is the live location. `workflows-staged/` was where the workflow was parked
# before the owner's token had the `workflow` scope; the fallback is kept so the script still
# works on an older branch or a revert, and costs nothing.
CI_CANDIDATES = [
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "workflows-staged" / "ci.yml",
]

JSON_FILES = [
    ROOT / ".github" / "ruleset.json",
    ROOT / ".claude" / "settings.json",
]

YAML_FILES = [
    ROOT / ".pre-commit-config.yaml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
]


def fail(message: str) -> None:
    print(f"FAIL {message}")
    sys.exit(1)


def main() -> None:
    ci_path = next((p for p in CI_CANDIDATES if p.exists()), None)
    if ci_path is None:
        fail("no ci.yml found in .github/workflows/ or .github/workflows-staged/")
    assert ci_path is not None

    for path in [*JSON_FILES, *YAML_FILES, ci_path]:
        if not path.exists():
            continue
        loader = json.load if path.suffix == ".json" else yaml.safe_load
        try:
            with path.open(encoding="utf-8") as handle:
                loader(handle)  # type: ignore[operator]
        except Exception as exc:  # noqa: BLE001 - any parse failure is a failure
            fail(f"{path.relative_to(ROOT)} does not parse: {exc}")
        print(f"ok   {path.relative_to(ROOT)} parses")

    with RULESET.open(encoding="utf-8") as handle:
        ruleset = json.load(handle)
    with ci_path.open(encoding="utf-8") as handle:
        workflow = yaml.safe_load(handle)

    required = {
        check["context"]
        for rule in ruleset["rules"]
        if rule["type"] == "required_status_checks"
        for check in rule["parameters"]["required_status_checks"]
    }
    if not required:
        fail(f"{RULESET.relative_to(ROOT)} declares no required status checks")

    jobs = set(workflow.get("jobs", {}))

    missing_jobs = required - jobs
    if missing_jobs:
        fail(
            f"the ruleset requires {sorted(missing_jobs)}, which are not job names in "
            f"{ci_path.relative_to(ROOT)}. Every pull request would block forever on a check "
            "that never reports. Fix the ruleset or the job names so they match."
        )

    unrequired_jobs = jobs - required
    if unrequired_jobs:
        fail(
            f"{ci_path.relative_to(ROOT)} defines {sorted(unrequired_jobs)}, which the ruleset "
            "does not require. A job whose failure cannot block a merge is decoration. Add it to "
            f"{RULESET.relative_to(ROOT)} or remove it."
        )

    # A skipped job never reports, which blocks a strict required check permanently.
    if "paths" in workflow.get("on", {}).get("pull_request", {}):
        fail(
            f"{ci_path.relative_to(ROOT)} has a `paths:` filter on `pull_request`. A skipped job "
            "never reports its status, so every pull request would block forever."
        )

    print(f"\nok   ruleset required checks match CI job names exactly: {sorted(required)}")


if __name__ == "__main__":
    main()
