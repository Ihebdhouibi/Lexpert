"""Reject staged file content that breaks repository rules or project conventions.

Three groups of check, each mapping to a rule the project has already committed to:

1. **No AI attribution, no emojis** (`CLAUDE.md` rules 1 and 2) in any staged file.
2. **Public-repository hygiene** -- an `.env` file, a credential-shaped assignment, or a
   private key must never be staged.
3. **Domain conventions from the implementation plan** -- money is integer millimes so
   `float` has no place in the money modules; timestamps are timezone-aware so a naive
   `datetime.now()` is a bug; and `print()` is not logging.

Group 3 only applies to files that exist, so it is inert until `apps/api` is created and
then starts guarding automatically.

pre-commit passes the staged filenames as arguments.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

# --------------------------------------------------------------------------- rule 1 and 2

ATTRIBUTION_PATTERNS = [
    re.compile(r"generated\s+(?:with|by)\s+claude", re.IGNORECASE),
    re.compile(r"co-authored-by:\s*(claude|copilot|cursor|devin|aider)", re.IGNORECASE),
    re.compile(r"written\s+by\s+claude", re.IGNORECASE),
    re.compile(r"\bclaude\s+code\b", re.IGNORECASE),
    re.compile(r"generated\s+with\s+\[?claude", re.IGNORECASE),
]

# Files exempt from the attribution and emoji rules, for two distinct reasons.
#
# The governance documents and this hook pair have to *quote* the forbidden phrases in order
# to state and enforce the rules -- a checker that cannot describe what it forbids is not
# much of a checker. Exempting them is the alternative to writing the patterns obfuscated,
# which would make them unreviewable.
#
# The feasibility study was authored elsewhere and is kept verbatim as the project's source
# document; rewriting it to satisfy a lint rule would lose more than it gains.
#
# Every other file in the repository is held to both rules. Keep this list short, and add to
# it only for a file whose job is to talk about the rules.
RULE_EXEMPT = {
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "docs/team_workflow_playbook.md",
    "docs/Phase1-Feasibility-Business-Architecture.md",
    "scripts/hooks/check_commit_message.py",
    "scripts/hooks/check_staged_content.py",
    "scripts/hooks/test_hooks.py",  # holds the inputs these checks must reject
}

# Text extensions worth scanning. A binary file is skipped by the decode guard anyway, but
# an explicit list keeps the hook fast and predictable.
TEXT_SUFFIXES = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yml", ".yaml", ".toml", ".md",
    ".css", ".scss", ".html", ".sh", ".sql", ".txt", ".cfg", ".ini", ".env",
}

# --------------------------------------------------------------------------- secrets

SECRET_PATTERNS = [
    (
        re.compile(
            r"""(?ix)
            \b(api[_-]?key|secret|password|passwd|token|private[_-]?key|client[_-]?secret)
            \b\s*[:=]\s*
            ['"](?P<value>[^'"\s]{12,})['"]
            """
        ),
        "a credential-shaped assignment with a literal value",
    ),
    (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
        "a private key block",
    ),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key id"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "a GitHub token"),
    (re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b"), "a Stripe secret key"),
]

# Placeholder values that are obviously not real secrets.
SECRET_ALLOWED_VALUES = re.compile(
    r"(?ix)^(change[-_]?me|placeholder|example|your[-_].*|x{4,}|\.{3,}|"
    r"<[^>]+>|\$\{[^}]+\}|test[-_]?(secret|token|key|password)|"
    r"dummy|fake|redacted|none|null|todo)"
)

# Files where a credential-shaped line is expected and safe.
SECRET_EXEMPT_SUFFIXES = (".example", ".md")
SECRET_EXEMPT_PATHS = {
    ".env.example",
    "scripts/hooks/check_staged_content.py",
    "scripts/hooks/test_hooks.py",  # holds the fixtures these patterns must reject
}

# --------------------------------------------------------------------------- conventions

MONEY_MODULE_HINTS = ("escrow", "booking", "pricing", "ledger")

FLOAT_PATTERN = re.compile(r"(?<![\w.])float\s*[(\[:]|:\s*float\b|->\s*float\b")
NAIVE_DATETIME_PATTERN = re.compile(
    r"datetime\.(?:datetime\.)?(?:utcnow\s*\(\s*\)|now\s*\(\s*\))"
)
PRINT_PATTERN = re.compile(r"^\s*print\s*\(", re.MULTILINE)

# A line ending in this marker opts out of a convention check, for the rare real exception.
ALLOW_MARKER = "lexpert: allow"


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith(".env")


def read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def emoji_in(text: str) -> tuple[int, str] | None:
    for index, char in enumerate(text):
        code = ord(char)
        if code < 0x2100:
            continue
        if unicodedata.category(char) not in {"So", "Cs", "Co"}:
            continue
        if char in "™®©†‡‰":
            continue
        if 0x2190 <= code <= 0x22FF:  # arrows and maths operators
            continue
        return index, char
    return None


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_file(rel: str, path: Path) -> list[str]:
    problems: list[str] = []

    if rel == ".env" or rel.endswith("/.env"):
        return [
            f"{rel}: a .env file must never be committed -- it is git-ignored for a reason. "
            "Ship .env.example instead."
        ]

    if not is_text(path):
        return problems
    text = read(path)
    if text is None:
        return problems

    lines = text.splitlines()

    # --- rule 1: AI attribution
    for pattern in [] if rel in RULE_EXEMPT else ATTRIBUTION_PATTERNS:
        match = pattern.search(text)
        if match:
            problems.append(
                f"{rel}:{line_of(text, match.start())}: AI attribution "
                f"({match.group(0)!r}). CLAUDE.md rule 1 forbids it."
            )
            break

    # --- rule 2: emojis
    if rel not in RULE_EXEMPT:
        hit = emoji_in(text)
        if hit is not None:
            index, char = hit
            name = unicodedata.name(char, "unnamed")
            problems.append(
                f"{rel}:{line_of(text, index)}: emoji {char!r} ({name}). "
                "CLAUDE.md rule 2 forbids emojis anywhere."
            )

    # --- secrets
    if rel not in SECRET_EXEMPT_PATHS and not rel.endswith(SECRET_EXEMPT_SUFFIXES):
        for pattern, description in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                value = match.groupdict().get("value") or ""
                if value and SECRET_ALLOWED_VALUES.match(value):
                    continue
                number = line_of(text, match.start())
                if ALLOW_MARKER in lines[number - 1]:
                    continue
                problems.append(
                    f"{rel}:{number}: {description}. This repository is public. Move it to "
                    f"an environment variable, or append '# {ALLOW_MARKER}' if it is "
                    "genuinely not a secret."
                )
                break

    # --- domain conventions, API source only
    if rel.startswith("apps/api/src/") and path.suffix == ".py":
        if any(hint in rel for hint in MONEY_MODULE_HINTS):
            for match in FLOAT_PATTERN.finditer(text):
                number = line_of(text, match.start())
                if ALLOW_MARKER in lines[number - 1]:
                    continue
                problems.append(
                    f"{rel}:{number}: `float` in a money module. Money is integer millimes "
                    "throughout (see docs/implementation/lexpert_plan.md); floats do not do "
                    "money."
                )
                break

        for match in NAIVE_DATETIME_PATTERN.finditer(text):
            number = line_of(text, match.start())
            if ALLOW_MARKER in lines[number - 1]:
                continue
            problems.append(
                f"{rel}:{number}: naive `{match.group(0)}`. Use the injectable clock from "
                "`lexpert_api.core.clock` and timezone-aware instants (see "
                "docs/technical_docs/time_and_timezones.md)."
            )
            break

        for match in PRINT_PATTERN.finditer(text):
            number = line_of(text, match.start())
            if ALLOW_MARKER in lines[number - 1]:
                continue
            problems.append(
                f"{rel}:{number}: `print()` in API source. Use the configured logger -- and "
                "remember request and response bodies are never logged."
            )
            break

    return problems


def main(argv: list[str]) -> int:
    problems: list[str] = []
    for name in argv:
        path = Path(name)
        if not path.is_file():
            continue
        problems.extend(check_file(name.replace("\\", "/"), path))

    if not problems:
        return 0

    print("Staged content rejected:\n", file=sys.stderr)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    print("\nSee CLAUDE.md for the rules and CONTRIBUTING.md for the workflow.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
