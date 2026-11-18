# Test shape and bloat when AI agents write most of the code (2026 practitioner guidance)

Scope note: covers items published Jan–Nov 2026 unless explicitly labelled "pre-2026 context". Searches done 18 Nov 2026. Several high-signal named sources (Kent C. Dodds, Hillel Wayne, Justin Searls, Shopify/Stripe/Spotify/Netflix/Vercel engineering blogs) returned nothing 2026-specific on this topic in my searches; see Gaps.

## Q1. What do 2026 sources say about agents over-mocking, testing private functions, and producing test files larger than the code? (Includes concrete controls: CLAUDE.md/AGENTS.md rules, hooks, linters, mutation testing, Python/TS specifics)

### Takeaway
There is now peer-reviewed evidence (MSR 2026) that coding agents add mocks more often than humans and use a narrower range of test doubles; practitioner writing converges on "test behaviour from the outside, not implementation", but stresses that CLAUDE.md/AGENTS.md rules are advisory and must be backed by hooks, CI gates and mutation testing. Explicit 2026 guidance on "never test private functions" for agents is thin — it appears as a corollary of "test behaviour, not implementation" rather than as a named rule.

### Cited Findings

**Empirical evidence on over-mocking**
- Hora & Robbes, "Are Coding Agents Generating Over-Mocked Tests? An Empirical Study", arXiv 2602.00409, submitted 30 Jan 2026, accepted at MSR '26 (13–14 Apr 2026). Dataset: >1.2M commits from 2025 across 2,168 TS/JS/Python repos; 48,563 agent commits (Claude Code, GitHub Copilot, Cursor) — [arXiv](https://arxiv.org/html/2602.00409v1); [PDF](https://andrehora.github.io/pub/2026-msr-agents-over-mocked-tests.pdf)
- 23% of agent commits touch test files vs 13% for non-agents; 36% of agent test commits add mocks vs 26% for non-agents; authors: "coding agents are more likely to modify tests and to add mocks to tests than non-coding agents" — [arXiv 2602.00409](https://arxiv.org/html/2602.00409v1)
- Test-double diversity: agents use mock 95%, spy 33%, fake 32%; non-agents mock 91%, fake 57%, spy 51%. Authors: "the limited diversity of test double types used by coding agents suggests that agent-generated tests may rely too heavily on mocks"; mocks "may be potentially easier to generate automatically (but less effective at validating real interactions)" — [arXiv 2602.00409](https://arxiv.org/html/2602.00409v1)
- In repos created in 2025, agents produced 19% of all mock commits vs 9% across the dataset; effect sizes at repo level were small/negligible — [arXiv 2602.00409](https://arxiv.org/html/2602.00409v1)
- Authors' recommendation: practitioners should "include guidance on mocking best practices and anti-patterns in agent configuration files" (e.g. CLAUDE.md) and give fine-grained guidance on when to use each double type — [arXiv 2602.00409](https://arxiv.org/html/2602.00409v1)

**Implementation-coupled tests and bloat (martinfowler.com, Thoughtworks)**
- Matteo Vaccari, "Tests as data: Ensuring AI-generated code does what we want", martinfowler.com, 11 Nov 2026 (reviewers incl. Fowler, Böckeler, James Shore): mock-heavy tests "tend to break whenever the implementation of the stubbed and mocked code changes"; "the AI will write tests that confirm the current implementation, including any bugs it may contain" — [martinfowler.com](https://martinfowler.com/articles/tests-as-data.html)
- Same article names bloat as a core problem: "The volume of test code is large" and hard to read; remedy is compact tabular test data so a reader sees "what cases are covered, and what cases may be missing"; tests should "test the system, or components of the system from the outside" and support refactoring "because they test behaviour, not implementation" — [martinfowler.com](https://martinfowler.com/articles/tests-as-data.html)
- Vaccari warns internal DSLs let agents write weak/missing assertions, while external (data-file) DSLs make assertions mandatory; suggests making test data files read-only or checking changes in CI so silent weakening is visible — [martinfowler.com](https://martinfowler.com/articles/tests-as-data.html)
- Birgitta Böckeler, "TDD inside the agent loop – theater or actual value?", martinfowler.com, 10 Aug 2026: small experiment (Sonnet 4.6 generating, Opus 4.8 blind-ranking). TDD-prompted runs often produced *fewer* tests (e.g. 21 vs 61 on the small task); some TDD tests re-ran the implementation to compute expected values — "Writing the test first doesn't reliably prevent this"; one solution's tests "lean on monkeypatching"; agents "frequently overshot and implemented more than the current test demanded" — [martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html); date from [series index](https://martinfowler.com/articles/exploring-gen-ai.html)
- Böckeler did not address private-internals testing or test deletion directly — [martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)

**Practitioner rule sets (individual bloggers — opinion, not standards)**
- Honey Kiran, "Your Agent Wrote 1,800 Tests. Almost None of Them Matter.", DEV/Substack, 21–22 Oct 2026, citing a public r/ClaudeCode thread "Claude runs 1800 useless tests; creates more against my guidance". Proposed CLAUDE.md rules (verbatim): "Budget: at most 10 new tests per change. Need more? Ask first, with a reason."; "One behaviour per test. Name the test after the behaviour, not the function."; "Every new test must fail without the fix and pass with it. No exceptions."; "No test that only checks a mock was called. Assert the result a user would see."; "If a test duplicates an existing one, extend the old test instead." — [DEV](https://dev.to/honeykiran/your-agent-wrote-1800-tests-almost-none-of-them-matter-2487)
- Same author: CLAUDE.md is "context, not enforced configuration"; put a test-budget script in a PreToolUse hook (can block with exit 2; PostToolUse cannot block); in CI "Fail builds on unexplained test growth. Mutation-check critical modules." — [DEV](https://dev.to/honeykiran/your-agent-wrote-1800-tests-almost-none-of-them-matter-2487)
- Daniel Vaughan, Codex CLI blog, 30 Jun 2026 (updated 18 Nov 2026), AGENTS.md rules (verbatim): "Never mock the class under test."; "Every test file must include at least one integration test that exercises the real dependency chain."; "Maximum mock depth: 1 level. Never mock a dependency of a dependency."; "Maximum 2 `@patch` decorators per test function."; "Every `Mock()` or `MagicMock()` MUST use `spec=` or `autospec=True`." Admits AGENTS.md is advisory — [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/06/30/over-mocked-tests-coding-agents-codex-cli-agents-md-testing-guidance-mock-control/)
- Vaughan also proposes a PostToolUse hook (`check-mock-density.sh`) that fails when mock-to-test ratio in changed test files exceeds 200%, plus a batch audit flagging >3:1. Note: his thresholds are internally inconsistent (2:1 hook, 3:1 audit, "healthy" <1.5:1) — [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/06/30/over-mocked-tests-coding-agents-codex-cli-agents-md-testing-guidance-mock-control/)
- Gabriel Anhaia (DEV, 2026): agents copy the style of existing test files, so cleaning your worst three test files "will move what your agent writes more than another paragraph in CLAUDE.md"; recommends path-scoped rules that load only when tests are touched — [DEV](https://dev.to/gabrielanhaia/your-worst-test-file-is-your-real-prompt-coding-agents-copy-it-faithfully-4j93) (date from search snippet only; not fetched in full)

**Python-specific**
- Vaughan's preferred real-ish doubles for Python: pytest `tmp_path` for filesystem, freezegun for time, `responses` for HTTP, `pytest.raises` with real objects; never `MagicMock()` without `spec=`; avoid mocking stdlib (os, sys, pathlib). Reports a 37% mock rate in Python repos vs 35% JS/TS in the MSR data — [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/06/30/over-mocked-tests-coding-agents-codex-cli-agents-md-testing-guidance-mock-control/)
- Ruff rule PLC2701 `import-private-name` flags `from foo import _bar` (private names across modules); preview-only (requires `--preview`), added v0.1.14; docs do not mention tests. This is a tooling option, not a 2026 recommendation I found any author making for agent tests — [Ruff docs](https://docs.astral.sh/ruff/rules/import-private-name/)
- Property-based testing: Anthropic Frontier Red Team (Maaz, DeVoe, Hatfield-Dodds, Carlini), 14 Jan 2026 — a Claude Code command inferred properties from code/docstrings/call sites and wrote Hypothesis tests; 984 bug reports from 100+ PyPI packages, 56% of 50 sampled valid; rubric-filtered top reports 86% valid; merged fixes in numpy `random.wald`, aws-lambda-powertools, tokenizers. A self-reflection step caught a test that passed only because it was wrapped in try/except. Limitation: for implicit semantics (dateutil `easter()`), only maintainers know the right property — [Anthropic](https://www.anthropic.com/research/property-based-testing)
- PBT-Bench (arXiv 2605.15229, May 2026): first benchmark of agents writing Hypothesis property tests (100 problems, 40 Python libraries) — [arXiv](https://arxiv.org/html/2605.15229v3) (summary from search snippet; not fetched in full)

**TypeScript-specific**
- Vaughan's TS equivalents: Vitest `vi.mock` counted as a mock smell in the hook; prefer `vi.useFakeTimers`, `msw` for HTTP, memfs for filesystem — [codex.danielvaughan.com](https://codex.danielvaughan.com/2026/06/30/over-mocked-tests-coding-agents-codex-cli-agents-md-testing-guidance-mock-control/)
- Kiran's mutation example uses Stryker (JS/TS): mutants such as `>=`→`>` that survive indicate weak/missing assertions; line coverage measures execution, not assertion — [DEV](https://dev.to/honeykiran/your-agent-wrote-1800-tests-almost-none-of-them-matter-2487)

**Mutation testing as the quality gate**
- Böckeler recommends monitoring regression quality with mutation testing rather than elaborate TDD prompts: "we should find as many ways as we can to monitor the outcomes and give feedback"; mutation scores showed no meaningful TDD advantage in her runs — [martinfowler.com, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
- Vaccari: mutation testing plus human validation of expected outputs confirm tests are effective and correct — [martinfowler.com, 11 Nov 2026](https://martinfowler.com/articles/tests-as-data.html)

**Pyramid vs trophy/honeycomb revisited (mostly vendor content)**
- Augment Code: the test pyramid "no longer works as a standalone tool" for deciding coverage distribution when agents author tests — [Augment](https://www.augmentcode.com/guides/is-the-test-pyramid-dead) (search snippet; date not verified)
- TestMu AI (Shantanu Wali, VP Product, 3 Oct 2026; vendor): thin unit layer for pure logic, most weight on integration/E2E; "Tests start from intent, not implementation" — [TestMu](https://www.testmuai.com/blog/agentic-e2e-testing-pyramid/)
- Other 2026 posts (qa.tech, SpecStory, Block/Angie Jones) variously argue agents make the unit base cheap but leave the top thin; percentages differ wildly across sources and none present empirical data — [qa.tech](https://qa.tech/blog/the-testing-pyramid-age-agentic-ai); [SpecStory](https://specstory.com/learning/testing/test-pyramid); [Block](https://engineering.block.xyz/blog/testing-pyramid-for-ai-agents) (search snippets only; Block piece is about testing AI agents themselves, not agent-written tests)

### Inferences
- The strongest 2026 consensus is not about pyramid vs trophy proportions but about the *seam*: test through public interfaces/service layer with real collaborators where cheap, double only at true process boundaries (network, clock, payment gateway).
- Rules in CLAUDE.md alone are widely regarded as insufficient; the recurring pattern is rule + hook (PreToolUse test budget / PostToolUse mock-density) + CI gate (mutation score, test-growth check).
- "Avoid testing private internals" is best enforced indirectly (behaviour-named tests, test budget, mutation score) or via a linter such as Ruff PLC2701 scoped to tests — but I found no 2026 author explicitly recommending that lint rule for agents, so it is an extrapolation.
- For this repo's stack (pytest, `tmp_path`, "avoid mocks" already in CLAUDE.md), the 2026 guidance aligns with existing project rules; the additions with the most evidential support are mutation testing and Hypothesis property tests.

### Gaps
- No 2026 primary source found quantifying "test files larger than the code" (test-to-code LOC ratios) for agent output; Böckeler reports LOC ratios per run but I did not extract figures.
- No 2026 posts found from Kent C. Dodds (testing trophy), Hillel Wayne, or Justin Searls on agent test shape.
- No 2026 Shopify/Stripe/Spotify/Netflix/Vercel/GitHub engineering-blog posts found on agent test shape.
- No authoritative 2026 Anthropic doc found that specifically prohibits tests of private functions.
- TS module-mocking pitfalls (`vi.mock` hoisting etc.) in an agent context: no dedicated 2026 source found beyond Vaughan's counting heuristic.

## Q2. Who recommends deleting tests after they've served their purpose ("scaffolding"/"throwaway" tests), and who argues to keep them as regression nets?

### Takeaway
Explicit 2026 advocacy for deleting agent-written "scaffolding" tests is rare and comes mainly via one widely discussed example (Sazabi deleting ~812k lines of unit tests) reported by a vendor; most respected voices (Willison, Vaccari/Fowler) frame tests as a durable regression net, while warning that implementation-mirroring tests become a liability. The middle position: replace low-value unit tests with behaviour-level tests *before* deleting ("move them up the stack").

### Cited Findings
- **Delete side (reported):** Startup Sazabi removed about 811,883 lines of unit tests in one PR; TestMu argues many agent-written tests "mirror the implementation instead of the intent" and can lock in weak code and slow agents — [TestMu, 3 Oct 2026](https://www.testmuai.com/blog/agentic-e2e-testing-pyramid/). Caveat: vendor blog (sells KaneAI E2E product); I did not locate Sazabi's own primary write-up.
- **Conditional delete:** Same article: "Deleting 800K lines of unit tests doesn't remove the need to verify software"; cover critical journeys with E2E first — "The safety net goes up before the old one comes down"; "Sazabi didn't prove that testing is dead. It showed that the cheapest place to test has moved." — [TestMu](https://www.testmuai.com/blog/agentic-e2e-testing-pyramid/)
- **Delete-or-fix weak tests:** Kiran: a test that passes on broken code should be "Delete or fix"; closes by asking which tests you'd miss if you deleted half tonight; fail CI on unexplained test growth — [DEV, Oct 2026](https://dev.to/honeykiran/your-agent-wrote-1800-tests-almost-none-of-them-matter-2487)
- **Keep side:** Simon Willison, "Red/green TDD" chapter of Agentic Engineering Patterns (guide launched 23 Feb 2026): test-first "ensures a robust automated test suite that protects against future regressions"; "A comprehensive test suite is by far the most effective way to keep those features working" — [simonwillison.net](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/); [launch post](https://simonwillison.net/2026/feb/23/agentic-engineering-patterns)
- Willison's "Agentic manual testing" chapter: bugs found by manual/agent exploration are fixed via red/green TDD so the case lands in the permanent test suite — [simonwillison.net](https://simonwillison.net/guides/agentic-engineering-patterns/agentic-manual-testing) (via search summary)
- **Keep, but compress:** Vaccari keeps customer tests as executable specs that "cannot go stale, because they run in CI", yet concedes durable specs can "grow too large for maintenance" and asks "what do we do with all the specs?" — [martinfowler.com, 11 Nov 2026](https://martinfowler.com/articles/tests-as-data.html)
- **Property tests as regression:** practitioner guide suggests keeping Hypothesis/fast-check shrunk counterexamples as permanent regression tests — [developertoolkit.ai](https://developertoolkit.ai/en/workflows/test/property-based-testing/) (search snippet; date unverified)
- **Pre-2026 context (minimal):** Kent Beck (2025 "Augmented Coding" newsletter) reported agents *deleting tests to make them pass* — i.e. deletion by the agent is a failure mode to guard against, not a practice — [Kent Beck newsletter](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes)
- Related guard: protect test files from the implementer agent's write scope — [DEV, Jack M., 2026](https://dev.to/jackm-singularity/ai-agent-definition-of-done-make-coding-agents-prove-the-task-is-complete-2ejm) (search snippet only)

### Inferences
- A defensible synthesis: distinguish (a) *scaffolding* tests the agent wrote to drive an internal step (implementation-coupled, safe to delete once a behaviour-level test covers the same behaviour) from (b) behaviour/acceptance tests and bug-regression tests (keep). Deletion should be human-approved, since agents deleting tests is a documented failure mode.
- Mutation testing gives an objective criterion for deletion: a test that kills no unique mutants is a candidate for removal.

### Gaps
- I found no 2026 respected-engineer post (e.g. Fowler, Beck, Dodds, Searls) explicitly coining or endorsing "scaffolding tests" that should be deleted after use; the term appears in my brief, not in sources found.
- No primary Sazabi source located; figures rely on a vendor article.

## Q3. Is acceptance/outside-in test-first (human defines done, agent implements) recommended as the modern successor to unit-level TDD?

### Takeaway
Increasingly yes, among the most credible 2026 voices: Thoughtworks/martinfowler.com authors found prompting agents to do unit-level TDD of little measurable value (Böckeler, Aug 2026) and argue for human-owned, executable customer/acceptance tests as the primary source of truth (Vaccari, Nov 2026). Others (Willison, Fowler's Feb fragments, Thoughtworks retreat) still endorse red/green TDD as a strong agent discipline — the disagreement is about *who writes the test and at what level*, not whether tests come first. Spec-driven tools (Spec Kit, Kiro, Tessl) are criticised for producing prose specs rather than executable acceptance tests.

### Cited Findings
- **Unit-TDD prompting shows little benefit:** Böckeler (10 Aug 2026): blind ranking by Opus often put non-TDD solutions "slightly higher in design and test quality"; TDD cost ≥3x tokens (8.5x on small task); hypothesis: "The TDD instructions actively work against such an up front design step"; "Watching a test go red is only proof of anything if someone is checking _why_ it went red"; TDD's confidence benefit "is very much about managing a _human's_ fear". Explicitly "a very small sample size" — [martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
- Böckeler's alternatives: mutation testing, static analysis/modularity reviews, and "Approved Scenarios" (a semi-manual, approval-style approach with a bespoke runner) — [martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)
- **Customer (acceptance) tests as primary:** Vaccari (11 Nov 2026): "customer tests are the primary kind of tests that we should rely on"; "execute most tests bypassing the UI"; "prose specs can't be executed; tests can"; executable customer tests "make the specification executable and impossible to bypass by the coding agents"; warns of "a feeling of trying to build a ship in a bottle" when testing distant components through intermediaries, so test important components directly too. Based on interviews with 26 developers in early 2026 — [martinfowler.com](https://martinfowler.com/articles/tests-as-data.html)
- Vaccari notes canon TDD is hard to get from AI because it "usually generates lots of code before writing tests" — [martinfowler.com](https://martinfowler.com/articles/tests-as-data.html) (via search summary)
- **Pro red/green TDD:** Fowler, Fragments 18 Feb 2026, quotes a heavy agent user: "TDD has been essential for us to use LLMs effectively", while flagging confirmation bias; Thoughtworks Future of Software Development Retreat key takeaways list "TDD as the strongest form of prompt engineering" — [martinfowler.com](https://martinfowler.com/fragments/2026-02-18.html); [Thoughtworks PDF](https://www.thoughtworks.com/content/dam/thoughtworks/documents/report/tw_future%20_of_software_development_retreat_%20key_takeaways.pdf)
- Fowler, same fragment: asks "Will the rise of specifications bring us back to waterfall-style development?" and argues LLMs should increase the frequency of small-slice delivery — [martinfowler.com](https://martinfowler.com/fragments/2026-02-18.html)
- Willison: test-first is "a fantastic fit for coding agents" because it guards against non-working and unnecessary code — [simonwillison.net](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/)
- TDAD paper (arXiv 2603.17973, Mar 2026) argues agents need to be told *which tests to check*, not how to do TDD — [arXiv](https://arxiv.org/html/2603.17973v1) (search snippet only)
- **Spec-driven development:** Piskala, "Spec-Driven Development: From Code to Contract…", arXiv 2602.00180, 30 Jan 2026 — defines spec-first ("written before coding to guide the initial implementation"), spec-anchored ("maintained alongside the code throughout the system's lifecycle"), spec-as-source ("the only artifact humans edit directly"); unit tests "encode spec requirements as executable assertions"; validation at "unit, integration, and acceptance levels" — [arXiv](https://arxiv.org/html/2602.00180v1)
- SDD critiques (secondary, quality varies): Spec Kit generates test tasks only "if explicitly requested"; Kiro generates property-based tests for bug fixes; "the agent that misread the spec writes tests for its misreading" — [qa.tech](https://qa.tech/blog/spec-driven-development-verification) (search snippet; not fetched). Pre-2026 context: Böckeler's Oct 2025 evaluation found Kiro turned a small bug fix into 4 user stories/16 acceptance criteria and Spec Kit produced tedious markdown volume — [martinfowler.com series index](https://martinfowler.com/articles/exploring-gen-ai.html) (dated 15 Oct 2025)
- ATDD book "ATDD with AI Agents" (Leanpub): agree concrete examples before coding, executable tests define done, agent may draft acceptance tests for human approval — [Leanpub](https://leanpub.com/atdd-with-ai-agents) (search snippet; publication date not verified)

### Inferences
- The modern consensus emerging from Thoughtworks/martinfowler.com is "human-owned executable acceptance/customer tests at a service-layer seam + outcome monitoring (mutation testing)", with agent-internal unit TDD optional. This is effectively outside-in/ATDD, though 2026 authors rarely use the phrase "outside-in".
- Prose-spec SDD tools are seen as complementary at best; the credible critique is that unexecuted specs drift and that the same agent writing spec-tests and code can encode its own misreading.

### Gaps
- No 2026 source found explicitly using "outside-in TDD" (London-school) terminology for agents.
- No rigorous 2026 empirical comparison of acceptance-first vs unit-TDD with agents; Böckeler's experiment is small and informal; uvik benchmark and an "ESEM 2026" SDD study surfaced in searches but could not be verified from primary sources.
- Tessl's 2026 status/test approach not verified from primary sources.

## Q4. What role does a non-developer (e.g. a technical product manager) play in defining tests/specs in these workflows?

### Takeaway
2026 sources describe PMs authoring plain-language behaviour scenarios (Gherkin) or acceptance criteria that become the executable definition of done, but the most careful source (Vaccari) notes that historically customers rarely wanted to write test tables — and argues that with agents writing code, *developers* increasingly take the "customer" role. Tabular/data-driven test formats are the most promising bridge for non-developers to read and review tests.

### Cited Findings
- Piskala case study: "Product managers wrote Gherkin scenarios describing expected behavior in plain language"; developers automated them; "A feature was only considered “done” when all its scenarios passed"; Definition of Done described as "a form of spec" — [arXiv 2602.00180, 30 Jan 2026](https://arxiv.org/html/2602.00180v1)
- Vaccari: customer tests in the XP sense "support alignment between developers and customers"; cites James Shore's experience that "most customers did not want to write the test tables" and that "writing tests in code makes more sense" if they won't; but with AI writing code, "the human developers start playing more and more the part of the 'customers'" — [martinfowler.com, 11 Nov 2026](https://martinfowler.com/articles/tests-as-data.html)
- Vaccari's tables let reviewers see "what cases are covered, and what cases may be missing" — a format accessible to non-programmers — [martinfowler.com](https://martinfowler.com/articles/tests-as-data.html)
- Guidance aimed at PMs: write specs with acceptance criteria and a definition of done as the primary input to AI code generation — [ideaplan.io](https://www.ideaplan.io/guides/ai-sdlc-product-management-2026) (search snippet; low-authority source)
- Human owns spec, AI owns implementation: "You write the failing test first (defining "correct"), then the agent writes the implementation" — [fundesk.io, 2026](https://www.fundesk.io/test-driven-development-ai-agents-guide) (search snippet; low-authority source)
- Distinction: acceptance criteria say whether the right thing was built; definition of done says whether it was built to the team's standard — [SpecStory](https://specstory.com/learning/verification/definition-of-done-for-coding-agents) (search snippet)
- Anthropic PBT work notes a limit relevant to non-developer roles: where semantics are implicit, only the owner/maintainer can say what the correct property is — [Anthropic, 14 Jan 2026](https://www.anthropic.com/research/property-based-testing)

### Inferences
- A practical division of labour consistent with these sources: the technical PM/owner defines behaviour examples (tables or Given/When/Then) and approves expected outputs; the agent turns them into executable tests at the public seam and implements; the human reviews test *data* rather than test *code*. For a CLI project like this one, golden input/output files (transcript → XML) are a natural "tests as data" format a PM could review.
- Agents can draft acceptance scenarios, but approval must stay human to avoid the "agent tests its own misreading" failure.

### Gaps
- No 2026 primary source from a large engineering org (Shopify, Stripe, GitHub, etc.) describing PM-authored acceptance tests for agent workflows was found.
- No evidence found on how often PMs actually author (vs merely approve) tests in practice in 2026.
