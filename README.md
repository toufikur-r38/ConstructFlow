# ConstructFlow

A Flask app for managing construction projects, costs, user roles, and PDF/Excel reports, with English and Bangla support.

## Setup (Windows PowerShell)

Install [Python 3.13](https://www.python.org/downloads/) with **Add Python to PATH** enabled, then reopen PowerShell. Run these commands from the repository folder.

1. Create a virtual environment and install dependencies. No activation is needed.

   ```powershell
   python --version
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   If `python` is not found, try `py -3.13` for the first two commands. If neither works, install Python first.

2. Create your local settings (first setup only):

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   Replace `SECRET_KEY` with a long random value and set `DEFAULT_ADMIN_PASSWORD` to your chosen password. Keep the development settings for local use. SQLite is created automatically; no separate database server is needed.

3. Create the database and first admin:

   ```powershell
   .\.venv\Scripts\python.exe -m flask --app main.py db upgrade
   .\.venv\Scripts\python.exe -m flask --app main.py seed-defaults
   ```

4. Start the app:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

   Open http://127.0.0.1:5000/login. Sign in as **admin** using the password you set in `.env`.

## Run again

```powershell
.\.venv\Scripts\python.exe main.py
```

Stop the server with **Ctrl+C**. After pulling database changes, run the `db upgrade` command again.

## Common setup problems

- **`.venv\Scripts\python.exe` is missing:** create the virtual environment in step 1 before installing dependencies.
- **Admin password does not work:** changing `.env` or running `seed-defaults` again does not reset an existing account. Ask another admin to reset it under `/register`.
- **Form expired:** refresh the login page and submit again. Tokens expire after one hour.

## Deployment

Local setup uses the development server. Production requires HTTPS, a fixed `SECRET_KEY`, `DATABASE_URL`, and `REDIS_URL`, with `FLASK_ENV=production` and `FLASK_DEBUG=0` set in the server environment.

Keep `.env`, databases, logs, and backups out of Git. This repository does not include real project data or credentials.

MIT License - see [LICENSE](LICENSE).
