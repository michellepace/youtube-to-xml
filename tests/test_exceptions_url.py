"""Tests all YouTube exception scenarios by hitting the real yt-dlp API.

Each test verifies both exit code and error message for comprehensive coverage.
"""

import subprocess
from pathlib import Path

import pytest


def run_script(url: str, tmp_path: Path | None = None) -> tuple[int, str]:
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


# === Input Validation ===
@pytest.mark.integration
def test_empty_url_raises_invalid_format_error(tmp_path: Path) -> None:
    """Empty URL should be rejected."""
    exit_code, output = run_script("", tmp_path)
    assert exit_code == 1
    assert "❌ Input must be a YouTube URL or .txt file" in output
    assert "Try: youtube-to-xml --help" in output


@pytest.mark.integration
def test_plain_text_raises_invalid_format_error(tmp_path: Path) -> None:
    """Non-URL text should be rejected."""
    exit_code, output = run_script("some_text", tmp_path)
    assert exit_code == 1
    assert "❌ Input must be a YouTube URL or .txt file" in output
    assert "Try: youtube-to-xml --help" in output


# === URL Domain Validation ===
@pytest.mark.integration
def test_non_youtube_url_raises_not_youtube_error(tmp_path: Path) -> None:
    """Non-YouTube URLs should be rejected."""
    exit_code, output = run_script("https://www.google.com/", tmp_path)
    assert exit_code == 1
    assert "URL is not a YouTube video" in output


@pytest.mark.integration
def test_invalid_domain_raises_unmapped_error(tmp_path: Path) -> None:
    """Unreachable domains should fail gracefully."""
    exit_code, output = run_script("https://ailearnlog", tmp_path)
    assert exit_code == 1
    assert "Unable to download webpage" in output


# === YouTube URL Format ===
@pytest.mark.integration
def test_incomplete_youtube_id_raises_incomplete_error(tmp_path: Path) -> None:
    """Truncated video IDs should be detected."""
    exit_code, output = run_script("https://www.youtube.com/watch?v=Q4g", tmp_path)
    assert exit_code == 1
    assert "YouTube URL is incomplete" in output


@pytest.mark.integration
def test_invalid_youtube_id_format_raises_invalid_error(tmp_path: Path) -> None:
    """Invalid character patterns in video IDs should be caught."""
    exit_code, output = run_script(
        "https://www.youtube.com/watch?v=invalid-url", tmp_path
    )
    assert exit_code == 1
    assert "Invalid URL format" in output


# === Video Availability ===
@pytest.mark.integration
def test_removed_video_raises_unavailable_error(tmp_path: Path) -> None:
    """Handles videos removed from YouTube."""
    exit_code, output = run_script("https://youtu.be/ai_HGCf2w_w", tmp_path)
    assert exit_code == 1
    assert "YouTube video unavailable" in output


@pytest.mark.integration
def test_private_video_raises_unavailable_error(tmp_path: Path) -> None:
    """Handles private/restricted videos."""
    exit_code, output = run_script("https://youtu.be/15vClfaR35w", tmp_path)
    assert exit_code == 1
    assert "Private video" in output


# === Transcript Availability ===
@pytest.mark.integration
def test_video_without_transcript_raises_transcript_not_found_error(
    tmp_path: Path,
) -> None:
    """Handles videos that exist but lack transcripts."""
    exit_code, output = run_script(
        "https://www.youtube.com/watch?v=6eBSHbLKuN0", tmp_path
    )
    assert exit_code == 1
    assert "This video doesn't have a transcript available" in output


# === Network/Access ===
@pytest.mark.integration
def test_bot_protection_handles_gracefully(tmp_path: Path) -> None:
    """Intermittent bot protection should either succeed or fail cleanly."""
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


# === Success Case ===
@pytest.mark.integration
def test_valid_video_with_transcript_creates_xml_successfully(
    tmp_path: Path,
) -> None:
    """End-to-end success with stable public video."""
    # Using Rick Astley - Never Gonna Give You Up (stable, public video)
    exit_code, output = run_script(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", tmp_path
    )
    assert exit_code == 0
    assert "✅ Created" in output
    # Verify XML file was created in tmp directory
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1
