"""Tests for the no-comments ratchet in scripts/check_comments.py."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from check_comments import Comment, find_comments, main, ratchet

if TYPE_CHECKING:
    from pathlib import Path


def test_finds_full_line_comment() -> None:
    assert find_comments("# explain\nx = 1\n") == [Comment(line=1, text="# explain")]


def test_finds_inline_comment() -> None:
    assert find_comments("x = 1  # explain\n") == [Comment(line=1, text="# explain")]


def test_ignores_hash_inside_string() -> None:
    assert find_comments('x = "# not a comment"\n') == []


@pytest.mark.parametrize(
    "pragma",
    [
        "# noqa",
        "# noqa: S603",
        "# noqa: S603, PLR2004",
        "# type: ignore",
        "# type: ignore[call-arg]",
        "# pyright: ignore[reportPrivateUsage]",
        "# pyright: reportPrivateUsage=false",
        "# pyright: strict",
        "# fmt: off",
        "# fmt: skip",
        "# pragma: no cover",
        "# type: ignore[call-arg]  # noqa: E501",
    ],
)
def test_ignores_tool_pragmas(pragma: str) -> None:
    assert find_comments(f"x = 1  {pragma}\n") == []


def test_counts_prose_smuggled_after_pragma() -> None:
    source = "x = 1  # noqa: S603  # because reasons\n"
    assert len(find_comments(source)) == 1


def test_ignores_shebang_and_encoding_lines() -> None:
    source = "#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nx = 1\n"
    assert find_comments(source) == []


def test_ratchet_passes_when_counts_match_baseline() -> None:
    over_limit, new_baseline = ratchet({"a.py": 2}, {"a.py": 2})
    assert over_limit == {}
    assert new_baseline == {"a.py": 2}


def test_ratchet_flags_file_above_baseline() -> None:
    over_limit, _ = ratchet({"a.py": 3}, {"a.py": 2})
    assert over_limit == {"a.py": 2}


def test_ratchet_flags_new_file_with_any_comment() -> None:
    over_limit, _ = ratchet({"new.py": 1}, {})
    assert over_limit == {"new.py": 0}


def test_ratchet_tightens_baseline_when_comments_removed() -> None:
    _, new_baseline = ratchet({"a.py": 1}, {"a.py": 4})
    assert new_baseline == {"a.py": 1}


def test_ratchet_drops_files_that_reach_zero() -> None:
    _, new_baseline = ratchet({}, {"a.py": 4, "b.py": 1})
    assert new_baseline == {}


def test_ratchet_never_loosens_baseline_for_file_above_limit() -> None:
    _, new_baseline = ratchet({"a.py": 9}, {"a.py": 2})
    assert new_baseline == {"a.py": 2}


def _write_baseline(path: Path, baseline: dict[str, int]) -> None:
    path.write_text(json.dumps(baseline), encoding="utf-8")


def test_main_passes_for_comment_free_code(tmp_path: Path) -> None:
    code = tmp_path / "clean.py"
    code.write_text("x = 1\n", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    _write_baseline(baseline, {})

    assert main(["--baseline", str(baseline), str(tmp_path)]) == 0


def test_main_rejects_new_comment_and_shows_where(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = tmp_path / "commented.py"
    code.write_text("x = 1  # explain\n", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    _write_baseline(baseline, {})

    exit_code = main(["--baseline", str(baseline), str(tmp_path)])

    assert exit_code == 1
    assert f"{code}:1: # explain" in capsys.readouterr().out


def test_main_tightens_baseline_file_and_fails_so_it_is_committed(
    tmp_path: Path,
) -> None:
    code = tmp_path / "legacy.py"
    code.write_text("x = 1  # one left\n", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    _write_baseline(baseline, {str(code): 3})

    exit_code = main(["--baseline", str(baseline), str(tmp_path)])

    assert exit_code == 1
    assert json.loads(baseline.read_text(encoding="utf-8")) == {str(code): 1}


def test_main_treats_missing_baseline_as_empty(tmp_path: Path) -> None:
    code = tmp_path / "commented.py"
    code.write_text("# explain\n", encoding="utf-8")

    exit_code = main(["--baseline", str(tmp_path / "absent.json"), str(tmp_path)])

    assert exit_code == 1


def test_main_list_prints_every_comment_and_never_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = tmp_path / "legacy.py"
    code.write_text("# first\nx = 1  # second\n", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    _write_baseline(baseline, {str(code): 2})

    exit_code = main(["--baseline", str(baseline), "--list", str(tmp_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert f"{code}:1: # first" in output
    assert f"{code}:2: # second" in output
