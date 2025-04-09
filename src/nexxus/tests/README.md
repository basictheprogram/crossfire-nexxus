# Unit Test Prompt
Write comprehensive unit tests for the follow python code. The code is part of the `nexxus` django app.
- Use `pytest` for the testing framework
- The tests should cover standard behavior, edge cases, error handling, and overall code coverage.
- Use `django.test.Client` for making HTTP requests.
- Leverage the following testing libraries:
  - `pytest`
  - `pytest-django`
  - `pytest-mock`
  - `requests-mock`
  - `factory-boy`
  - `faker`
- Write tests with the following focus:
  - Validate view responses (status codes, redirections).
  - Test authentication, permissions, and access control (if applicable).
  - Test handling of edge cases (e.g., missing data, invalid inputs).
  - Ensure error handling is properly tested (e.g., 404, 500 errors).
  - Coverage for all major logic branches in the view.
- Use typing annotations and PEP 257 docstrings to improve code clarity and maintainability.
