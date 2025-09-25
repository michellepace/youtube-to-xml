THINK HARD FOR ELEGANT SIMPLICITY:

# Code Quality Evaluation Task

## Objective
Perform a comprehensive code quality assessment of `<source_module>` to identify refactoring opportunities that improve maintainability, readability, and robustness.

<source_module>
`src/url_parser.py` (~280 lines)
</source_module>

<test_module>
`tests/test_url_parser.py` (~160 lines)
</test_module>

## Pre-Analysis Context Review
Before evaluating, analyze:
- The module's primary purpose and responsibilities
- How it integrates with the broader codebase
- The existing test coverage in `<test_module>`
- Any dependencies and usage patterns

## Code Quality Evaluation Framework

Systematically assess each aspect below, thinking through the current implementation and identifying specific issues:

### 1. Architectural Quality
- **Single Responsibility Principle**: Does each function/class have one clear purpose?
- **Separation of Concerns**: Are different responsibilities properly isolated?
- **Module Cohesion**: Do all components belong together logically?

### 2. Function Design Quality
- **Function Size**: Are functions focused and concise (ideally <20 lines)?
- **Function Complexity**: Avoid deep nesting, multiple return paths, or complex conditionals
- **Parameter Count**: Functions should have minimal parameters (ideally <4)
- **Return Value Clarity**: Functions should return predictable, well-typed values

### 3. Code Readability Quality
- **Naming Clarity**: Do names clearly express intent without abbreviations or ambiguity?
- **Type Annotations**: Are function signatures properly typed for clarity and tooling?
- **Code Self-Documentation**: Is the code's purpose obvious without extensive comments?
- **Consistent Style**: Is naming and structure consistent throughout?

### 4. Testability Quality
- **Pure Functions**: Are functions deterministic with minimal side effects?
- **Dependency Injection**: Can dependencies be easily substituted for testing?
- **State Management**: Is mutable state minimized and well-contained?
- **Error Handling**: Are error conditions testable and well-defined?

## Evaluation Process

For each quality aspect:
1. **Analyze Current State**: Examine the existing implementation
2. **Identify Issues**: Find specific problems with examples
3. **Assess Impact**: Determine how issues affect maintainability/clarity
4. **Propose Solutions**: Suggest specific, actionable improvements
5. **Consider Tests**: Identify what tests would validate the improvement

## TDD Refactoring Approach

When recommending changes, follow our TDD methodology:
- **Test-First**: Write failing tests that specify desired behaviour
- **Incremental**: One test should drive one focused change
- **Practical Testing**: Use `tmp_path` fixture, avoid mocks unless essential
- **Clear Test Names**: Tests should describe the specific behaviour being verified

## Output Requirements

Create `2-REPORT.md` with the following structure:
```markdown
# URL Parser Code Quality Evaluation

## Executive Summary
- Overall assessment (Good/Needs Improvement/Poor)
- Top 3 priority improvements
- Estimated refactoring effort

## Detailed Analysis

### [Quality Aspect Name]
**Current State**: [Description of current implementation]
**Issues Found**: [Specific problems with code examples]
**Impact**: [How this affects maintainability/clarity]
**Recommendation**: [Specific improvement with rationale]
**Test Strategy**: [What test to write or why none needed]
**Priority**: [High/Medium/Low]

## Refactoring Roadmap
1. [Priority order of improvements]
2. [Suggested implementation sequence]
3. [Dependencies between changes]

## Test Coverage Assessment
- Current test adequacy
- Missing test scenarios
- Opportunities to improve test quality