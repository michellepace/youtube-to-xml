I have an unused `logging_config.py` module that needs integration before merging this PR. I want to activate it without changing any user-facing behavior.

**Constraint**: Keep the **exact same CLI user experience** - all existing `print()` statements in `cli.py` must remain unchanged. Users should see identical console output before and after this change.

**Current Exception Summary**:

<exception_summary>

# Exception Usage Summary

## Current Exception Usage

### Exception Raises

| Exception Type | Module | File | Location(s) | Status |
|---|---|---|---|---|
| `FileEmptyError` | parser | `src/youtube_to_xml/parser.py` | Line 57 | Active |
| `FileInvalidFormatError` | parser | `src/youtube_to_xml/parser.py` | Lines 67, 72, 77, 82 | Active |
| `URLVideoNotFoundError` | transcript_auto_fetcher | `scripts/transcript_auto_fetcher.py` | Lines 140, 203 | Experimental |
| `URLRateLimitError` | transcript_auto_fetcher | `scripts/transcript_auto_fetcher.py` | Line 201 | Experimental |
| `URLSubtitlesNotFoundError` | transcript_auto_fetcher | `scripts/transcript_auto_fetcher.py` | Lines 206, 402 | Experimental |

### Exception Catches  

| Exception Type | Module | File | Location(s) | Purpose |
|---|---|---|---|---|
| `FileEmptyError` | cli | `src/youtube_to_xml/cli.py` | Line 64 | User error handling |
| `FileInvalidFormatError` | cli | `src/youtube_to_xml/cli.py` | Line 67 | User error handling |
| `FileNotFoundError` | cli | `src/youtube_to_xml/cli.py` | Line 54 | System error handling |
| `PermissionError` | cli | `src/youtube_to_xml/cli.py` | Lines 57, 80 | System error handling |

**Notes:**

- **3 YouTube exceptions are proven** in experimental script; **1 is unused** (`URLFormatError`)  
- **YouTube exceptions are unused** in active `src/` code - they exist as infrastructure for future integration

## Logging Implications

**Should these modules have logging?**

**Current state**: PARTIALLY - the architecture supports it but it's not implemented:

- `parser.py`: Pure business logic - appropriately has no logging (follows clean architecture)
- `cli.py`: Boundary layer - could benefit from logging but currently only prints user messages
- `transcript_auto_fetcher.py`: Would greatly benefit from logging for debugging URL operations, rate limits, and failures

**Recommendation**: YES - implement logging strategically:

- Keep `parser.py` logging-free (pure business logic)
- Add logging to `cli.py` for operational visibility
- Essential for YouTube functionality due to network operations and rate limiting
- The unused `logging_config.py` is ready for integration

**Conclusion**: The YouTube exceptions are **proven and tested** in the experimental script, demonstrating they're ready for integration into the main application when YouTube functionality is added.
</exception_summary>

**Current State**:

- `src/youtube_to_xml/logging_config.py` exists but is never imported
- `src/youtube_to_xml/cli.py` handles all user interaction with print statements
- Need logging foundation for future API service development

**Integration Requirements**:

1. **Main application logging** (cli.py): Focus on FileEmptyError, FileInvalidFormatError, and system exceptions that are currently caught
   - Import and initialize `logging_config.py` at start of `main()`
   - Add log statements **alongside** existing print statements (not replacing them)
   - Log ERROR for caught exceptions with context
   - Log INFO for successful XML generation

2. **Experimental script logging**: Focus on YouTube exceptions (URLVideoNotFoundError, URLRateLimitError, URLSubtitlesNotFoundError) that are actively used
   - Make `scripts/transcript_auto_fetcher.py` use same logging approach

3. **Preserve all existing behavior**:
   - Keep every `print()` statement exactly as-is
   - Keep all error messages and success messages unchanged
   - Users see identical console experience

**Example Integration Pattern**:

```python
# KEEP: print(f"❌ Your file is empty: {transcript_path}")
# ADD:  logger.error(f"FileEmptyError: {transcript_path}")
```

**Success Criteria**: CLI behavior identical + log files created when running commands.

Can you analyze what minimal integration is needed to make the `logging_config.py` module functional in the current codebase while keeping the implementation simple and preserving the exact user experience?
