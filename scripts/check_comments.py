"""Ratchet lint that bans code comments in Python files.

Tool pragmas (noqa, type: ignore, pyright:, fmt:, pragma:) are not comments and
always pass. Prose comments that predate the ban are tolerated per file, up to
the count recorded in the baseline. The baseline only ever shrinks: removing a
comment tightens it automatically, and adding one fails the check.

Why comments are banned, and where decisions go instead: docs/adr/0001.

Usage:
    uv run python scripts/check_comments.py            # ratchet check
    uv run python scripts/check_comments.py --list src # every prose comment
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

DEFAULT_BASELINE = Path(".comment-baseline.json")
DEFAULT_ROOTS = ("src", "tests", "scripts")

_PRAGMA = re.compile(
    r"""
    noqa(:\s*[A-Z]+[0-9]+(\s*,\s*[A-Z]+[0-9]+)*)?
    | type:\s*ignore(\[[^\]]*\])?
    | pyright:\s*(ignore(\[[^\]]*\])?|basic|standard|strict|\w+=\w+(\s*,\s*\w+=\w+)*)
    | fmt:\s*(off|on|skip)
    | pragma:\s*no\s+(cover|branch)
    """,
    re.VERBOSE,
)
_ENCODING = re.compile(r"#.*coding[:=]")
_HEADER_LINES = 2


@dataclass(frozen=True, slots=True)
class Comment:
    """A prose comment found in Python source."""

    line: int
    text: str


def _is_pragma(text: str) -> bool:
    segments = [segment.strip() for segment in text.split("#") if segment.strip()]
    return bool(segments) and all(_PRAGMA.fullmatch(s) for s in segments)


def _is_file_header(text: str, line: int) -> bool:
    is_header_directive = text.startswith("#!") or bool(_ENCODING.match(text))
    return line <= _HEADER_LINES and is_header_directive


def find_comments(source: str) -> list[Comment]:
    """Return every prose comment in source, skipping tool pragmas and headers."""
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return [
        Comment(line=token.start[0], text=token.string)
        for token in tokens
        if token.type == tokenize.COMMENT
        and not _is_pragma(token.string)
        and not _is_file_header(token.string, token.start[0])
    ]


def ratchet(
    counts: Mapping[str, int], baseline: Mapping[str, int]
) -> tuple[dict[str, int], dict[str, int]]:
    """Compare comment counts with the baseline.

    Args:
        counts: Prose comments found per file (files with none may be absent)
        baseline: Comments each file is still allowed (absent means zero)

    Returns:
        Tuple of (files over their allowance mapped to that allowance,
        baseline tightened to the counts found, never loosened)
    """
    over_limit = {
        path: baseline.get(path, 0)
        for path, found in counts.items()
        if found > baseline.get(path, 0)
    }
    tightened = {
        path: min(allowed, counts.get(path, 0)) for path, allowed in baseline.items()
    }
    return over_limit, {path: n for path, n in sorted(tightened.items()) if n > 0}


def _python_files(paths: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file() and path.suffix == ".py":
            files.add(path)
        elif path.is_dir():
            files.update(
                candidate
                for candidate in path.rglob("*.py")
                if not any(
                    part.startswith(".") or part == "__pycache__"
                    for part in candidate.relative_to(path).parts
                )
            )
    return sorted(files)


def _read_baseline(baseline_path: Path) -> dict[str, int]:
    if not baseline_path.is_file():
        return {}
    loaded: dict[str, int] = json.loads(baseline_path.read_text(encoding="utf-8"))
    return loaded


def _write_baseline(baseline_path: Path, baseline: Mapping[str, int]) -> None:
    text = json.dumps(dict(baseline), indent=2, sort_keys=True)
    baseline_path.write_text(f"{text}\n", encoding="utf-8")


def _parse_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_comments",
        description="Fail when Python files gain prose comments (ratchet).",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=list(DEFAULT_ROOTS),
        help="files or directories to scan (default: src tests scripts)",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help="JSON file of comments still allowed per file",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="print every prose comment, including baselined ones, and exit 0",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ratchet check (or list comments) and return the exit code."""
    args = _parse_arguments(argv)
    comments_by_file = {
        str(path): comments
        for path in _python_files(args.paths)
        if (comments := find_comments(path.read_text(encoding="utf-8")))
    }

    if args.list:
        for path, comments in comments_by_file.items():
            for comment in comments:
                print(f"{path}:{comment.line}: {comment.text}")
        total = sum(len(comments) for comments in comments_by_file.values())
        print(f"{total} prose comment(s) in {len(comments_by_file)} file(s)")
        return 0

    baseline = _read_baseline(args.baseline)
    counts = {path: len(comments) for path, comments in comments_by_file.items()}
    over_limit, tightened = ratchet(counts, baseline)

    for path, allowed in over_limit.items():
        print(f"{path}: {counts[path]} comment(s), {allowed} allowed")
        for comment in comments_by_file[path]:
            print(f"{path}:{comment.line}: {comment.text}")
    if over_limit:
        print(
            "\nCode comments are banned (docs/adr/0001). Make the code say it, "
            "record decisions in docs/adr/, or file an issue for a workaround."
        )

    if tightened != baseline:
        _write_baseline(args.baseline, tightened)
        print(f"Tightened {args.baseline}: commit it so the ratchet keeps the gain.")

    return 1 if over_limit or tightened != baseline else 0


if __name__ == "__main__":
    sys.exit(main())
