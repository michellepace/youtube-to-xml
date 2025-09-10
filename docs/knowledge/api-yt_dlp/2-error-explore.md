# yt-dlp Error Classification Investigation

## Run Test Scenarios

Test scenario results obtained from running Python directly against `yt-dlp` API to determine true behaviour (independent of `scripts/url_to_transcript.py`).

To retest the scenario against the script behaviour use: `uv run scripts/url_to_transcript.py <URL>`

## Test Scenario Results to Understand Error Types

### Scenario 1: Bot Protection Network (Not Traditional Rate Limiting)
**URL:** https://www.youtube.com/watch?v=Q4gsvJvRjCU
**Expected:** Bot protection error (often confused with rate limiting)
**Actual Error:**
```
ERROR: [youtube] Q4gsvJvRjCU: Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies for the authentication.
```
**Exception Type:** `yt_dlp.utils.DownloadError`
**Key Observations:**
- No HTTP status code (429, etc.) mentioned
- Suggests authentication solution, not "try again later"
- Occurs during video info extraction phase, not subtitle download
- Error message focuses on bot protection, not rate limiting
- Frequently occurs after extensive running of integration tests (hitting API)
- Resolved when I switch to a new network (New IP)

---

### Scenario 2: Clean Network (New IP, No Bot Protection)
**URL:** https://www.youtube.com/watch?v=Q4gsvJvRjCU  
**Expected:** Should work normally
**Network Status:** ✅ Switched to new network/IP address
**Result:** ✅ SUCCESS
```
Title: How Claude Code Hooks Save Me HOURS Daily
Duration: 2m 43s
📝 Downloaded 75 subtitles
📑 Organising into 4 chapter(s)...
✅ Created: how-claude-code-hooks-save-me-hours-daily.xml
```
**Key Observations:**
- Same URL works perfectly on clean network
- Downloads subtitles successfully
- Creates XML file as expected
- Confirms the "Sign in to confirm you're not a bot" was network/IP specific (scenario 1)

---

### Scenario 3: Video with No Transcript (New IP, Clean Network)
**URL:** https://www.youtube.com/watch?v=6eBSHbLKuN0
**Expected:** Should fail with "no subtitles" error
**Network Status:** ✅ Still on new network/IP address
**Result:** ✅ EXPECTED ERROR
```
❌ Error: No subtitle URL found for video (there is no transcript)
```
**Exception Type:** `youtube_to_xml.exceptions.URLSubtitlesNotFoundError`
**Key Observations:**
- Clear, specific error message about missing transcript
- Proper exception classification (URLSubtitlesNotFoundError)
- Video metadata extraction succeeds, only subtitle fetch fails
- This is the correct behavior for videos without transcripts

---

### Scenario 4: Empty URL Input (New IP, Clean Network)
**URL:** Empty
**Network Status:** ✅ Still on new network/IP address
**Purpose:** Test what exceptions yt-dlp throws for empty URL
**Test Method:** Direct yt-dlp call with empty string
```python
yt_dlp.extract_info('', download=False)
```
**Result:** ❌ EXPECTED ERROR
```
ERROR: [generic] '' is not a valid URL
```
**Exception Type:** `yt_dlp.utils.DownloadError`
**Key Observations:**
- Clear error message about invalid URL format
- Occurs during video info extraction phase
- Different message pattern from bot protection
- Should be classified as URLIsInvalidError

---

### Scenario 5: Malformed URL Format (New IP, Clean Network)
**URL:** `invalid-url`
**Network Status:** ✅ Still on new network/IP address
**Purpose:** Test what exceptions yt-dlp throws for completely malformed URL
**Test Method:** Direct yt-dlp call with malformed string
```python
yt_dlp.extract_info('invalid-url', download=False)
```
**Result:** ❌ EXPECTED ERROR
```
ERROR: [youtube] invalid-url: Video unavailable
```
**Exception Type:** `yt_dlp.utils.DownloadError`
**Key Observations:**
- Descriptive error message about video availability
- Occurs during video info extraction phase  
- Different message pattern from bot protection
- Should be classified as URLIsInvalidError

---

### Scenario 6: Non-YouTube URL (New IP, Clean Network)
**URL:** https://www.google.com/
**Network Status:** ✅ Still on new network/IP address
**Purpose:** Test what exceptions yt-dlp throws for valid URL but wrong domain
**Test Method:** Direct yt-dlp call with non-YouTube URL
```python
yt_dlp.extract_info('https://www.google.com/', download=False)
```
**Result:** ❌ EXPECTED ERROR
```
ERROR: Unsupported URL: https://www.google.com/
```
**Exception Type:** `yt_dlp.utils.DownloadError`
**Key Observations:**
- Clear error message about unsupported URL
- Occurs during video info extraction phase
- Different message pattern from bot protection
- Should be classified as URLNotYouTubeError

---

