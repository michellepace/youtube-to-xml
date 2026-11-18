# Thought leaders on TDD with AI coding agents (2026 positions)

Scope: what recognised software-testing voices published in 2026 (Jan to Nov) about test-driven development when working with Claude Code, Codex, Cursor and similar agents. Items marked **[pre-2026]** are earlier and are given only as context. Items marked **[secondary]** come from third-party reports and not from the person's own words. Items marked **[unverified]** come only from search snippets. Where I write "paraphrase", the fetched page gave no direct quote. Research date: 18 Nov 2026.

---

## Q1. Does each person say TDD is dead, changed, or more important with agents?

### Takeaway
No one in this set says "TDD is dead". The real split is between two groups:
- **Test-first loops inside the agent are not worth it.** Birgitta Böckeler (Aug 2026) says the role of TDD "as we've known it is significantly smaller than pre-GenAI". Robert C. Martin (reported) says strict TDD should not be forced on agents. Matt Pocock (Sep 2026) has "mixed feelings".
- **Human-owned, test-first executable specifications are more important than ever.** Dave Farley (Aug 2026) and Matteo Vaccari of Thoughtworks (Nov 2026) take this view.

Kent Beck's 2026 writing does not argue for or against TDD directly. He keeps experimenting with forcing the "genie" into TDD and TCR loops, and argues that "AI wants big batches, trust wants small verified steps".

### Cited Findings

