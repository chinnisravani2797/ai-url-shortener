# Architecture Overview

## Components

- **FastAPI application**: exposes versioned REST endpoints and validates request data.
- **SQLAlchemy model/session**: maps URL records to SQLite for the prototype.
- **SQLite**: persistent local store for short-code mappings and click counts.
- **Pytest**: automated API regression tests.
- **Ruff and Bandit**: linting and basic security checks.

## Request flow

1. Client sends a validated long URL to `POST /api/v1/urls`.
2. FastAPI validates the payload with Pydantic.
3. The API handler generates a cryptographically random seven-character code.
4. The SQLAlchemy session checks uniqueness and stores the mapping in SQLite.
5. The API returns the short code.
6. A client requests `GET /{short_code}`.
7. The application finds the mapping, increments the click count, and returns a temporary redirect.
8. `GET /api/v1/urls/{short_code}/analytics` returns non-sensitive usage information.

## Decisions and trade-offs

- SQLite keeps the prototype simple and runnable without external infrastructure; production would use a managed relational database.
- Random codes avoid exposing sequential database IDs; a uniqueness check with bounded retries handles collisions.
- Redirects use HTTP 307 so the destination is explicit and the behavior is easy to test.
- The API accepts only HTTP(S) URLs through Pydantic validation, rejects unsafe destinations, applies configurable rate limiting, and optionally protects analytics with an API key. A distributed limiter and stronger identity/authorization model remain production follow-ups.

## AI-assisted engineering control flow

1. The engineer defines the requirement, constraints, and acceptance criteria.
2. AI is used for implementation suggestions, test ideas, documentation, and review prompts.
3. The engineer reviews, edits, or rejects generated output and records the rationale.
4. Automated gates run: tests, linting, and security scanning.
5. The engineer performs final review and owns the correctness and release decision.

AI does not receive secrets or production data, and generated code is never accepted without human review and validation.
