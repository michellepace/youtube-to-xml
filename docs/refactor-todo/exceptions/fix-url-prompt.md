I have created a draft of @manual_url.md to parallel the "manual test case approach" of verifying the user  experience of exceptions when using the CLI. 

**YOUR GOAL:** Is to systematically evaluate that test cases for `manual_url.md` are sane (e.g correctly named  and using appropriate argument) and complete. 

**LEVERAGE THE FOLLOWING SOURCES AND LOGICAL THINKING TO DO THIS:** 
- Use `exceptions.py` to ensure coverage of all "URL" exceptions
- Use `test_exceptions_ytdlp.py` and `tests/end_to_end.py` to gather known test cases and test URLs
- Determine if other test cases will add additional valuable insights that a user may do not covered by the  testing modules (they may be incomplete but they also may not)
- You may search for other test modules if they current contain test cases for URL exceptions too

**IMPORTANT - BE TARGETE NOT REDUNDANT**
In `cli.py` review lines [190-199] taking note of the `is_valid_url` and routing. This will help you avoid  making exhausted test cases that will never be hit.

Once you have investigated and thought this through, Update `manual_url.py` to improve it and also complete  section "## Important Notes on Test Cases". 

Then summarise your changes and additions here as relevant.