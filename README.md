# AI-Assisted URL Shortener

This project is an engineer-led, AI-assisted prototype for a production-minded URL shortener.

## APIs

- `POST /api/v1/urls` — create a short URL
- `GET /{short_code}` — redirect and record a click
- `GET /api/v1/urls/{short_code}/analytics` — view click analytics
- `GET /health` — health check

Interactive API documentation is available at `/docs` when the application is running.

After creating a short URL, open `http://127.0.0.1:8000/<short_code>` in a browser to verify that it redirects to the original URL.

## Initial scope

- Create a short URL from a validated long URL.
- Redirect a short code to its original URL.
- Record basic click analytics.
- Support optional expiry and safe error responses.
- Provide tests, architecture notes, AI execution traceability, and automated quality checks.

Implementation and design decisions will be added incrementally as the prototype is developed.

## Assessment documentation

- [Setup and usage](docs/setup.md)
- [Architecture overview](docs/architecture.md)
- [Engineering scenarios](docs/scenarios.md)
- [AI-assisted execution log](docs/ai-execution-log.md)
- [Final engineering summary](docs/final-summary.md)

GitHub Actions runs the automated tests, Ruff, and Bandit checks for pushes and pull requests.
