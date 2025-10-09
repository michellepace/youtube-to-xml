**THINKING ON EVALS**

*Possible approach and thinking. Thoughts detailed as a post for collaboration / sound boarding.*

---

<draft>

<post1_intro>
I’m rusty on **Six Sigma** and looking to connect with someone that can criticise my logic. The project is for fun and applying DMAIC lightly. The problem is simple, just unsure of the approach. Rough details in reply.
</post1_intro>

---

<post2_problem>

# Problem

As a learning project, I need to evaluate: is plain text transcript better than XML for chatbot Q&A?

## The Story / Unsure of Approach

A) Started simple: write 30 questions while watching a video, get blind answers from both formats, and pick the winner. Then I worried — what if both win?

B) So I shifted: stop forcing a winner, instead for each response (plain and XML) I give independent yes/no — did this one answer my question? That’s method two.

C) Third pivot: maybe yes/no loses detail, so score each on 1–3 (3=perfect match, 2=some value, 1=failed) still per response, not per pair. Now I can average, bin, or treat it like ordinal data. I’ve got my "golden 30 answers" so I should be quite reliable / repeatable on scoring.

## Choosing Approach by Analysis Data

With yes/no approach: count wins/ties/losses — raw defect rate, binomial process capability (e.g., defect proportion with confidence intervals)

With 1–3 rating approach: I could do capability (not real Cpk — binomial capability instead) or just mean score per type.

| Approach | Description | Strength ✅ | Weakness⚠️ | Best For Analysis |
|----------|-------------|--------------|---------------|-------------------|
| **A: Pick Winner per Pair** | Force-select one winner (or tie) between plain-text and XML responses. | Simple tally of wins/ties; quick to execute. | Ignores cases where both succeed/fail; forces artificial choices. | Basic win rates; not ideal for defects or capability. |
| **B: Yes/No per Response** | Independent binary judgment (yes/no: did it answer?) for each format. | Avoids forced ties; enables binomial defect rates and confidence intervals. | Loses nuance (e.g., partial successes); binary flattens data. | Binomial capability; tallying defects by question type/duration. |
| **C: 1–3 Scoring per Response** | Ordinal scale (3=perfect, 2=partial, 1=fail) against golden answers. | Captures richness; allows averages, binning, or ordinal stats. | Subjective (needs calibration); more time-intensive to score. | Mean scores per type; pseudo-capability (treat as discrete); MSA for LLM. |

## Crossing with Duration

### Different Videos

I also need to cross-video duration (1hr, 5hrs, 10hrs): do 30 questions per transcript (different ones each time), but segment them: e.g., five factual, five sequential, five inference, five cross-ref. So now the segments give commonality to analyse irrespective of transcript / actual questions.

### And/Or within the same Video

Take a 9 hour video and split into 0-1hr, 0-5hrs, 0-10hrs. See if retains capability of questions spread throughout.

## Maybe Later

Finally: can an LLM judge these answers like me? That is, MSA: test if its 1–3 (or yes/no) matches mine before trusting it.

## So full stack

multiple transcripts → 30 questions each → categorised → per-answer score (yes/no or 1–3) → tally by type and total → optional LLM-judge validation.

---///--///------

*I know this is likely overkill. The "project" is mostly for exploring and learning. I will progress to RAG, essentially a "third format" but in that, many more variables on how to do it optimally. This establishes a foundation (one that will be automated).*

---///--///------

</post2_problem>

---

<post3_request>
📊 **My Request:**

If anyone is in a position to have a conversation and give a criticising perspective / sense check, I would really appreciate it. If you became keen to join me in whichever capacity, that would be great too.

</post3_request>