### Scenario 7: Truncated YouTube URL (New IP, Clean Network)
**URL:** https://www.youtube.com/watch?v=VvkhYW
**Network Status:** ✅ Still on new network/IP address
**Purpose:** Test what exceptions yt-dlp throws for truncated YouTube video ID
**Test Method:** Direct yt-dlp call with incomplete YouTube URL
```python
yt_dlp.extract_info('https://www.youtube.com/watch?v=VvkhYW', download=False)
```
**Result:** ❌ EXPECTED ERROR
```
ERROR: [youtube:truncated_id] VvkhYW: Incomplete YouTube ID VvkhYW. URL https://www.youtube.com/watch?v=VvkhYW looks truncated.
```
**Exception Type:** `yt_dlp.utils.DownloadError`
**Key Observations:**
- Very specific error message about truncated ID
- yt-dlp recognizes this as a YouTube URL but invalid
- Occurs during video info extraction phase
- Should be classified as URLIncompleteError

---

## Analysis & Conclusions

### Error Classification Summary:

1. **"Sign in to confirm you're not a bot"** → **Bot Protection** (Network/IP specific)
   - Exception: `yt_dlp.utils.DownloadError` 
   - Cause: IP-based access restriction by YouTube
   - Solution: Change network/IP OR use cookies
   - **Classification: NOT rate limiting, NOT permanent video unavailability**

2. **"No subtitle URL found for video"** → **No Transcript Available** (Permanent)
   - Exception: `youtube_to_xml.exceptions.URLSubtitlesNotFoundError`
   - Cause: Video genuinely has no subtitles/transcript
   - Solution: None - this is permanent
   - **Classification: Correct current behavior**

### Key Findings:

1. **Bot protection is NOT traditional rate limiting** - "Sign in to confirm you're not a bot" is IP-based bot detection, not HTTP 429
2. **Bot protection is network/IP specific** - switching networks resolves it temporarily
3. **HTTP 429 can still occur** - Traditional rate limiting happens during download operations (process_info), not metadata extraction
4. **The problem**: Bot protection errors during extract_info() are currently unhandled and cause crashes

### Recommendations:

1. **Create new exception type**: `URLBotProtectionError` 
2. **Update error detection** to catch "Sign in to confirm you're not a bot"
3. **Provide user guidance** suggesting network change or cookie usage
4. **Keep current URLSubtitlesNotFoundError** for genuine no-transcript cases

---

## Complete Error Classification Matrix

| Error Scenario | Source Scenario | Exception Type | Error Message Pattern | Current Classification | Correct Classification |
|----------------|----------------|----------------|----------------------|----------------------|----------------------|
| **Bot Protection** | Scenario 1 | `DownloadError` | "Sign in to confirm you're not a bot" | ❌ Unhandled crash | 🔄 Need `URLBotProtectionError` |
| **No Transcript** | Scenario 3 | `URLSubtitlesNotFoundError` | "No subtitle URL found for video" | ✅ Correct | ✅ Keep as-is |
| **Empty URL** | Scenario 4 | `DownloadError` | "'' is not a valid URL" | ✅ `URLIsInvalidError` | ✅ Correctly handled |
| **Malformed URL** | Scenario 5 | `DownloadError` | "Video unavailable" | ✅ `URLIsInvalidError` | ✅ Correctly handled |
| **Non-YouTube URL** | Scenario 6 | `DownloadError` | "Unsupported URL" | ✅ `URLNotYouTubeError` | ✅ Correctly handled |
| **Truncated YouTube URL** | Scenario 7 | `DownloadError` | "Incomplete YouTube ID" | ✅ `URLIncompleteError` | ✅ Correctly handled |
| **HTTP 429 (True Rate Limit)** | Not tested but possible | `DownloadError` | "HTTP Error 429" / "429" | ✅ `URLRateLimitError` | ✅ Keep as-is |

## Action Plan

1. **Create `URLBotProtectionError`** for bot protection scenarios (Scenario 1)
2. **Update script error handling** to catch bot protection during `extract_info()`
3. **Verify invalid URL handling** maps to `URLVideoNotFoundError` (Scenarios 4, 5, 6 & 7)
4. **Keep existing HTTP 429 detection** for genuine rate limiting (existing logic)
5. **Keep existing no-transcript handling** for genuine subtitle unavailability (Scenario 3)
6. **Update tests** to cover all scenarios

## Key Insights

- **Bot protection (Scenario 1)** occurs during video metadata extraction (`extract_info()`), NOT during subtitle download
- **Success case (Scenario 2)** confirms bot protection is network/IP specific, not time-based
- **No transcript (Scenario 3)** is correctly handled by existing logic in `process_info()`
- **Invalid URLs (Scenarios 4, 5, 6 & 7)** now properly handled with semantic exception mapping
- **HTTP 429 (true rate limiting)** can still occur during `process_info()` - keep existing detection
- **Important distinction**: Bot protection ≠ Rate limiting (different mechanisms, different solutions)