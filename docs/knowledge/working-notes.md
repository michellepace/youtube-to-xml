# Working Notes / Rough

## Transcripts with no chapters

Currently I reject it, deal with it nicely.

```text
0:21
hey hey hey
0:53
[Music] welcome
2:04
[Music]
```

## Better Format via Evals?

**Evals to test:** prove systamticaly - does XML make claude.ai respond better? Start with evals via Anthropic SDK as indication and segement tests: short, medium, long 15k lines. I suspect claude.ai projects break it with RAG anyhow, but maybe not in chat direct? Try it manual. Thinking ideas:

- Easy: Count chapters
- Easy: Find all details: e.g. tech stack items in [nextjs-tutorial-11hrs.txt](../../transcript_files/nextjs-tutorial-11hrs.txt)
- Think: Compare which gives better Q&A answers an summaries (LLM as a judge and/or Sentence Transformers, Rouge for summary). Try not to human in the loop, but maybe Braintrust UI can make it easier. Mimic claude.ai chat temp at 1.

New format, maybe?:

```xml
<?xml version="1.0" encoding="utf-8"?>
<transcript>
  <metadata>
    <title>Cleaning Cows</title>
    <duration>12:04:27</duration>
    <source>https://youtu.be/fGKNUvivvnc</source>
    <description>A comprehensive guide to cow cleaning techniques. Covers fundamental principles and practical washing methods for proper cow hygiene and care.</description>
  </metadata>
  <chapters>
    <chapter title="Introduction to Cows" start_time="0:02" end_time="15:43">
      <caption timecode="0:02">Welcome to this talk about erm.. er</caption>
      <caption timecode="2:30">Let's start with the fundamentals</caption>
    </chapter>
    <chapter title="Washing the cow" start_time="15:45" end_time="12:04:27">
      <caption timecode="15:45">First, we'll start with the patches</caption>
      <caption timecode="12:00:00">That took a long time</caption>
      <caption timecode="12:04:27">Usually it's much quicker</caption>
    </chapter>
  </chapters>
</transcript>
```

Does it perform better than this (and does this perform better than raw transcript):

```xml
<?xml version='1.0' encoding='utf-8'?>
<transcript>
  <chapters>
    <chapter title="Introduction to Cows" start_time="0:02">
      0:02
      Welcome to this talk about erm.. er
      2:30
      Let's start with the fundamentals</chapter>
    <chapter title="Washing the cow" start_time="15:45">
      15:45
      First, we'll start with the patches
      11:59:59
      That took a long time
      12:04:27
      Usually it s much quicker</chapter>
  </chapters>
</transcript>
```

Do these factors impact LLM comprehension: XML tag names, white space (remove pretty formatting) - impacts cost if big?
