# Engineering Scenarios

## 1. Greenfield: build the URL shortener

**Requirement:** Create, redirect, and report on short URLs.

**Decomposition:**

1. Define API contracts and error responses.
2. Validate HTTP(S) URLs.
3. Design the URL record and persistence boundary.
4. Generate collision-safe short codes.
5. Implement redirect and click counting.
6. Add analytics, tests, documentation, and quality checks.

**AI-assisted execution:** AI helped suggest endpoint shapes, validation cases, test cases, and documentation wording. The engineer reviewed and adapted each suggestion to the chosen FastAPI/SQLite design.

**Validation:** Pytest covers successful creation, redirect behavior, analytics, and missing codes. Manual Swagger testing confirms the API contract. Ruff and Bandit run as quality gates locally and in GitHub Actions.

## 2. Brownfield: fix a short-code collision defect

**Observed issue:** An existing implementation generated a code and inserted it without checking whether the code already existed.

**Investigation:** Reproduce the issue with a controlled duplicate-code test, inspect the creation path, and confirm the database uniqueness constraint and error behavior.

**Change:** Generate a cryptographically random code, check for an existing record, retry a bounded number of times, and return a controlled `503` if allocation repeatedly fails.

**Regression validation:** Add a test that exercises the collision path using a controlled generator or repository seam; run the complete test suite and review the database behavior.

**Risk control:** The retry bound prevents an infinite loop. A production implementation would add metrics and an operational alert for allocation failures.

## 3. Ambiguous requirement: URL expiry

**Requirement:** “URLs should expire after some time.”

**Clarifying assumptions:** Use a documented default lifetime, allow an optional expiry value, return `410 Gone` for an expired link, preserve analytics, and never delete the original mapping automatically.

**Decomposition:** Add an expiry field, validate that expiry is in the future, check expiry before redirecting, define the response contract, and test active/expired boundaries.

**AI-assisted execution:** AI was used to identify missing questions and edge cases. The engineer selected the assumptions, documented them, and would confirm them with the product owner before production release.

**Validation and open decisions:** Add unit and integration tests for timezone handling, boundary timestamps, and analytics after expiry. Confirm retention, timezone, default lifetime, and whether expired records can be reactivated before implementation.
