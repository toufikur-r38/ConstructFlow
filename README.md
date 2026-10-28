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

   Replace `SECRET_KEY` with a long random value. Set `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD` to your chosen Super Admin credentials; both are required by `seed-defaults`. Keep the development settings for local use. SQLite is created automatically; no separate database server is needed.

3. Create the database and first admin:

   ```powershell
   .\.venv\Scripts\python.exe -m flask --app main.py db upgrade
   .\.venv\Scripts\python.exe -m flask --app main.py seed-defaults
   ```

4. Start the app:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

   Open http://127.0.0.1:5000/login. Sign in using `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD` from `.env`.

## Run again

```powershell
.\.venv\Scripts\python.exe main.py
```

Stop the server with **Ctrl+C**. After pulling database changes, run the `db upgrade` command again.

## Reset the local development database

Use this when you want to erase all local users, projects, costs, and other database records and start fresh. These steps apply only to the default SQLite database at `app/construction.db`, when `DATABASE_URL` is unset. They do not reset a database configured through `DATABASE_URL`.

1. Stop the app with **Ctrl+C**. Back up the database first if you need to keep any data; deleting it permanently removes all its records.
2. Confirm that `.env` contains your desired `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD`.
3. From the repository folder, delete the database, recreate its tables, and seed the default dropdowns and Super Admin:

   ```powershell
   Remove-Item -LiteralPath .\app\construction.db
   .\.venv\Scripts\python.exe -m flask --app main.py db upgrade
   .\.venv\Scripts\python.exe -m flask --app main.py seed-defaults
   ```

   Run each command only after the previous one succeeds. Keep the `migrations` folder; it contains the instructions for rebuilding the database.

4. Start the app and sign in with the credentials from `.env`:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

## Common setup problems

- **`.venv\Scripts\python.exe` is missing:** create the virtual environment in step 1 before installing dependencies.
- **Admin password does not work:** changing `.env` or running `seed-defaults` again does not reset an existing account. Ask another admin to reset it under `/register`.
- **Changing the default username:** `seed-defaults` creates an account if that username does not exist; it does not rename an existing account. Edit existing users under `/register`.
- **Form expired:** refresh the login page and submit again. Tokens expire after one hour.

## Deployment

Local setup uses the development server. Production requires HTTPS, a fixed `SECRET_KEY`, `DATABASE_URL`, and `REDIS_URL`, with `FLASK_ENV=production` and `FLASK_DEBUG=0` set in the server environment.

1. Create a PostgreSQL database and database user through your hosting provider. Obtain its host, port, database name, username, and password. Also provision Redis for caching and rate limiting.
2. Set the following variables in your hosting dashboard or deployment service's environment configuration. Replace all placeholders with your actual settings:

   ```dotenv
   FLASK_ENV=production
   FLASK_DEBUG=0
   SECRET_KEY=replace-with-a-long-random-secret

   DATABASE_URL=postgresql+psycopg://DB_USER:DB_PASSWORD@DB_HOST:5432/DB_NAME
   REDIS_URL=redis://REDIS_HOST:6379/0

   DEFAULT_ADMIN_USERNAME=your_admin_username
   DEFAULT_ADMIN_PASSWORD=your_strong_admin_password
   ```

   Use `postgresql+psycopg://` because this project installs Psycopg 3. URL-encode special characters in the database username and password. Follow your provider's connection instructions for TLS, certificates, and authentication; for example, your PostgreSQL URL may require `?sslmode=require`, and your Redis URL may use `rediss://` with credentials.

   The database credentials connect the app to PostgreSQL. `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD` create the initial ERP Super Admin login.

   **Production environment loading:** `main.py` skips automatic `.env` loading when `FLASK_ENV=production` is already set in the process environment. Configure your hosting platform or deployment service to inject these variables, or explicitly load your protected `.env` file into the process environment before starting the app and running setup commands. Placing a `.env` file beside the app alone is not sufficient in that case.

3. Install the dependencies in your deployment environment, then initialize the database with the production variables loaded:

   ```bash
   python -m pip install -r requirements.txt
   python -m flask --app main.py db upgrade
   python -m flask --app main.py seed-defaults
   ```

   Run each command only after the previous one succeeds. The PostgreSQL database must already exist; migrations create its tables, and `seed-defaults` creates dropdown defaults and the configured Super Admin. Later deployments should run `db upgrade` for schema changes. Seeding does not reset an existing user's password.

4. Start the app through your production hosting service behind HTTPS. Use a production WSGI server rather than `python main.py`.

Setting `DATABASE_URL` connects to that database; it does not transfer records from your local SQLite database. A fresh PostgreSQL database starts without your local users, projects, or costs.

Keep `.env`, databases, logs, and backups out of Git. This repository does not include real project data or credentials.

MIT License - see [LICENSE](LICENSE).
