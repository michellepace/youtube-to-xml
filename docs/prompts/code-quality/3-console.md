THINK HARD FOR ELEGANT SIMPLICITY:

# Python Code Quality Evaluation Task

## Context

You are evaluating `<source_module>` and its test suite `<test_module>` for refactoring opportunities. This project follows test-driven development and prioritises maintainable, readable code over complex architectures.

<source_module>
`src/youtube_to_xml/url_parser.py` (~280 lines)
</source_module>

<test_module>
`tests/test_url_parser.py` (~160 lines)
</test_module>

## Quality Standards

**Maintainable Simplicity**: Code should be easy to understand and modify. Prefer:

- Functions with single responsibilities
- Cyclomatic complexity under 10
- Clear, descriptive names over comments
- Straightforward solutions over clever abstractions

**Professional Standards**: Apply industry best practices:

- Type annotations on all function signatures
- Proper error handling without over-engineering
- Testable design with clear interfaces

## Evaluation Framework

### 1. Code Structure Analysis

- **Single Responsibility**: Each function/class has one clear purpose
- **Function Size**: Identify functions >20 lines that could be decomposed
- **Complexity**: Flag high cyclomatic complexity (>10)
- **Dependencies**: Assess coupling between components
- **Encapsulation**: Are there functions that are sensible to be private?

### 2. Naming and Clarity

- **Descriptive Names**: Functions and variables clearly express intent
- **Consistency**: Uniform naming patterns throughout codebase
- **Self-Documentation**: Code meaning is clear without extensive comments

### 3. Testing Architecture

- **Coverage**: All public functions have corresponding tests
- **Test Quality**: Tests are focused, independent, and descriptive
- **TDD Compatibility**: Code structure supports incremental testing

### 4. Type Safety and Robustness

- **Type Annotations**: All function signatures include proper types
- **Error Handling**: Appropriate exception handling without over-complication
- **Edge Cases**: Critical paths handle boundary conditions

## Evaluation Process

1. **Initial Assessment**: Read through the entire codebase to understand overall structure and purpose
2. **Structural Analysis**: Apply the evaluation framework systematically to each function and class
3. **Pattern Recognition**: Identify recurring issues or architectural problems
4. **Impact Prioritisation**: Classify findings by effort required vs. benefit gained
5. **Test Strategy**: For each recommendation, determine required test approach

## TDD Refactoring Approach

When recommending changes that require new tests:

- **Extract Method**: Write test for extracted functionality first > run to fail
- **Interface Changes**: Update tests before modifying function signatures  
- **New Features**: Follow write-test-fail-implement-pass cycle
- **Existing Behaviour**: Ensure current tests still pass after refactoring

**Testing Guidelines**:

- Use `pytest` with `tmp_path` fixture for file operations
- Write focused tests with descriptive names (e.g., `test_parse_url_handles_missing_protocol`)
- Avoid mocks unless testing external dependencies
- One test should verify one specific behaviour

## Required Output: `3-REPORT.md`

Structure your evaluation as follows:

### Executive Summary

- Overall code quality assessment (1-2 paragraphs)
- Top 3 priority recommendations with impact summary

### Detailed Analysis

For each major finding:

- **Issue**: Specific problem with code location
- **Impact**: How this affects maintainability/readability
- **Recommendation**: Concrete refactoring steps
- **Test Strategy**: Required test changes or explanation why tests aren't needed
- **Effort**: Estimated complexity (Low/Medium/High)

### Refactoring Roadmap

- Prioritized list of recommendations
- Suggested implementation order
- Dependencies between refactoring tasks

### Code Quality Metrics

- Function count and average size
- Identified complexity hotspots
- Test coverage gaps
- Type annotation completeness

## Success Criteria

Your recommendations should:

- Improve code readability and maintainability
- Reduce complexity without over-engineering
- Support the existing test-driven development workflow
- Provide clear, actionable steps with effort estimates
- Justify each change with concrete benefits
