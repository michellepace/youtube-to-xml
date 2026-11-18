# Skip the TDD ritual, keep strong tests

*This is a rewrite of the report "TDD with AI coding agents 2026". It uses the same research, but it answers a narrower question. The question is not "should I drop tests?" It is "can I skip TDD, and go straight to sociable tests plus end-to-end, property and differential tests?"*

## The short answer ✅

You want to stop one practice and keep everything else. The practice to stop is the **TDD ritual**. In this ritual, the agent writes a failing unit test, then writes code to make it pass, in many small cycles. With Claude, this ritual gives you a lot of scaffolding, and you must refactor it into sociable tests anyway.

What you plan instead is to go **straight to sociable tests at the seams**. You also plan to add the three test types from Anthropic's verification article: **end-to-end tests, property tests and differential tests**.

The 2026 evidence supports this principle. When an agent follows the TDD ritual, quality does not clearly improve, but the cost goes up by three to eight times. The order of the tests is not what makes agent work reliable. What makes it reliable is a check that is **independent of the agent** and that **the agent cannot change**.

There is one exception and one risk. The exception is bugs: **reproduce a bug before you fix it**. This is the part of Geoff's advice that is correct. The risk is that tests the agent writes after the code can copy the mistakes in that code. Your end-to-end, property and differential tests, plus examples that you own, are the solution to that risk.

## What the terms mean

| Term | Plain meaning | Example in `youtube-to-xml` |
|---|---|---|
| **TDD ritual** (red/green) | Write a test and see it fail (red). Write code until it passes (green). Repeat in small steps. | Leftovers such as `test_parse_youtube_url_accepts_one_parameter`, which checks the shape of a function, not its behaviour |
| **Sociable test** | A test that runs code with its real collaborators, not with fakes ("mocks") | A test that gives `parse_transcript_file()` a full transcript and checks the result |
| **Seam** | A public entry point where you can test behaviour without access to internals | `parse_transcript_file()`, `parse_youtube_url()` and the `youtube-to-xml` command |
| **End-to-end (E2E) test** | A test that runs the real program as a user does, and checks the real output | `tests/test_end_to_end.py`, which compares the XML output with saved "golden files" |
| **Property test** | A test that states a rule that must always be true. A library generates thousands of inputs to try to break the rule. | Not in the repo yet. Example: seconds → timestamp → seconds always gives the same number |
| **Differential test** | A test that gives the same input to two versions, and compares the outputs | `test_url_vs_file_equivalent_output`, which compares XML from a URL with XML from a `.txt` file |

## Why the TDD ritual adds little with agents 📉

Birgitta Böckeler of Thoughtworks made the most direct comparison in 2026. Böckeler gave an agent small, medium and large tasks, with TDD instructions and without them. A separate model then ranked the results without knowing which was which. The result was "**no clearly discernable difference**" in quality. More than once, the version without TDD ranked slightly higher.

The cost was not equal. The TDD runs used **8.5, 2.96 and 4.89 times the tokens** for the small, medium and large tasks. Böckeler now writes: "I personally have stopped telling my coding agents to write tests first." The experiment was small and informal, and the article says so ([Böckeler, Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)).

A much larger academic study agrees. Chen and colleagues examined **5,000 agent runs by six models** on a standard bug-fix benchmark. They told four models to write tests, or not to write tests. The number of fixed tasks changed by only **0 to 13 out of 500** for each model. That difference was not statistically significant, but token use went up a lot for three of the four models. The agents' test files also contained more print statements than assertions. The agents used tests as a scratchpad, not as a judge ([arXiv 2602.07900](https://arxiv.org/abs/2602.07900)).