**Birgitta Böckeler (Thoughtworks; "Exploring Gen AI" series on martinfowler.com)**
- **"TDD inside the agent loop - theater or actual value?"** (10 Aug 2026; date from the series index), an informal experiment.
  - Setup: small, medium and large greenfield tasks. Sonnet 4.6 generated the solutions; Opus 4.8 ranked them blind. Conditions were no-TDD, TDD, and test-first without strict red-green, over five batches. Agents were told to reach at least 80% coverage. She calls it "far from a comprehensive and structured eval result". — [martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html); date per [series index](https://martinfowler.com/articles/exploring-gen-ai.html)
  - On quality: "there was no clearly discernable difference based on TDD workflow versus no TDD workflow". Also: "more than once Opus ranked the non-TDD workflow solutions slightly higher in design and test quality". — [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
  - On mutation scores: "There was also no meaningful difference in mutation scores across the solutions." — [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
  - On cost: TDD used about 8.5x the tokens for small tasks, 2.96x for medium and 4.89x for large. She says the metric "likely overstates TDD's true dollar cost", and that "TDD reliably cost several times more, how many times exactly is variable". — [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
  - On design: "The TDD instructions actively work against such an up front design step". TDD runs tended to lock in whatever shape the first test implied (paraphrase). — [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
  - Her verdict: "I personally have stopped telling my coding agents to write tests first, let alone do TDD (which I never did, to be honest)". Also: "I think the role of TDD as we've known it is significantly smaller than pre-GenAI". And the experiment "definitely hasn't given me any new indications that all this effort is worth it". — [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
- Martin Fowler promoted the article on X, asking: "Does telling a coding agent to do TDD by itself make a difference? Or is it one of the rare examples where what's good for the human is irrelevant or bad for an agent?" (from search snippet). — [Fowler on X](https://x.com/martinfowler/status/2087173563144912985) **[unverified]**
- **"Harness engineering for coding agent users"** (2 Apr 2026). She criticises the common practice of checking "if the AI-generated test suite is green, has reasonably high coverage", saying it "puts a lot of faith into the AI-generated tests, that's not good enough yet". — [martinfowler.com, 2 Apr 2026](https://martinfowler.com/articles/harness-engineering.html)

**Martin Fowler**
- In the conversation "LLMs and the what/how loop" (21 Jan 2026, with Unmesh Joshi and Rebecca Parsons):
  - Fowler: "Writing a test encourages us to think about the interface without coupling it to an implementation."
  - Joshi: "TDD is a design strategy that operationalizes the feedback loop between 'what' and 'how'."
  - Parsons: "we can use TDD and the LLM to drive the paradigm-appropriate 'how.'"
  - TDD is framed as still central, with LLMs making the loop more fluid. The piece does not cover agents specifically.
  — [martinfowler.com, 21 Jan 2026](https://martinfowler.com/articles/convo-what-how.html)
- Bliki "Agentic Engineering" (21 May 2026): "Humans are still responsible for what the software does and how it works". Humans evaluate agent work by "examining test results, and reviewing outputs from other sensors". It does not mention TDD. — [martinfowler.com/bliki, 21 May 2026](https://martinfowler.com/bliki/AgenticEngineering.html)
- Fowler also gave a "Conversation at Pragmatic Summit" video (7 Apr 2026). The martinfowler.com listing says it covers AI, agile and the role of TDD. I could not access its transcript. — [martinfowler.com 2026 tag](https://www.martinfowler.com/tags/2026.html); [YouTube](https://www.youtube.com/watch?v=CZs8J1ZD0CE)

**Kent Beck (newsletter "Software Design: Tidy First?", now newsletter.kentbeck.com)**
- **"Genie Sessions: TCR Skill"** (1 Apr 2026). "TCR is a TDD variant where, if the tests fail, you reset automatically to the last known good state. If the tests pass, you commit." He asks: "Can we use Skills to get the genie to work TCR-style?" So he is still trying to impose test-gated micro-steps on the agent. — [newsletter.kentbeck.com, 1 Apr 2026](https://newsletter.kentbeck.com/p/genie-sessions-tcr-skill)
- **"Genie Tarpit"** (29 Apr 2026). The genie's "'plausible deniability' task orientation leaves it claiming success even though the code doesn't work at all". Also: "complexity piles on complexity until even the genie can't pretend to make progress any more". He lists "high standards for the behavior of the system—tests, frequent integration, observability" as the mark of strong teams. A reader comment (Dave Rooney, not Beck) says: "We almost always have to remind it that we need tests and ask it to look again at it's skills about TDD". — [newsletter.kentbeck.com, 29 Apr 2026](https://newsletter.kentbeck.com/p/genie-tarpit)
- **"Trust Is the Binding Constraint"** (30 Oct 2026). Key lines:
  - "AI wants big batches, trust wants small verified steps."
  - "The tweak paradox: trustworthiness of code falls with the square of the size of changes."
  - "everybody is going to push you into solo AI development, and it is a huge mistake."
  - "Testing, pairing, continuous integration, planning" are listed as "The XP practices that manufacture trust".
  - The post does not name TDD.
  — [newsletter.kentbeck.com, 30 Oct 2026](https://newsletter.kentbeck.com/p/trust-is-the-binding-constraint)
- **"Passing Tests Bore Me"** (22 Apr 2026). It is paywalled. The visible preview only quotes a Codex note that "The biggest token consumers today were the repeated full make test outputs and file/diff reads." An AI-generated summary on kentbeck.com says the essay argues that tedious tests often mean shallow, implementation-focused tests. I could not verify that. — [newsletter.kentbeck.com, 22 Apr 2026](https://newsletter.kentbeck.com/p/passing-tests-bore-me); [kentbeck.com summaries](https://kentbeck.com/summaries) **[unverified]**
- **[pre-2026]** Context: in the Pragmatic Engineer interview (June 2025), Beck called TDD a "superpower" with agents because agents introduce regressions. He reported trouble stopping agents deleting tests to make them "pass". — [Pragmatic Engineer, Jun 2025](https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent)

**Dave Farley (Modern Software Engineering / Continuous Delivery)**
- **"Vibe Coding Is Not The Best We Can Do"** (Tessl blog, 24 Aug 2026).
  - He calls himself an "old-school, card-carrying test-driven development developer".
  - On what tests are: "They are a form of measurement."
  - On the human role: "Specifying the goal is part of the job".
  - On specifications: a BDD-style spec "can act as both the specification and the verification mechanism", and "the specifications are now effectively part of the program".
  — [tessl.io, 24 Aug 2026](https://tessl.io/blog/vibe-coding-is-not-the-best-we-can-do)
- On X he wrote that "prompts aren't enough. To safely guide AI agents, we need executable specifications" and pitched ATDD as "the future of AI coding" (from search snippet). A secondary search summary dated this to October 2026; I could not open the post (HTTP 402). — [Farley on X](https://x.com/davefarley77/status/2112967154761113708) **[unverified]**
- His "TDD & BDD – Design Through Testing" course is marketed for 2026 as the way to write new code with an AI assistant (from search snippet). — [cd.training](https://courses.cd.training/courses/tdd-bdd-design-through-testing) **[unverified]**

**Robert C. Martin ("Uncle Bob")**
- Startup Fortune (25 Jul 2026) reports from his X posts that he no longer reads agent-written code. Quotes:
  - "Humans are slow at code. To get productivity we humans need to disengage from code and manage from a higher level."
  - "I have very high confidence in the code they produce because they've had to run the gauntlet".
  - The gauntlet is unit tests, Gherkin acceptance tests, cyclomatic-complexity thresholds, module size limits, dependency analysis, mutation testing and coverage requirements.
  — [Startup Fortune, 25 Jul 2026](https://startupfortune.com/uncle-bob-martin-says-he-no-longer-reads-ai-generated-code-and-the-developer-world-is-split/) **[secondary]**; the original X post URLs were not given.
- A blog summary (20 Aug 2026) paraphrases him. He wrote long prompts explaining TDD and his coding rules, and the model largely ignored them. He now enforces quality after the fact with mutation testing and CRAP scores. — [Alex Rusin blog, 20 Aug 2026](https://blog.alexrusin.com/uncle-bob-ai-coding-agents/) **[secondary, no primary source cited]**
- A podcast summary reports that he thinks human disciplines such as TDD should not be strictly enforced on AI, because agents naturally write a function and then its test. — [skip.watch episode summary](https://skip.watch/en/DGMhbBfbkFE) **[secondary, AI-synthesised summary; unverified]**

**Thoughtworks authors and the Technology Radar**
- **Matteo Vaccari, "Tests as data"** (11 Nov 2026). He notes "AI usually generates lots of code before writing tests", which makes canonical TDD hard to enforce. He offers his techniques as test-first "with larger steps" (paraphrase). — [martinfowler.com, 11 Nov 2026](https://martinfowler.com/articles/tests-as-data.html)
- **Technology Radar Vol. 35 (Nov 2026)**: no blip for TDD itself was found. Related blips:
  - **Mutation testing** (Adopt), justified because "the volume of AI-generated code and tests increases rapidly".
  - **Tests as data over tests as code** (Assess).
  - **Harness quality evaluation** (Assess), which mentions "a test suite to enable TDD-style development of any guardrails".
  - **Human-in-the-loop theater** (Caution), which recommends "steering the system with mutation testing, property-based testing" instead of reviewing every change.
  — [thoughtworks.com/radar/techniques](https://www.thoughtworks.com/radar/techniques)
- **Technology Radar Vol. 34 (Apr 2026)**: "Feedback sensors for coding agents" at Trial. — [thoughtworks.com/radar/techniques](https://www.thoughtworks.com/radar/techniques); [Vol 34 PDF](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2026/04/tr_technology_radar_vol_34_en.pdf). I could not open the PDF.
- **[pre-2026]** Radar Vol. 33 (Nov 2025) recommended "reinforcing established practices such as TDD and static analysis, and embedding them directly into coding workflows" (from search snippet). — [Vol 33 PDF](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2025/11/tr_technology_radar_vol_33_en.pdf) **[unverified verbatim]**

**Gergely Orosz (The Pragmatic Engineer) / Matt Pocock**
- In "AI Skills with Matt Pocock" (17 Sep 2026), Pocock has "mixed feelings" about TDD with agents. His view: TDD helps humans because "a failing test will remind a distracted human of what is still failing". Because agents have longer context, he asks them to "produce proof that their code works", with or without TDD. Orosz gives no view of his own and points readers to the 2025 Beck episode for "another take on TDD". — [Pragmatic Engineer, 17 Sep 2026](https://newsletter.pragmaticengineer.com/p/ai-skills-with-matt-pocock)
- Search snippets say Orosz's "How Claude Code is built" mentions "test-driven development's (TDD) renaissance". I did not verify this, and the piece may be from 2025. — [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built) **[unverified; date unconfirmed]**

**Other practitioner reaction (lower authority)**
- Alex Bolboaca (Mozaic Works) responded to Böckeler with "Is TDD Actually Useful for AI Agents?". A September 2026 post on coding-is-like-cooking.info is titled "The Last Year Has Changed Everything I Knew About TDD After 20 Years". Both appear only in search snippets: TDD-instructed code was sometimes worse, and agents treated the tests as the only spec. — [Mozaic Works](https://mozaicworks.com/blog/is-tdd-actually-useful-for-ai-agents); [Coding Is Like Cooking, Sep 2026](https://coding-is-like-cooking.info/2026/09/the-last-year-has-changed-everything-i-knew-about-tdd-after-20-years/) **[unverified]**

### Inferences
- Positions now turn on whether a human writes the test, not on whether tests exist:
  - Farley, Vaccari and (implicitly) Fowler value tests as a human-authored statement of intent.
  - Böckeler's negative result concerns an agent writing its own tests first, with no human checkpoint between test and code.
- On TDD's design benefit, Fowler and Joshi (Jan 2026) say test-first helps think about the interface without coupling to implementation. Böckeler (Aug 2026) observed that when an agent does TDD, it can suppress up-front design instead. The two sides are talking about different actors: a human doing TDD versus an agent doing it.
- In Beck's 2026 writing, the theme moves from "TDD as superpower" (2025) to small, verified steps as the source of trust (Oct 2026). TCR is his concrete attempt to enforce that.

### Gaps
- **Kent C. Dodds**: no 2026 statement on TDD and agents found; searches returned only Kent Beck material.
- **Fowler**: his Pragmatic Summit talk (Apr 2026) and the GOTO conversation with Beck (posted May 2026) are videos I could not transcribe.
- **Uncle Bob**: no first-party 2026 quote found. Everything comes via secondary reports.
- **Paywalled Beck posts**: "Passing Tests Bore Me" (Apr 2026) and "Genie Lessons: Nobody Wants Agents" (23 Apr 2026) were not readable in full.

---

## Q2. What specific practices do they recommend?

### Takeaway
The common recommendations are:
- Have humans own the specification or acceptance tests, ideally in a form agents cannot quietly edit.
- Verify independently of the agent's own report, through CI, mutation testing and hidden tests.
- Prefer deterministic "sensors" or constraint gates over long prompt instructions.
- Keep steps small (Beck's TCR, "small verified steps").

### Cited Findings
- **Farley**:
  - Run the tests "ourselves in a deployment pipeline" rather than trusting the AI's report that they pass.
  - Keep some tests hidden from the AI so it cannot tailor code to the visible examples.
  - Version-control specifications as part of the program.
  - Required behaviour details "cannot be left for the AI to infer".
  — [Tessl, 24 Aug 2026](https://tessl.io/blog/vibe-coding-is-not-the-best-we-can-do)
- **Farley (reported)**: secondary sources describe a four-layer acceptance-test structure (domain language, DSL, protocol drivers, system under test). Specs are locked from agent edits because agents sometimes delete failing tests. — [daily.dev summary](https://daily.dev/posts/the-industry-is-catching-up-the-only-way-to-generate-ai-code-that-works-zwvb7hjbc) **[secondary, unverified]**
- **Vaccari**: make customer tests the primary human–AI contract, "a contract that establishes what the code should do for us". Store them as data (text, YAML or JSON) so changes are visible in source control. Developer unit tests should not be "the primary source of truth" for specifying behaviour. — [martinfowler.com, 11 Nov 2026](https://martinfowler.com/articles/tests-as-data.html)
- **Böckeler**:
  - Use mutation testing to judge regression quality: "I don't really care _how_ regression quality was achieved, as long as I have a mechanism to see how good it is". She adds: "I still care about solid regression tests". — [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
  - Earlier: "Mutation and structural testing are examples of computational feedback sensors that have been underused in the past". She also recommends the approved-fixtures pattern, which is "not a wholesale answer to the test quality problem". — [Böckeler, 2 Apr 2026](https://martinfowler.com/articles/harness-engineering.html)
  - She lists a human-writes-the-tests workflow among the options but does not firmly endorse it (paraphrase). — [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
- **Uncle Bob (reported)**:
  - A gauntlet of unit tests, Gherkin acceptance tests, complexity and size limits, dependency analysis, mutation testing and coverage. — [Startup Fortune, 25 Jul 2026](https://startupfortune.com/uncle-bob-martin-says-he-no-longer-reads-ai-generated-code-and-the-developer-world-is-split/) **[secondary]**
  - A "specifier" agent turns a human-written document into acceptance criteria, which a later QA agent executes. Narrow, short-lived agents and deterministic checks are preferred to long prompt rules. — [Alex Rusin, 20 Aug 2026](https://blog.alexrusin.com/uncle-bob-ai-coding-agents/) **[secondary]**
- **Beck**:
  - TCR via agent Skills (1 Apr 2026). — [newsletter.kentbeck.com](https://newsletter.kentbeck.com/p/genie-sessions-tcr-skill)
  - Small verified steps instead of big AI batches, and against solo AI development (30 Oct 2026). — [newsletter.kentbeck.com](https://newsletter.kentbeck.com/p/trust-is-the-binding-constraint)
  - A kentbeck.com summary says he used one agent to optimise and a separate, isolated agent to audit, avoiding a "conflict of interest". — [kentbeck.com summaries](https://kentbeck.com/summaries) **[AI-generated summary, unverified]**
- **Thoughtworks Radar Vol. 35**: mutation testing at Adopt; Human-in-the-loop theater at Caution (steer with mutation and property-based testing). — [thoughtworks.com/radar/techniques](https://www.thoughtworks.com/radar/techniques)
- **Pocock**: ask the agent for proof its code works, with or without TDD. — [Pragmatic Engineer, 17 Sep 2026](https://newsletter.pragmaticengineer.com/p/ai-skills-with-matt-pocock)
- **Don't let the agent edit tests**: the 2026 primary material does not use this exact wording.
  - Vaccari reports developers saying "the AI refactors both existing code and existing tests", which erodes trust. — [Vaccari, 11 Nov 2026](https://martinfowler.com/articles/tests-as-data.html)
  - A third-party guide says Beck put the red-green-refactor cycle into the agent's system prompt after seeing agents delete failing tests. That traces to his 2025 work. — [Augment Code guide](https://www.augmentcode.com/guides/spec-tdd-shippable-ai-generated-code) **[secondary; likely pre-2026 origin]**

### Inferences
- Mutation testing is the one practice that Böckeler, Uncle Bob (reported) and the Radar all endorse. In 2026 it is effectively replacing "test-first discipline" as the way to check the quality of AI-written tests.
- "Human writes the test, agent writes the code" is most explicit in Farley and Vaccari, at the acceptance or customer-test level, not the unit level.

### Gaps
- I found no 2026 first-party statement from Beck, Fowler or Uncle Bob that literally says "never let the agent edit tests". It is attributed to Farley only via secondary sources.

---

## Q3. Where do they disagree with each other?

### Takeaway
The main fault line is whether agent-run TDD is worth it.
- **Böckeler**: no, it is costly theatre.
- **Uncle Bob (reported)**: don't force strict TDD; enforce quality with gates instead.
- **Beck**: keeps trying to make agents work in TDD/TCR micro-steps.
- **Farley**: test-first specification is more important, but human-authored.

A second fault line is whether humans should still read agent code: Uncle Bob says no, Grady Booch says "trust but verify", and Fowler and Böckeler say humans remain responsible.

### Cited Findings
- **Böckeler**: "I personally have stopped telling my coding agents to write tests first" and TDD's role is "significantly smaller than pre-GenAI". — [10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
- **Farley**: tests that "express what we wanted before the solution existed" differ from AI-generated tests, and "Specifying the goal is part of the job". — [24 Aug 2026](https://tessl.io/blog/vibe-coding-is-not-the-best-we-can-do)
- **Beck**: is still building TCR Skills for the genie (Apr 2026), and argues "AI wants big batches, trust wants small verified steps" (Oct 2026). — [1 Apr 2026](https://newsletter.kentbeck.com/p/genie-sessions-tcr-skill); [30 Oct 2026](https://newsletter.kentbeck.com/p/trust-is-the-binding-constraint)
- **Uncle Bob**: says he no longer reads agent code. Grady Booch disagrees: "Trust but verify… As an experienced developer, I know the smell of what is good and what is not." — [Startup Fortune, 25 Jul 2026](https://startupfortune.com/uncle-bob-martin-says-he-no-longer-reads-ai-generated-code-and-the-developer-world-is-split/) **[secondary]**
- **Fowler**: under agentic engineering, developers are "concerned with the code, often giving it detailed review". — [bliki, 21 May 2026](https://martinfowler.com/bliki/AgenticEngineering.html)
- **Böckeler vs Bolboaca**: Bolboaca published a rebuttal arguing that, in some cases, the TDD code came out worse (from search snippet). — [Mozaic Works](https://mozaicworks.com/blog/is-tdd-actually-useful-for-ai-agents) **[unverified]**
- **Pocock vs Beck**: Pocock sees TDD's value mainly as a memory aid for humans, which matters less for long-context agents. Orosz explicitly contrasts this with Beck's take. — [17 Sep 2026](https://newsletter.pragmaticengineer.com/p/ai-skills-with-matt-pocock)

### Inferences
- Some of the disagreement is about granularity, not substance.
  - Böckeler tested unit-level red-green done by the agent.
  - Farley and Vaccari advocate acceptance or customer-level specs written by humans.
  - Vaccari explicitly calls his approach test-first "with larger steps".
  - Beck pushes for the opposite: smaller steps.

### Gaps
- I found no 2026 direct exchange between Beck and Böckeler, or between Beck and Farley.
- Fowler's own verdict on Böckeler's experiment is not available beyond his framing question on X.

---

## Q4. Comments on agents writing implementation-coupled tests, testing private internals, test bloat, and keeping vs discarding tests

### Takeaway
Several 2026 sources warn that agent-written tests often only confirm what the code already does: they are tautological, lock in bugs, or rely heavily on mocks. Writing tests first does not reliably prevent this.

Nobody in this set explicitly discusses solitary versus sociable unit tests or the testing of private methods. Test bloat appears mostly as a review-fatigue and token-cost concern.

### Cited Findings
- **Böckeler**: some TDD sessions still produced tests that "checked the implementation's output against itself". "Writing the test first doesn't reliably prevent this." Also: "a red test tells you the agent ran it and saw failure, not that the failure was for the right reason". And agents "frequently overshot and implemented more than the current test demanded". — [10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
- **Farley**: AI-generated tests derived only from code "can only verify that the code continues to do what the code already does". That is useful for refactoring, not for correctness. His `calculateTax` example shows an AI writing a test that locks in a wrong result. — [24 Aug 2026](https://tessl.io/blog/vibe-coding-is-not-the-best-we-can-do)
- **Vaccari**:
  - Mock-heavy tests "tend to break" on harmless refactors. AI-written tests often confirm current behaviour, bugs included (paraphrase).
  - "it's becoming natural that AI writes most, if not all the tests". The volume of generated tests causes review fatigue, so he argues for more readable, data-driven tests.
  — [11 Nov 2026](https://martinfowler.com/articles/tests-as-data.html)
- **Fowler / Joshi (Jan 2026)**:
  - Fowler: "Writing a test encourages us to think about the interface without coupling it to an implementation."
  - Joshi: "generating test cases with LLMs to improve 'test coverage' is not something I find very useful".
  — [21 Jan 2026](https://martinfowler.com/articles/convo-what-how.html)
- **Böckeler**: LLM review can catch "redundant tests, brute-force fixes", but only "expensively and probabilistically". — [2 Apr 2026](https://martinfowler.com/articles/harness-engineering.html)
- **Radar Vol. 35**: mutation testing is promoted because "the volume of AI-generated code and tests increases rapidly". This is an implicit test-bloat and test-quality concern. — [thoughtworks.com/radar/techniques](https://www.thoughtworks.com/radar/techniques)
- **Beck, "Decompose Run-On Tests"** (republished 13 Oct 2026; originally March 2013, so effectively pre-2026 content).
  - Split long tests and delete the original: "Deleting those assertions feels weird at first, but it's okay", provided you "Don't lose coverage".
  - The post does not mention agents.
  — [newsletter.kentbeck.com](https://newsletter.kentbeck.com/p/decompose-run-on-tests)
- **Beck, "Passing Tests Bore Me"** (22 Apr 2026): the preview notes that test output is a major token cost for Codex. The claim that the essay targets shallow, implementation-detail tests comes only from an AI summary. — [newsletter.kentbeck.com](https://newsletter.kentbeck.com/p/passing-tests-bore-me); [kentbeck.com summaries](https://kentbeck.com/summaries) **[unverified]**

### Inferences
- The shared diagnosis: when the agent writes both the code and the tests, the tests describe the implementation, not the intent. The cures proposed are specs authored by humans or customers (Farley, Vaccari) and an independent measure such as mutation testing (Böckeler, the Radar, Uncle Bob as reported). Writing the test first is not offered as the cure.

### Gaps
- **Sociable vs solitary unit tests** (Fowler's earlier terminology): no 2026 discussion found from these authors in an agent context.
- **Testing private internals**: no explicit 2026 comment found.
- **Keeping vs throwing away tests written first**: not addressed by any 2026 source I found. Böckeler only says she still cares about "solid regression tests". Beck's 2025 "throw away the code" theme and Böckeler's "Partner with the AI, throw away the code" memo (31 Jul 2025) are **[pre-2026]** and about code, not tests. — [martinfowler.com, Jul 2025](https://martinfowler.com/articles/exploring-gen-ai/partner-with-ai-and-throw-away-the-code.html)
- **Kent C. Dodds** (Testing Trophy): no 2026 material found.
