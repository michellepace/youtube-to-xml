# yt-dlp Error Classification Investigation

## Testing Scenarios to Understand Error Types

### Scenario 1: Rate Limited Network
**URL:** https://www.youtube.com/watch?v=Q4gsvJvRjCU
**Expected:** Some form of rate limiting error
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

---

### Scenario 2: Non-Rate Limited Network (New IP)
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
- Confirms the "Sign in to confirm you're not a bot" was network/IP specific

---

### Scenario 3: Video with No Transcript (Clean Network)
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

### Scenario 4: Empty URL Input
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
- Should be classified as URLVideoNotFoundError

---

### Scenario 5: Malformed URL Format  
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
- Should be classified as URLVideoNotFoundError

---

### Scenario 6: Non-YouTube URL
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
- Should be classified as URLVideoNotFoundError

---

### Scenario 7: Truncated YouTube URL
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
- Should be classified as URLVideoNotFoundError

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

1. **Your previous "rate limiting" was actually bot protection** - different concept entirely
2. **Bot protection is network/IP specific** - switching networks resolves it
3. **Current script behavior is mostly correct** for genuine "no transcript" cases
4. **The problem**: Bot protection errors are being misclassified as subtitle errors

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
| **Empty URL** | Scenario 4 | `DownloadError` | "'' is not a valid URL" | ❓ Unknown | ✅ Should be `URLVideoNotFoundError` |
| **Malformed URL** | Scenario 5 | `DownloadError` | "Video unavailable" | ❓ Unknown | ✅ Should be `URLVideoNotFoundError` |
| **Non-YouTube URL** | Scenario 6 | `DownloadError` | "Unsupported URL" | ❓ Unknown | ✅ Should be `URLVideoNotFoundError` |
| **Truncated YouTube URL** | Scenario 7 | `DownloadError` | "Incomplete YouTube ID" | ❓ Unknown | ✅ Should be `URLVideoNotFoundError` |
| **HTTP 429** | Not tested | `DownloadError` | "HTTP Error 429" / "429" | ✅ `URLRateLimitError` | ✅ Keep as-is |

## Action Plan

1. **Create `URLBotProtectionError`** for bot protection scenarios (Scenario 1)
2. **Update script error handling** to catch bot protection during `extract_info()`
3. **Verify invalid URL handling** maps to `URLVideoNotFoundError` (Scenarios 4, 5, 6 & 7)
4. **Keep existing HTTP 429 detection** for genuine rate limiting (existing logic)
5. **Keep existing no-transcript handling** for genuine subtitle unavailability (Scenario 3)
6. **Update tests** to cover all scenarios

## Key Insights

- **Bot protection (Scenario 1)** occurs during video metadata extraction, not subtitle processing
- **Success case (Scenario 2)** confirms bot protection is network/IP specific
- **No transcript (Scenario 3)** is correctly handled by existing logic
- **Invalid URLs (Scenarios 4, 5, 6 & 7)** need proper classification as video not found errors
- **HTTP 429 detection** remains valid for genuine rate limiting (though not encountered in testing)