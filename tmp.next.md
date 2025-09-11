# Development Notes

## Architecture Insights Discovered 🔍

### Major Bug Identified: URLRateLimitError Double-Printing
**Issue**: URLRateLimitError is printed twice in the CLI script:
1. First: `print(f"❌ {e}", file=sys.stderr)` (in exception handler)
2. Then: Exception is re-raised and caught again
3. Second: `print(f"\n❌ Error: {e}")` (in main exception handler)

**Result**: Rate limit errors appear twice to users, while all other errors appear once.

**All other exceptions**: Only printed once to stdout in main handler.

### stdout vs stderr Usage Analysis
**Current inconsistent behavior**:
- 99% of output (including most error messages): Goes to stdout
- Only URLRateLimitError: Goes to stderr (due to the bug above)

**In tests**: Currently combine `result.stdout + result.stderr` to catch all output

### Future Service Architecture Considerations
**Current**: CLI script mixes business logic with presentation (formatting errors)
**Future**: When refactoring to service for Next.js app, should separate:
- **Core Service**: Just raises exceptions, no formatting
- **CLI Edge**: Formats exceptions for terminal users  
- **API Edge**: Formats exceptions for JSON responses

**Testing Strategy Should Evolve**:
- Current: Tests CLI presentation (stdout/stderr output)
- Better: Test business logic (exception types and core messages)
- Future: Separate CLI presentation tests from service logic tests

## Next Steps for Future Sessions 🚀

### Immediate Technical Debt
1. **Fix URLRateLimitError Double-Printing Bug**
   - Remove the early stderr print in exception handler
   - Let all errors flow to main handler for consistent presentation
   - OR decide on consistent stderr vs stdout strategy

2. **Standardize stdout vs stderr Usage**
   - Decide if errors should go to stderr or stdout
   - Apply consistently across all error types
   - Update tests accordingly

### Architectural Improvements (Lower Priority)
3. **Consider Service Extraction**
   - Extract core YouTube processing logic from CLI script
   - Separate business logic from presentation concerns
   - Enable reuse in future API/service contexts

4. **Update Testing Strategy**
   - Consider testing exception types directly instead of CLI output
   - Prepare for service-oriented testing approach

## Files Changed in This Session
- `tests/test_exceptions_ytdlp.py`: Complete rewrite with proper assertions
- `tests/test_end_to_end.py`: Cleaned up, removed exception testing
- `tests/test_exceptions.py`: Updated with realistic yt-dlp error patterns

## Context for Next Session
The test reorganization is complete and working. The main value is eliminating test duplication and creating clear separation of concerns. The bug discovery and architecture insights are bonus findings that can be addressed when convenient.