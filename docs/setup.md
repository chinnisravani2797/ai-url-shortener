# Setup and Usage

## Prerequisites

- Python 3.11 or newer
- Git

Verify the prerequisites before setup:

```powershell
python --version
git --version
```

If either command is unavailable, install Python from [python.org](https://www.python.org/downloads/windows/) and Git from [git-scm.com](https://git-scm.com/download/win), then reopen PowerShell.

## Windows setup

```powershell
git clone https://github.com/chinnisravani2797/ai-url-shortener.git
Set-Location ai-url-shortener
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run once as your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Optional environment configuration:

```powershell
Copy-Item .env.example .env
```

Never commit `.env`; it is excluded by `.gitignore`.

## Run the API

```powershell
uvicorn app.main:app --reload
```

Open the interactive documentation at `http://127.0.0.1:8000/docs`.

You can also verify process and database readiness:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
Invoke-RestMethod "http://127.0.0.1:8000/ready"
```

Expected responses are `{"status":"ok"}` and `{"status":"ready"}`.

## Example request

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/urls `
  -ContentType "application/json" `
  -Body '{"original_url":"https://www.example.com"}'
```

Use the returned `short_code` in `http://127.0.0.1:8000/{short_code}`. Analytics are available at `/api/v1/urls/{short_code}/analytics`.

## PowerShell verification

```powershell
$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/urls" `
  -ContentType "application/json" `
  -Body '{"original_url":"https://www.example.com"}'

$response | ConvertTo-Json
$code = $response.short_code
Invoke-WebRequest "http://127.0.0.1:8000/$code" -MaximumRedirection 0
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/urls/$code/analytics" | ConvertTo-Json
```

Expected results:

- Create request: HTTP `201 Created` with a generated `short_code`.
- Redirect request: HTTP `307 Temporary Redirect`. This is successful because the service intentionally tells the client to fetch the original URL without silently changing the request method.
- Redirect response: includes `X-Request-ID`, `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy` headers.
- Analytics request: HTTP `200 OK` with `click_count: 1`, proving the redirect was recorded.
- Invalid or unsafe URL: HTTP `422 Unprocessable Entity`, proving request validation is active.
- If `CREATE_API_KEY` is configured, include it as `X-API-Key` when creating URLs; missing or invalid keys return `401`.
- Rate-limited requests return `429` with `Retry-After: 60`.

## Run tests and quality checks

```powershell
python -m pytest -q
ruff check .
bandit -r app
```

The SQLite database is created automatically at runtime and is intentionally excluded from Git.

## Optional Docker/PostgreSQL run

Install Docker Desktop, then run:

```powershell
docker compose up --build
```

The API is available at `http://127.0.0.1:8000`. The Compose password is a local-development placeholder; replace it with a secret-managed value for real deployment. Stop the stack with:

```powershell
docker compose down
```
