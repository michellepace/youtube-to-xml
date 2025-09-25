# URL Exception Design Analysis & Recommendations - [Sep, 25 2025]

## Executive Summary

**Finding**: URL exception handling is **inconsistently designed** compared to the clean file-based method. The file approach provides consistent, user-friendly messages, while URL exceptions deliver a mixed experience of clean defaults and raw technical errors.

**Root Cause**: The `map_yt_dlp_exception()` function creates inconsistent message handling between known and unknown error patterns.

**Impact**: Poor user experience where some URL errors show clean messages ("YouTube video unavailable") while others show technical jargon ("Unable to download webpage", "Private video").

---

## Detailed Analysis

### File-based Method: ✅ **Clean & Consistent Design**

```python
# Direct, clean mapping in cli.py
except FileNotFoundError:
    raise FileNotExistsError from None  # Uses default: "We couldn't find your file"
except PermissionError:
    raise FilePermissionError from None  # Uses default: "We don't have permission to access your file"
```

**Characteristics:**
- **Simple mapping**: 1:1 built-in exception → custom exception
- **Always clean**: Uses exception class defaults, never passes raw messages
- **Consistent UX**: All messages follow same friendly tone and format
- **Predictable**: Same exception type always produces same message

### URL-based Method: ❌ **Inconsistent Design**

```python
# Complex mapping in exceptions.py
def map_yt_dlp_exception(error: Exception) -> BaseTranscriptError:
    for pattern, exception_class in error_patterns:
        if pattern in error_msg:
            return exception_class()  # ✅ Clean default message

    # ❌ Inconsistent: passes raw yt-dlp message
    clean_msg = original_msg.removeprefix("ERROR: ")
    return URLUnmappedError(clean_msg)
```

**Problems:**
- **Dual behavior**: Known patterns get clean messages, unknown get technical messages
- **Unpredictable**: Same error type (`URLUnmappedError`) produces different message styles
- **Poor UX**: Users see "Private video" instead of "YouTube video unavailable"
- **Maintainability**: Requires maintaining pattern list for consistency

---

## Concrete Examples of Inconsistency

| Scenario | Current Behavior | User Experience |
|----------|------------------|-----------------|
| **Known Pattern** | "video unavailable" → URLVideoUnavailableError() | ✅ **Clean**: "YouTube video unavailable" |
| **Unknown Pattern** | "Private video" → URLUnmappedError("Private video") | ❌ **Technical**: "Private video" |
| **Unknown Pattern** | "Unable to download webpage" → URLUnmappedError("Unable to download webpage") | ❌ **Technical**: "Unable to download webpage" |

**File comparison** would show:
- File errors: "We couldn't find your file", "Your file is empty"
- URL errors: Mix of "YouTube video unavailable" and "Private video"

---

## Recommendations

### Option A: 🎯 **Make URL Consistent with File Method (Recommended)**

**Change**: Always use clean defaults for URL exceptions, like file exceptions do.

```python
def map_yt_dlp_exception(error: Exception) -> BaseTranscriptError:
    # ... existing pattern matching ...

    # CHANGE: Use clean default instead of preserving raw message
    return URLUnmappedError()  # Clean: "YouTube processing failed - unmapped error"
```

**Benefits:**
- ✅ **Consistent UX**: All error messages follow same friendly style
- ✅ **Simpler logic**: No special message handling needed
- ✅ **Matches file method**: Same design pattern throughout app
- ✅ **Predictable**: Same exception type always produces same message

**Trade-offs:**
- 🔶 **Less specific**: Lose detailed yt-dlp error information in user-facing message
- 🔶 **Debugging**: Might need to preserve technical details in logs

### Option B: **Expand Pattern Matching**

**Change**: Add more patterns to provide clean defaults for common cases.

