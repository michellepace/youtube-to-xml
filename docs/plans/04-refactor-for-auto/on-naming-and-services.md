The intention of the CLI is to use either a transcript.txt argument or a <youtube_url> argument. From a API service perspective as mentioned in @README.md, in my Next.js app I plan to give uses the first option of simply inputting the URL and as a fallback (e.g. rate limiting) they can upload a transcript file (copied from the YouTube page and pasted into a file).

Please review each of my questions:

<questions>
## Q1. Module Renaming(?)
Since `parser.py` only parses contents of files.
1. renamed `parser.py` to `file_parser.py`
2. Within the module renamed function `parse_transcript` to `parse_transcript_text`
3. I ran all tests and they are passing and ran the CLI too with a `transcript.txt` file

I am undecided if this change TO help me decide what to use:

1. Please map out the module flow of running CLI both by file and then youtube_url arguments.
   - First with the current names as detailed in @PLAN-auto.xml and @REVIEW.md
   - Then with the new names I have suggested
   - Review both options and provide a recommendation and state your reasoning

## Q2. API Services: anything currently implied?

In terms of this being an API service and what is exposed currently

- Is there any information in @README.md that details this already or implied by our current code?
- Does the @PLAN-auto.xml detail anything with regards to this?

## Q3. APPI services: what makes sense to expose?

What makes sense to expose in the API, what is clearest and best practice?

- A) Does it makes sense to have one exposed service, where the logic is within the code?
- B) Does it make sense to have two exposed services, one for files and for youtube_url?
- What is the impact of either choice (A) and (B)?
- What do you recommend?
</questions>

Then deeply think about my questions and answer each in reference to the files mentions and this code base. Consider all in light of the current direction of PLAN-auto.md.

Provide a well structured answer to each of my questions. Then include a final summary of your recommendations with reasoning.
