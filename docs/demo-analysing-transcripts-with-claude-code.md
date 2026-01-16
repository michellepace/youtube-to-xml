---
Title: Analysing YouTube Transcripts with Claude Code
Description: Demonstrates Claude Code's ability to analyse and extract structured information from YouTube transcripts
---

To replicate this conversation, use the [README.md](../README.md) and run `youtube-to-xml https://www.youtube.com/watch\?v\=NAV3G9oFPC0` which creates the transcript file:

```bash
$ youtube-to-xml https://www.youtube.com/watch\?v\=NAV3G9oFPC0

🎬 Processing: https://www.youtube.com/watch?v=NAV3G9oFPC0
✅ Created: design-systems-that-make-apps-look-real-live.xml
```

## Question 1 (too big)

> **Q1.** Please analyse YouTube transcript `day1_design-systems-that-make-apps-look-real-live.xml` and tell me what is the name of the application he is building and the folder / directory he creates in Cursor?

<claudecode_answer_q1>

*[The file is too big for Claude Code (> 25,000 tokens). Summarising the file per chapter will lose timestamps. Anthropic API holds 200,000 tokens in context, so we still wouldn't have to use RAG in an app.]*

```text
Read(~/projects/nextjs/day1_design-systems-that-make-apps-look-real-live.xml)                                              
  ⎿  ❌ Error: File content (63231 tokens) exceeds maximum allowed tokens (25000). Please use offset and limit parameters to read specific portions of the file, or use the GrepTool to search for specific content.
```

*[But still useful for now. Claude Code goes on to read selected lines only]:*

● Based on the transcript:

Application name: med pdf (also referred to as "med PDF"). Initially (around 46:07) he considered naming it "translate PDF", but later in the video (around 1:39:08) when starting fresh, he settles on "med pdf": *"Okay, cd med pdf ls. There's nothing in here. Okay, cool. So I just called it med pdf."* He creates this folder in his workspace directory where he keeps all his apps, then opens it in Cursor to begin building the project.

</claudecode_answer_q1>

## Question 2: Identify Chapters

> **Q2.** Please identify all the chapters, what are they?

<claudecode_answer_q2>

● Here are all 30 chapters from the transcript:

```text
+----+----------+------------------------------------------------------------------+
| #  | Time     | Chapter Title                                                    |
+----+----------+------------------------------------------------------------------+
| 1  | 0:00     | The differentiator today is taste and experience                 |
| 2  | 0:35     | Exploring Cult UI interactions and landing pages                 |
| 3  | 1:05     | Introducing blocks.so and the shadcn UI ecosystem                |
| 4  | 2:13     | How to use AI agents with design systems                         |
| 5  | 4:11     | Showcasing a directory of shadcn components                      |
| 6  | 5:21     | Demonstrating an interactive design that takes over the screen   |
| 7  | 6:01     | Explaining how to use props to modify components                 |
| 8  | 8:14     | Showcasing a distorted glass morphing surface                    |
| 9  | 9:35     | Demonstrating animated dot pattern backgrounds                   |
| 10 | 11:38    | Introducing the PDF translation app idea                         |
| 11 | 14:41    | Detailing the full tech stack: Convex, Clerk, and Stripe         |
| 12 | 16:28    | Using an architect skill in Claude to start planning             |
| 13 | 21:46    | Answering a user's question about using Convex over Supabase     |
| 14 | 29:43    | Reviewing the AI-generated architecture confirmation             |
| 15 | 32:20    | Explaining the "Yap to App" framework                            |
| 16 | 35:41    | Reviewing the full architecture specification document           |
| 17 | 41:53    | Visualizing the data flow and state machine diagrams             |
| 18 | 45:08    | Transitioning to Cursor to begin building the application        |
| 19 | 51:40    | Prompting the Cursor agent to break the work into phases         |
| 20 | 58:34    | Starting the Next.js project setup and encountering issues       |
| 21 | 1:05:33  | Configuring the environment variables for Clerk                  |
| 22 | 1:08:23  | Assigning all of Phase 2 to the AI agent                         |
| 23 | 1:10:31  | The AI agent begins integrating Clerk and Convex                 |
| 24 | 1:20:22  | Introducing the 'Start My AI' cohort for building apps           |
| 25 | 1:37:24  | Starting a fresh project setup from the command line             |
| 26 | 1:43:28  | Giving a quick terminal tutorial on pipe and grep                |
| 27 | 1:48:08  | Finalizing the Next.js and shadcn UI setup                       |
| 28 | 1:56:42  | Manually initializing the Convex database project                |
| 29 | 2:00:28  | Explaining why he uses Clerk for authentication                  |
| 30 | 2:08:23  | Kicking off the AI agent for the full Clerk/Convex integration   |
+----+----------+------------------------------------------------------------------+
```

The video covers the complete journey from discussing design systems and UI libraries (shadcn, Cult UI, blocks.so) through to building a PDF translation app using Next.js, Convex, Clerk, and Stripe with AI-assisted development in Cursor.

</claudecode_answer_q2>

## Question 3: Target Chapters

*[This is possible because the transcript is structured into XML chapters, it's easy for Claude Code just to get that chapter.]*

> Analyse chapter 10 and 11. Please summarise each, so I can understand what the app does firstly. Then the tech stack. Output well structured.

<claudecode_answer_q3>

### Chapter 10: Introducing the PDF Translation App Idea (11:38)

**The Problem**

- A neighbour had a stroke whilst travelling abroad
- She had medical documents in French that needed translating to English
- Professional translation quote: $4,000-$5,000 and one week turnaround
- Existing tools (Google Translate, etc.) failed to preserve formatting for charts and medical data

**The Solution**

The presenter translated the 20-page medical document in 5 minutes using AI, preserving all charts and formatting. The doctors were able to use it to make healthcare decisions.

**The App Concept: med pdf**

```text
+------------------------+--------------------------------------------------------------+
| Aspect                 | Details                                                      |
+------------------------+--------------------------------------------------------------+
| Core function          | AI-powered PDF translation that preserves formatting         |
|                        | (charts, tables, layouts)                                    |
+------------------------+--------------------------------------------------------------+
| Target users           | People needing document translation, especially              |
|                        | medical/legal documents                                      |
+------------------------+--------------------------------------------------------------+
| Distribution strategy  | ChatGPT Store integration - users can attach PDFs and        |
|                        | translate directly                                           |
+------------------------+--------------------------------------------------------------+
| Market potential       | Access to 800 million ChatGPT users                          |
+------------------------+--------------------------------------------------------------+
| Key differentiator     | Reliable formatting preservation where other tools fail      |
+------------------------+--------------------------------------------------------------+
```

**Use Cases Identified**

- Medical documents (hospital records, bills, charts)
- Foreign language documents for people travelling abroad
- Any PDF requiring accurate translation with layout integrity

---

### Chapter 11: Detailing the Full Tech Stack (14:41)

**Tech Stack Overview**

```text
+--------------------+------------+--------------------------------------------------+
| Layer              | Technology | Purpose                                          |
+--------------------+------------+--------------------------------------------------+
| Frontend           | Next.js    | React framework for the web application          |
+--------------------+------------+--------------------------------------------------+
| Database           | Convex     | Real-time database with built-in backend         |
|                    |            | functions                                        |
+--------------------+------------+--------------------------------------------------+
| Authentication     | Clerk      | User sign-up, login, and account management      |
+--------------------+------------+--------------------------------------------------+
| Payments           | Stripe     | Payment processing (using Convex-Stripe          |
|                    |            | component)                                       |
+--------------------+------------+--------------------------------------------------+
```

**Why This Stack?**

```text
+---------------+------------------------------------------------------------------+
| Consideration | Reasoning                                                        |
+---------------+------------------------------------------------------------------+
| Scalability   | Built to handle up to 800 million users from day one             |
+---------------+------------------------------------------------------------------+
| Security      | Enterprise-grade auth (Clerk) and database (Convex)              |
+---------------+------------------------------------------------------------------+
| Speed         | Stripe integration via Convex component takes ~10 minutes        |
+---------------+------------------------------------------------------------------+
| Agentic       | Stack is well-documented and AI-friendly for rapid development   |
| coding        |                                                                  |
+---------------+------------------------------------------------------------------+
```

**Key Integration**

The presenter mentions a Stripe starter component by Ross Mickey that integrates payments with Convex quickly - handling payment initiation, database queries, and webhook processing in a streamlined way.

</claudecode_answer_q3>

## Question 4: Dig For A Complete Answer

*[Claude's diligence could be improved via prompt engineering later]*

> Review the chapter titles you have output above. Are there any tech stack items you have not mentioned?

<claudecode_answer_q4>

Looking back at the chapter titles, I missed two important items:

```text
+-------------+------------------+------------------------------------------------------+
| Missed Item | Chapters         | Role                                                 |
+-------------+------------------+------------------------------------------------------+
| shadcn UI   | Ch. 3, 5, 27     | UI component library - provides pre-built,           |
|             |                  | customisable React components                        |
+-------------+------------------+------------------------------------------------------+
| Cursor      | Ch. 18, 19       | AI-powered code editor - used for agentic            |
|             |                  | coding/development                                   |
+-------------+------------------+------------------------------------------------------+
```

Additionally, from the tooling/workflow perspective:

```text
+-------------+------------------+------------------------------------------------------+
| Tool        | Chapters         | Role                                                 |
+-------------+------------------+------------------------------------------------------+
| Claude      | Ch. 12           | AI assistant for architecture planning (using        |
|             |                  | "architect skill")                                   |
+-------------+------------------+------------------------------------------------------+
| blocks.so   | Ch. 3            | Directory of shadcn-based templates and components   |
+-------------+------------------+------------------------------------------------------+
| Cult UI     | Ch. 2            | UI interaction library for landing pages             |
+-------------+------------------+------------------------------------------------------+
```

**Updated Tech Stack**

```text
+-------------------+--------------------------------------------------------------+
| Layer             | Technology                                                   |
+-------------------+--------------------------------------------------------------+
| Frontend          | Next.js                                                      |
+-------------------+--------------------------------------------------------------+
| UI Components     | shadcn UI (+ Cult UI, blocks.so for templates)               |
+-------------------+--------------------------------------------------------------+
| Database          | Convex                                                       |
+-------------------+--------------------------------------------------------------+
| Authentication    | Clerk                                                        |
+-------------------+--------------------------------------------------------------+
| Payments          | Stripe                                                       |
+-------------------+--------------------------------------------------------------+
| Development Tools | Cursor (AI code editor), Claude (architecture planning)      |
+-------------------+--------------------------------------------------------------+
```

</claudecode_answer_q4>
