---
name: delete-comment
description: Audit the Python code comments in this repository (or a given path), categorise each one as Tautology, Stale, Excuse or Decision Record, then delete it, file an issue, or move it into an ADR, and let the no-comments ratchet tighten. Use when asked to clean up, audit or remove code comments, or when the comment ratchet baseline still lists files.
argument-hint: "[path ...] (default: src tests scripts)"
---

# Delete comments

Code comments are banned in this repository ([ADR 0001](../../../docs/adr/0001-ban-code-comments.md)). `scripts/check_comments.py` enforces the ban as a ratchet: `.comment-baseline.json` lists how many legacy comments each file may still have. This skill removes those comments without losing anything worth keeping.

Scope: `$ARGUMENTS`. If it is empty, use `src tests scripts`.

## 1. Inventory

```bash
uv run python scripts/check_comments.py --list $ARGUMENTS
```

This lists every prose comment as `path:line: text`. Tool pragmas (`noqa`, `type: ignore`, `pyright:`, `fmt:`, `pragma: no cover`) are not comments and are not listed. Leave them alone. If the list is empty, report that and stop.

## 2. Read, then categorise every comment

Read each file in full before judging its comments, because a comment can only be judged against the code around it. Give every comment exactly one category:

| Category | Test | Action |
|---|---|---|
| **Tautology** | Repeats what the code, a name or a docstring already says. Section banners in test files belong here too. | Delete |
| **Stale** | Refers to something that no longer exists or is no longer true: a renamed function, a removed fixture, a "new" API with no old one, behaviour the code no longer has. Check names with `grep` before deciding. | Delete |
| **Excuse** | Lets a workaround stand: "shouldn't happen", "for now", "hack", "temporary", "during development", "TODO", a justification next to `type: ignore` or `noqa`, or a defensive branch nobody has tested. | Delete **and** file an issue |
| **Decision Record** | Explains an important *why* that the code cannot show, so that without it a maintainer would likely make a wrong change. | Move into an ADR, then delete |

Rules of thumb:
- When unsure between Tautology and Decision Record, ask: "Would a competent maintainer break something without this?" If not, it is a Tautology.
- A Stale comment that turns out to hide a real bug also gets an issue.
- Before filing an Excuse issue, **reproduce** what it hides (run the code path or read the library source) and put the evidence in the issue. Do not file guesses.
- If a Decision Record is really a unit or contract for a field or argument, also add it to that object's docstring (`Attributes:` or `Args:`). Docstrings are allowed.

Write the inventory to a CSV in the scratchpad (`file, line, comment, category, action`) so it can go into the PR description.

## 3. Act

- **Issues:** use the GitHub MCP `issue_write` tool. Give each a title, a code permalink at the commit before the deletion, the evidence, and a suggested fix. End the body with the Claude Code footer. If Issues is disabled (HTTP 410), write the issue to `docs/issues/NN-slug.md` instead (title as the H1) and add it to `docs/issues/README.md`.
- **ADRs:** add `docs/adr/NNNN-slug.md` using the headings of the existing ADRs (Status, Context, Decision, Consequences, plus a line naming the comments it replaces). Add a row to `docs/adr/README.md`. Extend an existing ADR instead when the decision clearly belongs there.
- **Deletion:** remove whole comment-only lines, and strip inline comments together with the whitespace before them. Never touch pragmas, strings or docstrings. Then run `uv run ruff format`.

Prove the deletions changed no code. Every file whose only change is deleted comments must have an identical AST:

```bash
uv run python - <<'PY'
import ast, subprocess
from pathlib import Path
changed = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "*.py"],
                         capture_output=True, text=True, check=True).stdout.split()
for f in changed:
    old = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
    same = ast.dump(ast.parse(old)) == ast.dump(ast.parse(Path(f).read_text()))
    print("same AST " if same else "DIFFERENT", f)
PY
```

Only files where you intentionally edited docstrings may show `DIFFERENT`.

## 4. Tighten the ratchet and verify

```bash
uv run python scripts/check_comments.py   # exits 1 once while it tightens the baseline
uv run python scripts/check_comments.py   # must now exit 0
uv run ruff check && uv run ruff format --check && uv run pyright
uv run pytest -m "not slow"
```

Commit `.comment-baseline.json` with the deletions. Never raise a count in it. If a comment must stay for now, leave it out of this run, and the baseline will keep tolerating it.

## 5. Report

Give counts per category, the ADRs and issues created, and the lines removed (`git diff --shortstat` for the deletion commit). Also list any comments left in scope and why.
