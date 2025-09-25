THINK HARD FOR ELEGANT SIMPLICITY:

Your task is to evaluate the code quality of `<source_module>` for opportunities to refactor. We implement using test driven development, the testing module is `<test_module>` (~160 lines). We prefer "elegant simplicity" and "self-document code" rather than "over engineered". 

<source_module>
`src/url_parser.py` (~280 lines)
</source_module>

<test_module>
`tests/test_url_parser.py` (~160 lines)
</test_module>

Please perform a comprehensive evaluation using criteria like:
* Single responsibility
* Code that is testable (encapsulation where pragmatic - a balance)
* Small well named practical functions over monolithic functions
* Clear, cohesive, and consistent naming of functions and variables
* Type annotation for function signatures

When changes are needed, we use test driven development:
* Process: write test > fail > implement change > pass
* Use pytest's `tmp_path` fixture to avoid creating test files
* Avoid mocks as they introduce unnecessary complexity
* Test incrementally: One test should drive one behaviour
* Use focused test names that describe what's being tested

Your evaluation report must recommend refactor improvements that are valuable by improving clarity, reducing complexity, and ensure pragmatic robustness (no over engineering). For each recommendation outline what test could be written or explain why one is not needed.

Output this evaluation report and actionable recommendations as a well-structured document `1-REPORT.md` 