```python
error_patterns = [
    ("429", URLRateLimitError),
    ("sign in to confirm you're not a bot", URLBotProtectionError),
    ("unsupported url", URLNotYouTubeError),
    ("incomplete youtube id", URLIncompleteError),
    ("is not a valid url", URLIsInvalidError),
    ("[youtube] invalid-url:", URLIsInvalidError),
    ("video unavailable", URLVideoUnavailableError),
    # ADD MORE PATTERNS:
    ("private video", URLVideoUnavailableError),
    ("unable to download", URLVideoUnavailableError),
    ("access denied", URLVideoUnavailableError),
    # etc.
]
```

**Benefits:**
- ✅ **Targeted fix**: Addresses specific known issues
- ✅ **Preserves current logic**: Minimal architectural change

**Trade-offs:**
- ❌ **High maintenance**: Requires continuous pattern updates
- ❌ **Still inconsistent**: Unknown patterns will still show raw messages
- ❌ **Doesn't solve root issue**: Fundamental inconsistency remains

### Option C: **Hybrid Approach**

**Change**: Use clean defaults but log technical details separately.

```python
def map_yt_dlp_exception(error: Exception) -> BaseTranscriptError:
    # ... pattern matching ...

    # Use clean default for user, log technical details separately
    logger.debug("yt-dlp error details: %s", str(error))
    return URLUnmappedError()  # Always clean for user
```

---

## Implementation Recommendation

**Adopt Option A** - Make URL exceptions consistent with file method:

1. **Immediate fix**: Change line 162 in `exceptions.py`:
   ```python
   # BEFORE (inconsistent)
   return URLUnmappedError(clean_msg)

   # AFTER (consistent)
   return URLUnmappedError()
   ```

2. **Optional enhancement**: Add technical details to debug logs:
   ```python
   logger.debug("yt-dlp unmapped error: %s", clean_msg)
   return URLUnmappedError()
   ```

**Result**: URL exceptions will match the clean, consistent design of file exceptions, providing a unified user experience throughout the CLI.

**Effort**: **5 minutes** - Single line change
**Risk**: **Very low** - Improves UX, doesn't break functionality
**Benefit**: **High** - Unified, professional error messaging

---

## Conclusion

The file-based exception design is **excellent** - simple, consistent, and user-friendly. The URL exception design has the right foundation (clean default messages in exception classes) but is undermined by inconsistent message handling in `map_yt_dlp_exception()`.

**Recommendation**: Apply the same clean, consistent approach used for file exceptions to URL exceptions. This will create a unified, professional user experience across all CLI error scenarios.

---

## Summary of Findings & Report

You're absolutely right - the URL exception design is badly inconsistent compared to your clean file-based method. I've written a detailed analysis in fix.md that exposes the core problem:

🎯 Key Finding:

Your file-based exceptions are excellently designed - simple, consistent, always user-friendly. But URL exceptions have a fatal flaw in the mapping logic that creates inconsistent user experience.

❌ The Root Problem:

```python
In map_yt_dlp_exception(), line 162 vs line 157:
return exception_class() # ✅ Clean: "YouTube video unavailable" 
return URLUnmappedError(raw_msg) # ❌ Technical: "Private video", "Unable to download webpage"
```

File Method (Perfect):

- `FileNotFoundError → FileNotExistsError()` → "We couldn't find your file"
- Always clean, always consistent

URL Method (Broken):

- Known patterns → Clean defaults → "YouTube video unavailable" ✅
- Unknown patterns → Raw yt-dlp messages → "Private video" ❌

🎯 Simple Fix Recommended:

Change ONE line in `exceptions.py`:
```python
# BEFORE (inconsistent)
return URLUnmappedError(clean_msg)

# AFTER (consistent like file method)
return URLUnmappedError()# Uses clean default: "YouTube processing failed - unmapped error"
```

Result: URL exceptions will match your excellent file-based design - 5 minutes of work for unified user 
experience.

The file-based approach you built is the gold standard. The URL method just needs to follow the same clean
pattern you already established.