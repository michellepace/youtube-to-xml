# Design A Unified Main Application

I need your help on how to design the existing main application so that it has the ability of the experimental script. I will then delete the script. Users will be able to have YouTube transcripts structured into XML through either input source. And again via CLI and later as an API service.

**Please analyse the experimental script:** `scripts/transcript_auto_fetcher.py`

It is important that the main application abides to good system design as you explained in your `report.md`. I am open to significant refactoring as clarity and simplicity is important to me. 

The commonality I see is that it's simply 2 different sources, from file and now from URL. However, how those sources are structured into their “data classes” is significantly different (and the code quite large for each), I feel these should be separate modules. 

I am unsure how we can standardise into one “data class” or “structure” and if we should attempt to avoid duplication. Or if it is fine for duplication for each source as a balance of simplicity. 

But once this has been done, I see that the rest of the application can work in the same manner independent of source. And that's one aspect of how we can achieve simplicity 

So I need you to think very deeply of how to do this as I want to delete the script And has a functionality in the main application It's an experimental script, and I don't intend to copy and paste the code into the main application. It's just the proven ability that I want in the new application.

Please also consider these losely proposed archtectual points:

<architectual_points>

## Architectural Points to Consider for Unified Application

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

Again, I want to keep a really good system design that is clean and as elegant and simple as practical. I am open to a significant refactoring if needed. 

Can you please help me how to do this? 

Save your design into `design.md` **HOWEVER Ask me questions if needed before you begin to confirm and clarify understanding (please number so it’s easy for me to answer).**