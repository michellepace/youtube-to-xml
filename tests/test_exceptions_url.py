"""Tests all YouTube exception scenarios by hitting the real yt-dlp API.

Each test verifies both exit code and error message for comprehensive coverage.
"""

import subprocess
from pathlib import Path

import pytest

from youtube_to_xml.exceptions import EXCEPTION_MESSAGES


def run_cli(url: str, tmp_path: Path | None = None) -> tuple[int, str]:
    """Run youtube-to-xml CLI and return (exit_code, output)."""
    result = subprocess.run(  # noqa: S603
        ["uv", "run", "youtube-to-xml", url],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=15,
        check=False,
    )

    # Handle rate limiting - skip test if encountered
    if result.returncode != 0:
        output = (result.stderr + result.stdout).lower()
        if any(pattern in output for pattern in ["429", "rate limit", "bot protection"]):
            pytest.skip("YouTube rate limited or bot protection triggered")

    return result.returncode, result.stdout + result.stderr


# === URL Domain Validation ===
@pytest.mark.slow
def test_non_youtube_url_raises_not_youtube_error(tmp_path: Path) -> None:
    """Non-YouTube URLs should be rejected."""
    exit_code, output = run_cli("https://www.google.com/", tmp_path)
    assert exit_code == 1
    assert EXCEPTION_MESSAGES["url_not_youtube_error"] in output


@pytest.mark.slow
def test_invalid_domain_raises_unmapped_error(tmp_path: Path) -> None:
    """Unreachable domains should fail gracefully."""
    exit_code, output = run_cli("https://nonexistent-domain-12345.com", tmp_path)
    assert exit_code == 1
    assert "unable to download webpage" in output.lower()


# === YouTube URL Format ===
@pytest.mark.slow
def test_incomplete_youtube_id_raises_incomplete_error(tmp_path: Path) -> None:
    """Truncated video IDs should be detected."""
    exit_code, output = run_cli("https://www.youtube.com/watch?v=Q4g", tmp_path)
    assert exit_code == 1
    assert EXCEPTION_MESSAGES["url_incomplete_error"] in output


@pytest.mark.slow
def test_invalid_youtube_id_format_raises_invalid_error(tmp_path: Path) -> None:
    """Invalid character patterns in video IDs should be caught."""
    exit_code, output = run_cli("https://www.youtube.com/watch?v=invalid-url", tmp_path)
    assert exit_code == 1
    assert EXCEPTION_MESSAGES["url_is_invalid_error"] in output


# === Video Availability ===
@pytest.mark.slow
def test_removed_video_raises_unavailable_error(tmp_path: Path) -> None:
    """Handles videos removed from YouTube."""
    exit_code, output = run_cli("https://youtu.be/ai_HGCf2w_w", tmp_path)
    assert exit_code == 1
    assert EXCEPTION_MESSAGES["url_video_unavailable_error"] in output


@pytest.mark.slow
def test_private_video_raises_private_error(tmp_path: Path) -> None:
    """Handles private/restricted videos."""
    exit_code, output = run_cli("https://youtu.be/15vClfaR35w", tmp_path)
    assert exit_code == 1
    assert EXCEPTION_MESSAGES["url_video_is_private_error"] in output


# === Transcript Availability ===
@pytest.mark.slow
def test_video_without_transcript_raises_transcript_not_found_error(
    tmp_path: Path,
) -> None:
    """Handles videos that exist but lack transcripts."""
    exit_code, output = run_cli("https://www.youtube.com/watch?v=6eBSHbLKuN0", tmp_path)
    assert exit_code == 1
    assert EXCEPTION_MESSAGES["url_transcript_not_found_error"] in output


# === Network/Access ===
@pytest.mark.slow
def test_bot_protection_handles_gracefully(tmp_path: Path) -> None:
    """Intermittent bot protection should either succeed or fail cleanly."""
    # This is intermittent - could succeed (0) or fail (1) due to bot protection
    exit_code, output = run_cli("https://www.youtube.com/watch?v=Q4gsvJvRjCU", tmp_path)
    assert exit_code in [0, 1]  # Either works or fails gracefully
    if exit_code == 1:
        # If it fails, should be due to bot protection
        assert any(
            phrase in output.lower() for phrase in ["verification", "bot", "sign in"]
        )
    else:
        # If it succeeds, should create an XML file in tmp directory
        xml_files = list(tmp_path.glob("*.xml"))
        assert len(xml_files) == 1


# === Success Case ===
@pytest.mark.slow
def test_valid_video_with_transcript_creates_xml_successfully(
    tmp_path: Path,
) -> None:
    """End-to-end success with stable public video."""
    # Using Rick Astley - Never Gonna Give You Up (stable, public video)
    exit_code, output = run_cli("https://www.youtube.com/watch?v=dQw4w9WgXcQ", tmp_path)
    assert exit_code == 0
    assert "✅ Created" in output
    # Verify XML file was created in tmp directory
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1