Google studied 120 real internal bugs. It compared strict TDD, tests after the fix, and a "Freeform" mode where the agent chose its own order. **Freeform gave the best fixes.** Strict TDD gave better reproduction tests, but not better fixes ([arXiv 2601.19066](https://arxiv.org/html/2601.19066v1)). Böckeler also saw that TDD instructions "actively work against" design before coding starts. The agent locks in whatever shape its first test implies.

Not everyone agrees, and the voices for TDD are reputable. The table shows the main 2026 positions.

| Who | 2026 position, in brief | Source |
|---|---|---|
| Birgitta Böckeler (Thoughtworks) | Has stopped telling agents to write tests first. Says the role of TDD is "significantly smaller than pre-GenAI". | [martinfowler.com, Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html) |
| Matteo Vaccari (Thoughtworks) | Human-owned customer tests are the primary contract. Test behaviour, not implementation. | [martinfowler.com, Nov 2026](https://martinfowler.com/articles/tests-as-data.html) |
| Dave Farley | Humans must write executable specifications. Run the tests yourself, and hide some from the AI. | [Tessl, Aug 2026](https://tessl.io/blog/vibe-coding-is-not-the-best-we-can-do) |
| Anthropic | "Give Claude something it can run that comes back pass or fail." Its newest team post prefers end-to-end checks and does not mention TDD. | [Claude Code docs](https://code.claude.com/docs/en/best-practices); [claude.dev, Nov 2026](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/) |
| OpenAI | Ask Codex to "create tests when needed" and to say what done means. No red/green rule. | [Codex best practices](https://learn.chatgpt.com/guides/best-practices) |
| Kent Beck | Still tries to keep agents in small steps with tests. "AI wants big batches, trust wants small verified steps." | [Oct 2026](https://newsletter.kentbeck.com/p/trust-is-the-binding-constraint) |
| Simon Willison | "'Use red/green TDD' is a pleasingly succinct way to get better results out of a coding agent." | [Feb 2026](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/) |
| Cursor | Commit the tests first, then tell the agent "not to modify the tests". | [Jan 2026](https://cursor.com/blog/agent-best-practices) |

Nobody in this group says that tests are unimportant. The disagreement is about **who writes the test, and at what level**.

Martin Fowler gives the strongest reason to write a test first. It "encourages us to think about the interface without coupling it to an implementation" ([Fowler, Jan 2026](https://martinfowler.com/articles/convo-what-how.html)). You can keep this benefit without the ritual. Before work starts, write down examples of correct output at the seam: a sample transcript and the XML you expect. That is a decision about what "done" means. It is not a unit test, and it creates no scaffolding.

## The real risk: tests that copy the code ⚠️

When the agent writes the code first and the tests after, there is a known problem. The tests can describe what the code *does*, not what it *should* do. Vaccari writes that "the AI will write tests that confirm the current implementation, including any bugs it may contain" ([Vaccari](https://martinfowler.com/articles/tests-as-data.html)).

Research measures this effect. Tests written after faulty code found **14%** of the faults. Tests written independently found **25%** ([arXiv 2607.05139](https://arxiv.org/abs/2607.05139)). Another study found that an agent's test and its fix can both be wrong and still pass together. The authors call this "**test–fix error coupling**" ([arXiv 2607.19843](https://arxiv.org/abs/2607.19843)). SpecBench found that every frontier agent passes all the tests it can see, but still fails tests that are hidden from it ([arXiv 2605.21384](https://arxiv.org/abs/2605.21384v1)).

TDD does not solve this problem. Böckeler found that writing the test first "doesn't reliably prevent" tests that mirror the implementation. The solution is **independence**. A check is strong when it comes from the requirement, when someone other than the coder writes it, and when the coder cannot edit it. Anthropic states the rule directly: "**If a change can modify the check that judges it, the check is broken**" ([claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/)).

This is why your set of four test types works well. Sociable tests at the seams remove the coupling to internals, but the agent still writes them, so they are not independent. The other three types add the independence, as the next section shows.

## Your four test types in this repo 🧪

| Test type | Why it resists agent bias | Status in `youtube-to-xml` | Next step |
|---|---|---|---|
| **Sociable tests at the seams** | They test behaviour through public functions, so a refactor does not break them | Good in `test_file_parser.py`, which uses only the public function. Weak in `test_url_parser.py`, which imports nine private names. | Test the URL logic through a public function. Delete the tests that check function shape. |
| **End-to-end tests** | "Either the whole feature works or it doesn't." You own the golden files, not the agent. | Present in `test_end_to_end.py`, with golden files in `example_transcripts/` | Add a `verify` skill. Protect the golden files. |
| **Property tests** | A library generates the inputs, so the edge cases do not share the agent's bias | Absent | Add Hypothesis tests for `time_utils` and the parsers |
| **Differential tests** | The old system, or a second path, is the judge | Present in `test_url_vs_file_equivalent_output` | Use the same method for any future rewrite, for example a TypeScript port |

**Sociable tests.** The URL parser tests import private functions for a reason. The public function `parse_youtube_url()` downloads from YouTube, which is slow and unreliable. A better design separates the download from the processing. Then a public function can take saved sample data and return a `TranscriptDocument`. You can test that function quickly at a seam, with no private imports.

**End-to-end tests.** The Claude Code team says: "If you have to focus on one test type, pick end-to-end." These tests "are difficult to fool" ([claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/)). Your golden files already do this job. A `verify` skill makes it a habit: Claude runs the real command on each sample transcript and compares the output before every commit.

**Property tests.** These are the most underused tool for someone in your role. Anthropic values them because their edge cases "aren't created with the same bias as the agent that created the original code". Anthropic's own researchers used Hypothesis to find real bugs in NumPy and other popular packages ([Anthropic, Jan 2026](https://www.anthropic.com/research/property-based-testing)). In one benchmark, an explicit instruction to use Hypothesis raised the bug-finding of Opus 4.8 by **41.9 points**. The gain depends on the model, and ranged from −8 to +42 points ([PBT-Bench](https://arxiv.org/html/2605.15229)).

For this repo, good rules are: a timestamp converts to seconds and back with no change; no transcript line is lost; chapter start times always increase; the output is always valid XML. **Your job is to name the rules. Claude's job is to write the code.**

**Differential tests.** Your file-versus-URL test is already one. It gives the same video to two paths and compares the chapters. It also ignores one expected difference: the file version has empty video details. Anthropic calls such differences "approved changes", and recommends a list of them. This method becomes very useful if you ever rewrite the tool. Run the old and new versions on many transcripts, and compare the XML.

## The one place to test first: bugs 🐛

Geoff said: "Claude Opus will very happily write a solution to a non-trivial problem that doesn't actually solve the problem if you don't have it confirm the problem before it starts." **This is correct, and it agrees with your principle.**

Other sources say the same thing. Kent Beck describes how the agent ends up "claiming success even though the code doesn't work at all" ([Beck, Apr 2026](https://newsletter.kentbeck.com/p/genie-tarpit)). Anthropic's documentation says: "Claude stops when the work looks done." Its example prompt for a bug is "write a failing test that reproduces it, then fix it" ([Claude Code docs](https://code.claude.com/docs/en/best-practices)). One study gave agents bugs that were already fixed. The agents went straight to the source code and wrote patches. A simple reproduction would have shown that there was nothing to fix ([FixedBench summary](https://codex.danielvaughan.com/2026/06/19/coding-agents-fixing-correct-code-fixedbench-codex-cli-abstain-reproduce-before-patch-action-bias/)).

Reproduce-first is **not** the TDD ritual. It is one test, at a seam, for one bug. It is also the most valuable test to keep, because it stops the bug from coming back. Simon Willison recommends a permanent test for each bug ([Willison](https://simonwillison.net/guides/agentic-engineering-patterns/agentic-manual-testing)). Agents often do the opposite. In Google's study, when a fix arrived with no test, the agent had deleted its reproduction test as "temporary" in **77%** of cases ([arXiv 2601.19066](https://arxiv.org/html/2601.19066v1)).

Two small corrections apply to Geoff's point. First, the problem is not specific to Opus. Most frontier models show it to some degree ([Handshake](https://joinhandshake.com/research/ai/deepswe-reward-hacking/)). Second, a confirmation that the agent writes and judges alone can be circular. Ask to see the command and its output. Anthropic's documentation says: "'All tests pass' on its own tells you very little."

## Where Geoff's first argument is weak

Geoff's first claim was: "telling the agent to write tests first, even if you're going to toss them at merge time, results in a better result. Our internal bugbot went from missing well over 50% of the time to hitting over 75% of the time on that change alone." This argument has three weak points.

**It mixes two ideas.** "Confirm the problem" and "write tests first" are different things. You can confirm a problem when you run the command on the transcript that breaks it, or when you read a stack trace. Neither needs a unit test written in advance. Google's study separates the two ideas: free order beat strict TDD, and the reproduction was the part that helped. A bug-hunting bot that writes a failing test must prove each finding. That is reproduce-first with another name. It says little about TDD when you build features.

**The number is too large to trust alone.** A jump from under 50% to over 75% is at least **25 points**. The large controlled study measured 0 to 13 tasks out of 500. A carefully engineered method with hardened reproduction tests gained **9.6 points** ([arXiv 2607.19843](https://arxiv.org/abs/2607.19843)). In one small study, a shorter instruction file alone moved success from 12% to 50% on ten tasks ([arXiv 2603.17973](https://arxiv.org/html/2603.17973v1)). Large jumps from one change usually have other causes. These questions would turn the story into evidence:

| Question to ask Geoff | Why it matters |
|---|---|
| How many bugs were in the sample, and was it the same set before and after? | Small samples change a lot. Ten tasks moved from 12% to 50% on wording alone. |
| Who decided that a result was a "hit": a person, hidden tests, or the bot's own test? | A test and a fix can both be wrong and still pass together |
| Did the model, prompt length, tools or step limit change at the same time? | The model alone changed property-test gains from −8 to +42 points |
| Did the bot actually write the tests first? | Even with explicit TDD prompts, Google saw tests written first in only 78.66% of runs |
| What did each hit cost? | Test-first adds steps and tokens, several times over in Böckeler's runs |

**"Toss them at merge time" supports your view.** If the tests can go in the bin, their value was in the confirmation, not in the test files. It also throws away the wrong tests. The reproduction test is the one to keep.

None of this means Geoff's change did not help. The direction is plausible. Boris Cherny, who created Claude Code, estimated that verification loops give "2-3x" better quality, although that is also an anecdote ([VentureBeat](https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are)). Geoff's practice is mainstream advice, not a rote habit. But he gives the credit to the wrong part. **The value comes from the reproduction, not from the ritual.**

## Keep the agent honest 🔒

Your problems with test bloat and mocks are common. A peer-reviewed study of 48,563 agent commits found that **36% of agent test commits add mocks, compared with 26% for humans** ([Hora & Robbes, MSR 2026](https://arxiv.org/html/2602.00409v1)). Vaccari writes that the "volume of test code is large", and that mock-heavy tests break when the implementation changes. Your repo has about 2,200 lines of tests and 1,460 lines of source code. No source gives a "healthy" ratio. The ratio is a symptom. The real problems are **coupling and unreadable tests**.

A rule in CLAUDE.md is not enough by itself. CLAUDE.md is "**context, not enforced configuration**" ([Kiran](https://dev.to/honeykiran/your-agent-wrote-1800-tests-almost-none-of-them-matter-2487)). A hook can block an action, and CI (the automated checks that run on each change) can fail a change. Agents also **copy the style of existing test files**. If you clean up your worst test files, Claude's new tests improve too ([Anhaia](https://dev.to/gabrielanhaia/your-worst-test-file-is-your-real-prompt-coding-agents-copy-it-faithfully-4j93)). Each refactor to seam-level tests is also a better prompt.

A short testing section in CLAUDE.md sets the expectation. A hook then enforces the most important lines:

```markdown
## Testing rules
- Do not use red/green TDD. Write the code, then write sociable tests at public seams.
- For a bug: first show the failure (command and output). Then add one failing test
  at a public seam. Then fix it, and keep the test.
- Tests import only public names. Never import a name that starts with `_`.
- Add at most 5 new tests per change. Ask before you add more.
- Never edit files in `example_transcripts/` to make a test pass. Ask me first.
- If a check still fails after three attempts, stop and ask me.
```

The last line comes from the Claude Code team: "If a check is still failing after three rounds, Claude stops and brings in a human." For the private-import rule, Ruff has a lint rule, **PLC2701**. It is a preview rule, and your `pyproject.toml` does not turn on preview rules, so you must turn it on yourself.

To decide which tests to delete, use **mutation testing**. A tool makes small deliberate bugs, for example it changes `>` to `>=`, and reports which bugs no test finds. The Thoughtworks Technology Radar puts mutation testing at "Adopt", because "the volume of AI-generated code and tests increases rapidly" ([Thoughtworks Radar](https://www.thoughtworks.com/radar/techniques)). One report suggests it is only slightly better than simple coverage at finding AI faults, so use it as a guide, not as proof. A test that finds no bug that other tests miss is a candidate for deletion.

## Nine habits for this repo

| Habit | What it looks like in `youtube-to-xml` | Backing |
|---|---|---|
| **1. Define "done" as examples** | Before work starts, add a sample transcript and the exact XML you expect to `example_transcripts/`. You review data, not test code. | [Vaccari](https://martinfowler.com/articles/tests-as-data.html); [Farley](https://tessl.io/blog/vibe-coding-is-not-the-best-we-can-do) |
| **2. Build first, then sociable tests** | Let Claude write the code in its own order. Then ask for a small number of tests at public seams. | [Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html); [arXiv 2601.19066](https://arxiv.org/html/2601.19066v1) |
| **3. Reproduce every bug first** | "Run `uv run youtube-to-xml` on this file and show me the wrong output. Then write one failing test at a seam. Then fix it." | [Claude Code docs](https://code.claude.com/docs/en/best-practices) |
| **4. A `verify` skill** | `.claude/skills/verify/` runs the command on every golden file and compares the output. Claude uses it before each commit. | [claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/) |
| **5. Property tests** | Hypothesis tests for the timestamp round trip, no lost lines, increasing chapter times and valid XML | [claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/); [PBT-Bench](https://arxiv.org/html/2605.15229) |
| **6. Differential tests for changes of system** | Keep the file-versus-URL test. Use the same method for any rewrite or port. | [claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/) |
| **7. Keep the judge out of reach** | A permission rule that denies edits to `example_transcripts/`. CI that runs the checks. `/code-review` in a fresh context. | [claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/) |
| **8. A test budget and public-only imports** | The CLAUDE.md rules above, enforced by a hook and Ruff PLC2701 | [Kiran](https://dev.to/honeykiran/your-agent-wrote-1800-tests-almost-none-of-them-matter-2487); [Ruff docs](https://docs.astral.sh/ruff/rules/import-private-name/) |
| **9. Prune on a routine** | Once a month, ask Claude to run a mutation tool on one module and suggest deletions. You approve each one. | [Thoughtworks Radar](https://www.thoughtworks.com/radar/techniques) |

## The same approach in TypeScript

These habits transfer directly to TypeScript. Vitest replaces pytest, fast-check replaces Hypothesis, and Stryker is the usual mutation tool. Practitioners suggest `msw` to fake web calls, and fake timers in place of hand-written mocks ([Vaughan](https://codex.danielvaughan.com/2026/06/30/over-mocked-tests-coding-agents-codex-cli-agents-md-testing-guidance-mock-control/)). In TypeScript, the rule "do not test private functions" becomes "**tests import only what a module exports**". Heavy use of `vi.mock` is the same warning sign as heavy use of `MagicMock` in Python.

## Conclusion

Your principle is sound. Skip the red/green ritual. Let Claude build, then ask for a small set of sociable tests at the seams. Add strength with end-to-end tests, property tests and differential tests, because these do not share the agent's bias. Keep one test-first habit: **reproduce each bug before you fix it**, and keep that test. Above all, own the definition of "done" yourself, as examples that Claude cannot edit.

Two cautions keep this honest. The evidence is still thin. Böckeler's experiment is small, and the academic studies use benchmarks, not repositories like yours. Models also change every few months, so check these habits again from time to time. The safest long-term principle is not a test order. It is **independence and readability**: checks that the agent did not write and cannot change, in a form that you can read.
