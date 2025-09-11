# Development Notes

## Architecture Insights Discovered 🔍

### stdout vs stderr Usage Analysis
**Current behavior**:
- All output (including error messages): Goes to stdout consistently

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
1. **Standardize stdout vs stderr Usage**
   - Decide if errors should go to stderr or stdout
   - Apply consistently across all error types
   - Update tests accordingly

### Architectural Improvements (Lower Priority)
2. **Consider Service Extraction**
   - Extract core YouTube processing logic from CLI script
   - Separate business logic from presentation concerns
   - Enable reuse in future API/service contexts

3. **Update Testing Strategy**
   - Consider testing exception types directly instead of CLI output
   - Prepare for service-oriented testing approach

## Files Changed in This Session
- `tests/test_exceptions_ytdlp.py`: Complete rewrite with proper assertions
- `tests/test_end_to_end.py`: Cleaned up, removed exception testing
- `tests/test_exceptions.py`: Updated with realistic yt-dlp error patterns

## Context for Next Session
The test reorganization is complete and working. The main value is eliminating test duplication and creating clear separation of concerns. Architecture insights were identified that can be addressed when convenient.