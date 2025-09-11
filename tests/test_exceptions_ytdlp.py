"""Tests all YouTube exception scenarios by hitting the real yt-dlp API.

Each test verifies both exit code and error message for comprehensive coverage.
"""

import subprocess
from pathlib import Path

import pytest


def run_script(url: str, tmp_path: Path | None = None) -> tuple[int, str]:
    """Run url_to_transcript.py script and return (exit_code, output)."""
    result = subprocess.run(  # noqa: S603
        ["uv", "run", "url-to-transcript", url],
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


# Basic input validation
@pytest.mark.integration
def test_empty_url(tmp_path: Path) -> None:
    """Empty URL should be rejected."""
    exit_code, output = run_script("", tmp_path)
    assert exit_code == 1
    assert "Invalid URL format" in output


@pytest.mark.integration
def test_not_a_url(tmp_path: Path) -> None:
    """Malformed text should be rejected."""
    exit_code, output = run_script("not_a_url_at_all", tmp_path)
    assert exit_code == 1
    assert "Invalid URL format" in output


# URL format validation
@pytest.mark.integration
def test_wrong_website(tmp_path: Path) -> None:
    """Non-YouTube URL should be rejected."""
    exit_code, output = run_script("https://www.google.com/", tmp_path)
    assert exit_code == 1
    assert "URL is not a YouTube video" in output


@pytest.mark.integration
def test_youtube_url_too_short(tmp_path: Path) -> None:
    """Truncated YouTube ID should be rejected."""
    exit_code, output = run_script("https://www.youtube.com/watch?v=Q4g", tmp_path)
    assert exit_code == 1
    assert "YouTube URL is incomplete" in output


# YouTube video issues
@pytest.mark.integration
def test_youtube_video_not_found(tmp_path: Path) -> None:
    """Invalid YouTube video ID should be rejected."""
    exit_code, output = run_script(
        "https://www.youtube.com/watch?v=invalid-url", tmp_path
    )
    assert exit_code == 1
    assert "Invalid URL format" in output


@pytest.mark.integration
def test_deleted_youtube_video(tmp_path: Path) -> None:
    """Deleted/removed video should be rejected."""
    exit_code, output = run_script("https://youtu.be/ai_HGCf2w_w", tmp_path)
    assert exit_code == 1
    assert "YouTube video unavailable" in output


@pytest.mark.integration
def test_video_without_captions(tmp_path: Path) -> None:
    """Video without subtitles should be rejected."""
    exit_code, output = run_script(
        "https://www.youtube.com/watch?v=6eBSHbLKuN0", tmp_path
    )
    assert exit_code == 1
    assert "This video doesn't have subtitles available" in output


@pytest.mark.integration
def test_private_video_blocked(tmp_path: Path) -> None:
    """Private video should be rejected."""
    exit_code, output = run_script("https://youtu.be/15vClfaR35w", tmp_path)
    assert exit_code == 1
    assert "Private video" in output


# Network/access issues
@pytest.mark.integration
def test_unreachable_website(tmp_path: Path) -> None:
    """Invalid domain should be rejected."""
    exit_code, output = run_script("https://ailearnlog", tmp_path)
    assert exit_code == 1
    assert "Unable to download webpage" in output


@pytest.mark.integration
def test_bot_protection_intermittent(tmp_path: Path) -> None:
    """Video that may trigger bot protection or succeed."""
    # This is intermittent - could succeed (0) or fail (1) due to bot protection
    exit_code, output = run_script(
        "https://www.youtube.com/watch?v=Q4gsvJvRjCU", tmp_path
    )
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


# Success case for completeness
@pytest.mark.integration
def test_valid_video_with_subtitles(tmp_path: Path) -> None:
    """Known good video should succeed."""
    # Using Rick Astley - Never Gonna Give You Up (stable, public video)
    exit_code, output = run_script(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", tmp_path
    )
    assert exit_code == 0
    assert "✅ Created:" in output
    # Verify XML file was created in tmp directory
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1
