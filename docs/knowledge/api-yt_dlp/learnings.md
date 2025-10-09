# YouTube Rate Limiting & yt-dlp: Complete Solution Guide

## The Starting Problem

YouTube frequently changes its API and rate limiting rules, causing `uv run scripts/url_to_transcript.py <youtube_url>` to fail with **HTTP Error 429: Too Many Requests**.

**Context**: This script only downloads video metadata and subtitles/transcripts from single YouTube URLs (no video/audio downloading, no batch processing).

## Code Changes Made

### Script Optimization: 564 → 523 lines (-41 lines, -7.3%)

**Git diff**: `73 insertions(+), 114 deletions(-)`

### Core Architectural Change

**Before**: Two-step process with direct HTTP requests

```python
# Step 1: yt-dlp gets metadata + subtitle URLs  
metadata = fetch_video_metadata(url)  
# Step 2: urllib directly downloads subtitle files (❌ Rate limited)
with urlopen(metadata.subtitle_url) as response:
    json_text = response.read().decode("utf-8")
```

**After**: Single-step process using yt-dlp throughout

```python  
# yt-dlp handles both metadata AND subtitle download (✅ Rate limiting protection)
with tempfile.TemporaryDirectory() as temp_dir:
    ydl.process_info(info)
    subtitle_files = list(Path(temp_dir).glob(f"*[{video_id}]*.json3"))
```

### Benefits of Code Changes

- **Eliminated custom HTTP handling** - removed `urllib.request.urlopen()` calls
- **Unified data flow** - single function returns both metadata and subtitles
- **Better error handling** - consistent yt-dlp exception handling
- **Cleaner architecture** - reduced complexity and duplicate code paths

### yt-dlp Configuration Using Default Behaviour

```python
options = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "writesubtitles": True,
    "writeautomaticsub": True,
    "subtitleslangs": ["en", "en-orig"],
    "subtitlesformat": "json3",
    "outtmpl": "%(title)s [%(id)s].%(ext)s",
}
```

**Rate limiting protection**: Relies on yt-dlp's built-in intelligence and default behaviour rather than overriding with potentially invalid options.

**Rate limiting options available but unused**: The following options are supported in both CLI and Python API but not used in our implementation:

- `--extractor-retries` → `extractor_retries` key (default: 3 retries)
- `--socket-timeout` → `socket_timeout` key (configures network timeout)
- `--extractor-args` → `extractor_args` key (available but typically unnecessary for unauthenticated access)

**Template approach**: Uses complex template `"%(title)s [%(id)s].%(ext)s"` with glob pattern matching for robust file handling.

## yt-dlp Nightly Build Configuration ✅

### Official Recommendation

Per yt-dlp README: *"The `nightly` channel...is the **recommended channel for regular users** of yt-dlp"*

### Configuration Added

**pyproject.toml**:

```toml
[project]
dependencies = [
    "yt-dlp>=2025.9.5",
]

[tool.uv]
prerelease = "allow"
```

**Update command**: `uv lock --upgrade-package yt-dlp && uv sync`

- Upgrades from stable (`2025.9.5`) to latest nightly (`2025.09.07.232816`)
- UV automatically adds `prerelease-mode = "allow"` to uv.lock

## Testing Results: Network vs Code Impact

### Network Impact Testing ⚠️

**Alternative Network**: ✅ Script works perfectly (235 subtitles → 11 chapters)
**Original Network**: ❌ Still fails with HTTP 429 errors

### Critical Finding

Even with **all code improvements implemented**, the script **still fails on the original network** that experienced heavy rate limiting. This proves:

1. **Code changes provide architectural benefits** (cleaner, shorter, better error handling)
2. **Rate limiting is primarily IP-based**, not method-based  
3. **Network switching remains the primary solution** for immediate relief
4. **yt-dlp's built-in methods are also affected** by aggressive IP-based rate limiting

## What Holds True 🎯

### **Network/IP Rate Limiting is Primary Factor**

- **Rate limiting is per-IP address** - most important factor
- **Heavy usage patterns get IPs blacklisted** by YouTube
- **Code improvements don't overcome IP-based blocks**
- **Network switching provides immediate relief**

### **yt-dlp Nightly Builds Still Matter**  

- **YouTube changes detection methods frequently**
- **Nightly builds stay ahead of changes** with latest countermeasures
- **Essential for long-term reliability**, even if not solving immediate IP issues

### **Architectural Improvements Have Value**

- **Cleaner codebase** (41 fewer lines, unified flow)
- **Better error handling** and consistency
- **Following yt-dlp best practices** vs. bypassing their protections

## Current Status & Recommendations

### **Primary Solution Hierarchy**

1. **Network switching** - Most effective for immediate relief from rate limiting
2. **yt-dlp nightly updates** - `uv lock --upgrade-package yt-dlp && uv sync`
3. **Wait for rate limit reset** - Time-based recovery (hours to days)
4. **Code architecture** - Follow yt-dlp patterns vs. custom HTTP calls

### **User Workflow**

- **Fresh clones**: `uv sync` (uses current lockfile)
- **Rate limiting occurs**:
  1. Try `uv lock --upgrade-package yt-dlp && uv sync`
  2. If still failing, switch networks or wait
- **Regular maintenance**: Update yt-dlp monthly

### **Key Learnings**

- **Rate limiting is IP-based first**, method-based second
- **YouTube's detection is sophisticated** - even yt-dlp can be blocked per-IP
- **Code quality matters** for maintainability, but won't solve IP blocks
- **Network diversity** is the most reliable workaround for heavy users

## Template Simplification Learning 📝

### Output Template Complexity Issue

During optimization, we discovered that changing the `outtmpl` from complex to simple requires coordinated changes:

**Original working approach**:

- Template: `"%(title)s [%(id)s].%(ext)s"` → Files like `"Phone Your Architecture [-ZS9NmYq5To].json3"`
- Finding: `glob(f"*[{video_id}]*.json3")` → Handles any title complexity

**Attempted simplification**:

- Template: `"%(id)s.%(ext)s"` → Files like `"-ZS9NmYq5To.json3"`
- Finding: `Path(f"{video_id}.json3")` → Direct path construction

**Key insight**: Both template and file-finding logic must be changed together. The script currently uses the proven complex template approach with matching glob logic for reliability.

### Recommendations

- **Keep complex template + glob**: More robust, handles edge cases
- **Or fully implement simple approach**: Change both template and finding logic together
- **Never mix approaches**: Template and file-finding must match

This solution provides **architectural improvements and best practices**, but **network switching remains the primary tool** against YouTube's IP-based rate limiting.
