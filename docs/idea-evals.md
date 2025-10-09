# Thinking on Evals

*Possible approach, extensive but a learning experience. Thoughts detailed below structured as a post to community for collaboration / sound boarding.*

---

<draft>

<post1>
Hello. I am a Six Sigma Black Belt from 10 years ago. I’m rusty and looking to connect with people that can give me perspective and criticise my logic. Work with me on this "play DMAIC project" if you are keen yourself. The problem is very simple (in reply).
</post1>

<post2>
# Problem
As a personal project, I need to evaluate: is plain text transcript better than XML for chatbot Q&A?

## The Story / Unsure of Approach

A) Started simple: write 20 questions while watching a video, get blind answers from both formats, and pick the winner. Then I worried — what if both win?

B) So I shifted: stop forcing a winner, instead for each response (plain and XML) I give independent yes/no — did this one answer my question? That’s method two.

C) Third pivot: maybe yes/no loses detail, so score each on 1–3 (3=perfect match, 2=some value, 1=failed) still per response, not per pair. Now I can average, bin, or treat it like ordinal data. I’ve got my "golden 20 answers" so I should be quite reliable / repeatable on scoring.

## Choosing Approach By Analysis Strength / Data

With yes/no approach: count wins/ties/losses—raw defect rate, binomial process capability (e.g., defect proportion with confidence intervals)

With 1–3 rating approach: I could do capability (not real Cpk—binomial capability instead) or just mean score per type.

## Crossing with Duration

### Different Videos

I also need to cross-video duration (1hr, 5hrs, 10hrs): do 20 questions per transcript (different ones each time), but segment them: e.g., five factual, five sequential, five inference, five cross-ref. So now the segments give commonality to analyse irrespective of transcript / actual questions.

### And/Or within the same Video

Take a 9 hour video and split into 1hr, 5hrs, 10hrs. See if retains capability of questions spread throughout.

## Maybe Later

Finally: can an LLM judge these answers like me? That is, MSA: test if its 1–3 (or yes/no) matches mine before trusting it.

## So full stack

multiple transcripts → 20 questions each → categorised → per-answer score (yes/no or 1–3) → tally by type and total → optional LLM-judge validation.
</post2>

<post3>
Is anyone keen to connect, or work on this with me as a learning experience from a Six Sigma perspective? I don’t have Minitab, just Python. I could get it for 14-days, possibly 30 if you preferred it. Or just to give a criticising perspective / sense check, I would really appreciate it.

On a final note: I know this may appear as overkill. It is partly for learning and partly because I am progressing toward RAG to reduce costs. This establishes a foundation (one that will be automated).
</post3>

<post4_appendix>

## Appendix: Comparison of Scoring Approaches (A, B, C)

Compares the three approaches based on our discussion, focusing on strengths, weaknesses, and analysis fit.

| Approach | Description | Strengths ✅ | Weaknesses ⚠️ | Best For Analysis |
|----------|-------------|--------------|---------------|-------------------|
| **A: Pick Winner per Pair** | Force-select one winner (or tie) between plain-text and XML responses. | Simple tally of wins/ties; quick to execute. | Ignores cases where both succeed/fail; forces artificial choices. | Basic win rates; not ideal for defects or capability. |
| **B: Yes/No per Response** | Independent binary judgment (yes/no: did it answer?) for each format. | Avoids forced ties; enables binomial defect rates and confidence intervals. | Loses nuance (e.g., partial successes); binary flattens data. | Binomial capability; tallying defects by question type/duration. |
| **C: 1–3 Scoring per Response** | Ordinal scale (3=perfect, 2=partial, 1=fail) against golden answers. | Captures richness; allows averages, binning, or ordinal stats. | Subjective (needs calibration); more time-intensive to score. | Mean scores per type; pseudo-capability (treat as discrete); MSA for LLM. |

</post4_appendix>

</draft>
