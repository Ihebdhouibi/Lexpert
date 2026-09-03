"""Tests for the project's own pre-commit hooks.

A hook nobody tests is a hook that silently stops catching things -- a tightened regex, a
refactor, a Python upgrade, and the check still exits 0 on input it used to reject. Nobody
notices, because a passing hook looks exactly like a working one.

These tests exercise both directions for every custom check: input that must be rejected,
and input that must be accepted. Run them directly, and in CI:

    python scripts/hooks/test_hooks.py
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, HOOKS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


commit_msg = load("check_commit_message")
staged = load("check_staged_content")

failures: list[str] = []


def expect(condition: bool, description: str) -> None:
    if condition:
        print(f"  ok    {description}")
    else:
        failures.append(description)
        print(f"  FAIL  {description}")


# --------------------------------------------------------------------- commit messages

REJECTED_MESSAGES = {
    "AI attribution trailer": "feat(api): add user model\n\nCo-authored-by: Claude <x@y.z>",
    "generated-with line": "feat(api): add user model\n\nGenerated with Claude Code",
    "robot emoji": "feat(api): add user model\n\n\U0001f916 automated",
    "emoji in subject": "feat(api): add sparkle ✨",
    "subject over 72 chars": "feat(api): " + "x" * 70,
    "subject ending in a full stop": "feat(api): add the user model.",
    "type with no description": "feat(api): ",
    "empty message": "\n\n# a comment git added\n",
}

ACCEPTED_MESSAGES = {
    "plain conventional commit": "feat(api): add the user model",
    "with a body": "fix(web): correct the slot timezone\n\nThe client zone was ignored.",
    "human co-author is fine": (
        "feat(api): add ledger\n\nCo-authored-by: Oumaima Abdessamed <o@example.tn>"
    ),
    "comments are ignored": "chore: tidy\n\n# Co-authored-by: Claude\n",
    "a merge commit is not policed": "Merge branch 'develop' into feature/x",
    "an arrow is not an emoji": "docs: describe the BOOKED -> FUNDS_HELD transition",
    "accented French is fine": "docs: ajouter la politique d'annulation",
}

print("commit message rules")
for description, message in REJECTED_MESSAGES.items():
    expect(bool(commit_msg.check(message)), f"rejects: {description}")
for description, message in ACCEPTED_MESSAGES.items():
    problems = commit_msg.check(message)
    expect(not problems, f"accepts: {description}" + (f" -- got {problems}" if problems else ""))


# --------------------------------------------------------------------- staged content


def check_content(relative: str, content: str) -> list[str]:
    """Write `content` to a temporary file but check it under the path `relative`.

    The checks are path-sensitive (a money module, the API source tree, an exempt document),
    so the path under test has to be the logical one, not the temporary one.
    """
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / Path(relative).name
        path.write_text(content, encoding="utf-8")
        return staged.check_file(relative, path)


print("\nrepository rules in staged content")

REJECTED_CONTENT = {
    "emoji in a source file": ("apps/web/src/App.tsx", "export const ok = '✅';\n"),
    "AI attribution in a source file": (
        "apps/api/src/lexpert_api/x.py",
        "# Generated with Claude\n",
    ),
    # The marker is assembled at runtime so the `detect-private-key` hook does not fire on
    # this file. Keeping that hook at full strength is worth more than a readable literal.
    "a private key": (
        "apps/api/src/lexpert_api/x.py",
        "KEY = " + "-----BEGIN RSA PRIVATE" + " KEY-----\nabc\n",
    ),
    # These two are assembled at runtime rather than written as literals. GitHub's push
    # protection scans the diff and rejects the push on a key-shaped string, even one that
    # exists only to be rejected by our own hook -- so a readable literal here makes the
    # branch unpushable. Splitting the prefix is the whole trick.
    "a real-looking secret assignment": (
        "apps/api/src/lexpert_api/x.py",
        'API_KEY = "' + "sk_" + "live_" + "51H8xQ2eZvKYlo2C1234567890" + '"\n',
    ),
    "an AWS access key id": (
        "scripts/deploy.py",
        "key = '" + "AKIA" + "IOSFODNN7EXAMPLE" + "'\n",
    ),
    "a committed .env": (".env", "LEXPERT_JWT_SECRET=hunter2hunter2\n"),
    "float in a money module": (
        "apps/api/src/lexpert_api/escrow/pricing.py",
        "def total(rate: float) -> float:\n    return rate\n",
    ),
    "naive datetime in the API": (
        "apps/api/src/lexpert_api/booking/service.py",
        "import datetime\nnow = datetime.datetime.utcnow()\n",
    ),
    "print in API source": (
        "apps/api/src/lexpert_api/core/x.py",
        "def f() -> None:\n    print('debug')\n",
    ),
}

ACCEPTED_CONTENT = {
    "ordinary source": ("apps/web/src/App.tsx", "export const Total = () => null;\n"),
    "French copy with accents": (
        "apps/web/src/i18n/fr.ts",
        "export const fr = { total: 'Montant total a payer' };\n",
    ),
    "a placeholder in .env.example": (".env.example", "LEXPERT_JWT_SECRET=change-me\n"),
    "a documented exception": (
        "apps/api/src/lexpert_api/escrow/report.py",
        "ratio = float(x)  # lexpert: allow\n",
    ),
    "float outside a money module": (
        "apps/api/src/lexpert_api/profiles/geo.py",
        "def distance(a: float) -> float:\n    return a\n",
    ),
    "timezone-aware datetime": (
        "apps/api/src/lexpert_api/booking/service.py",
        "from datetime import UTC, datetime\nnow = datetime.now(UTC)\n",
    ),
    "print in a script, not API source": ("scripts/x.py", "print('fine here')\n"),
    "a document that quotes the rules": (
        "CLAUDE.md",
        "Never write 'Generated with Claude' in a commit message.\n",
    ),
    "arrows in a state diagram": (
        "docs/technical_docs/escrow_lifecycle.md",
        "BOOKED -> FUNDS_HELD -> IN_SESSION\n",
    ),
}

for description, (relative, content) in REJECTED_CONTENT.items():
    expect(bool(check_content(relative, content)), f"rejects: {description}")
for description, (relative, content) in ACCEPTED_CONTENT.items():
    problems = check_content(relative, content)
    expect(not problems, f"accepts: {description}" + (f" -- got {problems}" if problems else ""))


# --------------------------------------------------------------------- summary

print()
if failures:
    print(f"{len(failures)} hook test(s) failed:")
    for description in failures:
        print(f"  - {description}")
    sys.exit(1)

total = (
    len(REJECTED_MESSAGES)
    + len(ACCEPTED_MESSAGES)
    + len(REJECTED_CONTENT)
    + len(ACCEPTED_CONTENT)
)
print(f"all {total} hook tests passed")
