# AI-Assisted Execution Log

AI was used as an engineering assistant. The engineer remained responsible for requirements, design, code review, testing, security, and release decisions.

| Task | Representative prompt sent to AI | AI output | Engineer action | Validation |
|---|---|---|---|---|
| API design | “For a FastAPI URL-shortener prototype, design versioned create, redirect, and analytics endpoints. Include status codes, validation, and no authentication assumptions. Keep the API small enough for a 2–3 day assessment.” | Suggested versioned endpoints and response shapes. | Accepted after checking the assignment scope. | Swagger review and API tests. |
| Persistence design | “Suggest a minimal durable URL mapping for SQLite using SQLAlchemy. Include short code, original URL, creation time, expiry-ready design, and click count. Avoid external infrastructure.” | Suggested URL mapping, timestamps, and click count. | Edited field names and selected SQLite for local portability. | Application startup and integration tests. |
| Short-code generation | “Design collision-safe short-code generation for a public API. Do not expose sequential IDs; use secure randomness and a bounded retry count. Explain failure handling.” | Suggested random alphanumeric codes and bounded retries. | Accepted the approach and set a seven-character code length. | Database uniqueness check and controlled failure response. |
| Test planning | “Create Pytest cases for valid and invalid URL creation, redirect behavior, click analytics, unknown codes, collisions, and expiry boundaries. Prioritize deterministic tests.” | Suggested validation, redirect, analytics, missing-code, and collision cases. | Accepted core cases; deferred load and concurrency tests. | Pytest suite and documented follow-up work. |
| Documentation | “Draft an assessment-ready architecture and scenario document. Describe components, control flow, trade-offs, AI review, validation, and limitations. Do not claim features that are not implemented.” | Produced an initial structure and wording. | Edited it to match the actual implementation and assessment language. | Manual review against the assessment PDF. |

## Secure AI-use controls

- No credentials, tokens, private customer data, or proprietary source code were provided to AI.
- Generated code was reviewed and adapted before being added.
- Test execution and API behavior were verified independently.
- High-impact decisions, including expiry semantics and production storage, remain engineer-owned decisions.

## Rejected or deferred suggestions

- A distributed database and queue were deferred because they were not necessary for a runnable two-to-three-day prototype.
- Automatic deletion of expired URLs was rejected because retention and audit requirements were not defined.
- Unauthenticated analytics were retained only for the prototype; production access control is a follow-up requirement.
