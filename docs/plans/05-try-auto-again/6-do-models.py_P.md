I need you to be my chief architect who loves "good system design". I am a product manager who loves delivering incremental pieces of value (at low risk).

**The end goal:** Integrate my experimental script `scripts/url_to_transcript.py` into my main application so that I can delete the stand-alone script.

**Key Files:**
- `PROJECT_INDEX.json`: complete project index map, including all `.py` modules and current function signatures including pytest tests - for understanding and navigating project at a glance.
- `README.md` functionality and i/o of the application
- `scripts/url_to_transcript.py`: experimental script for future integration ("URL based method" for URL sources)
- `src/file_parser.py`: ("FILE based method for FILE sources)
- `next.js`: my unvalidated next ideas yet to be arranged in incremental delivery of value

**Objectives now:**
1. Use key files to ground in current source code project state for relevant and accurate context
2. Review the unvalidated notes I have in `next.md`
3. Evaluate and verify if my simple next steps for value is a valid, sound, and pragmatic approach in `<next_steps_value>` tags. And if something critical is missing. Confirm what I need to do with sound pragmatism grounded in current code.
4. For the verified next steps of value: help me know how to apply TDD as per the rest of my application

<next_steps_value>
1. Refactor `src/file_parser.py` so that it has a `VideoMetadata` data class too. Ensure that it sets all attributes to "". As in standardise it to how the experimental script does it. - commit this value.
2. Writes tests to create `src/youtube_to_xml/models.py` as detailed in `next.md` lines `14-57`. Then write failing or fix existing tests (IF this is needed only) to drive refactoring of `file_parser.py` to use `src/youtube_to_xml/models.py`.- commit this value
3. Refactor `scripts/xml_to_transcript.py` to use `src/youtube_to_xml/models.py` so that it aligns how `file_parser.py` does it (start with failing tests or new ones if needed). - commit this value
4. Raise a PR (continue remaining steps in a new branch)
</next_steps_value>

Understand my goal and objectives. Please carefully analyse and evaluate all sources provided. Start with the PROJECT_INDEX.json as it is an efficient means to understand and navigate. Connect my goals and objectives to what you have analysed. Then carefully and deeply think about my next steps of value in order to find the gaps, bad logic, etc. and recommend a path forward.