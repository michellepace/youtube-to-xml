# Design A Unified Main Application

## Your Task
Create an architectual design ("Good System Design" as previously discussed) that meets the objective. Then save to root file `design.md`

**Analyse in addition to current conversation context:**
- Experimental script: `scripts/transcript_auto_fetcher.py`
- Example output currently (same YouTube video)
   - File method: `uv run youtube-to-xml how-claude-code-hooks-save-me-hours-daily.txt` → Output: `how-claude-code-hooks-save-me-hours-daily.txt.xml`
   - URL method: `uv run scripts/transcript_auto_fetcher.py "https://www.youtube.com/watch?v=Q4gsvJvRjCU"` → Output: `how-claude-code-hooks-save-me-hours-daily.xml`
- Analyse additional repo source files as needed: e.g., `parser.py` (better named "file_parser.py")

Thoroughly address all sections below to meet the objective.

***However, Ask me questions if needed before you begin to confirm and clarify understanding (please number so it’s easy for me to answer).***

## Objective
Integrate the experimental script's YouTube transcript functionality into the main application using clean architecture. The experimental script will be deleted after integration.

## Requirements
1. **Unified CLI**: Support both file and YouTube URL inputs for XML transcript generation
2. **Future-ready**: Architecture must support future API endpoints without modification
3. **Clean design**: Prioritize simplicity, clarity, and good system design principles
4. **Open to refactoring**: Willing to restructure significantly for optimal architecture

## Technical Context
- Two distinct sources (file vs YouTube) require different parsing logic
- Each source has substantial, specialized code that should remain in separate modules  
- Once parsed, both sources should produce identical data structures for downstream processing
- The experimental script proves the YouTube functionality works but won't be copied directly

## Key Question
Should we force both sources into one unified data structure early, or allow source-specific structures that converge at a common interface? The goal is balancing simplicity with clean separation of concerns.

## Architectural Points to Consider

<architectual_points>

The main application will support two transcript sources (file and YouTube URL) through a unified architecture using the Adapter Pattern.

1. **CLI uses explicit flags**: `--file <path>` and `--url <youtube_url>` to select source adapter (no auto-detection)

2. **Output XML format identical for both sources**:
   - Same XML structure and chapter content  
   - Only metadata attributes differ:
     - File source: All attributes empty (`video_title=""`, `upload_date=""`, `duration=""`, `video_url=""`)
     - YouTube source: All attributes populated with actual values
   - Example outputs from same video:
     - File: `youtube-to-xml --file how-claude-code-hooks-save-me-hours-daily.txt`
     - YouTube: `youtube-to-xml --url https://www.youtube.com/watch?v=Q4gsvJvRjCU`
     - Both produce identical chapter structure, only metadata values differ

3. **Two sources only**: FileSource and YouTubeSource (no other platforms)

4. **Adapter pattern**: Each source adapter implements `fetch() -> tuple[list[Chapter], Metadata]`

5. **Metadata handling**: Four attributes always present in XML (video_title, upload_date, duration, video_url); YouTube populates values, file source uses empty strings

6. **yt-dlp as required dependency**: Include in main dependencies (not optional)

7. **Error handling**: Use existing exceptions (URLRateLimitError, URLVideoNotFoundError, FileEmptyError) with simple failure - no retry logic

8. **Output behavior**: Both sources save to current directory with sanitized filename

9. **Parallel parsers with separated concerns**: 
   - **Acquisition**: Each source handles its own data acquisition (file reading vs YouTube downloading)
   - **Processing**: `parser.py` (unchanged) handles file transcripts; new `youtube_parser.py` handles YouTube transcripts
   - Both independently transform acquired data into Chapter objects
   - This separation enables clean testing and future API reuse

10. **API-ready design**: Stateless parsers and clean separation enable future API endpoints to reuse same source adapters and parsers

</architectual_points>

## Request
Design the architecture for integrating these two sources into the main application. Ask clarifying questions if needed (numbered for easy response).

Save your design into `design.md`.