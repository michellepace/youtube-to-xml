# 0001. Ban code comments; record decisions as ADRs

**Status:** Accepted, 2026-11-20

## Context

An audit of the 234 prose comments in `src/` and `tests/` found that almost all of them restated the code. The rest had gone stale (they named functions that had been renamed or removed) or excused a workaround ("shouldn't happen", "during development"). A few recorded real decisions, but they were scattered and easy to miss. Excuse comments were the most harmful: two of them hid bugs where text was silently dropped or tracebacks leaked to users.

## Decision

- Python files contain no prose comments. Code says *what* through its names, and tests say *how it behaves*.
- Important, non-obvious decisions (*why*) go in an ADR in `docs/adr/`.
- A workaround gets a GitHub issue, not a comment that apologises for it.
- Tool pragmas are not comments and stay allowed: `noqa`, `type: ignore`, `pyright:`, `fmt:` and `pragma: no cover`. The pragma alone is allowed; prose after it is not.
- Docstrings are documentation, not comments, and are still required by Ruff's `D` rules.

`scripts/check_comments.py` enforces this as a ratchet in pre-commit. `.comment-baseline.json` records how many legacy comments each file may still have. A new comment fails the check. A removed comment tightens the baseline automatically, and the commit must include the updated baseline, so the allowance only ever goes down. Raising an allowance means editing the baseline by hand, which shows up in review.

The `/delete-comment` skill repeats the audit: it categorises each comment, deletes it, files an issue or writes an ADR as needed, and lets the ratchet tighten.

## Consequences

- Fewer stale explanations. Intent has to live in names, tests and ADRs, all of which are checked or reviewed.
- Some short "why" notes cost more to write as an ADR than as a comment. That friction is intended.
- Comments in config files (`pyproject.toml`, YAML) are outside this rule.
