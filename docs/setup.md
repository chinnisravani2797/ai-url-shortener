# Setup and Usage

## Prerequisites

- Python 3.11 or newer
- Git

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

## Run the API

```powershell
uvicorn app.main:app --reload
```

Open the interactive documentation at `http://127.0.0.1:8000/docs`.

## Example request

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/urls `
  -ContentType "application/json" `
  -Body '{"original_url":"https://www.example.com"}'
```

Use the returned `short_code` in `http://127.0.0.1:8000/{short_code}`. Analytics are available at `/api/v1/urls/{short_code}/analytics`.

## Run tests and quality checks

```powershell
python -m pytest -q
ruff check .
bandit -r app
```

The SQLite database is created automatically at runtime and is intentionally excluded from Git.
