# ConstructFlow

ConstructFlow is a public showcase version of a Flask-based construction project ledger and cost management system. It supports project registries, expenditure tracking, filtered reports, audit history, managed dropdowns, user roles, module access, and English/Bangla UI translations.

This showcase repository does not include production secrets, private database files, logs, uploads, generated reports, backups, or real project data.

## Features

- Authentication with Flask-Login, CSRF protection, rate limiting, secure cookie settings, and security headers.
- Role-based access for `viewer`, `operator`, and `admin` users.
- Module-based access through the Construction workspace, with a module hub ready for future modules.
- Separate super-admin flag for system-owner accounts.
- Project ledger with firm/tender details, work order year, budget tracking, status, and completion date.
- Cost entry workflow for running projects and late-cost entry for completed projects.
- Edit, void, and restore workflows with password confirmation and audit snapshots.
- Managed project sector and cost type dropdowns.
- Financial dashboards and filtered PDF cost reports.
- Separate app, access, security, audit, and error logging setup.
- PostgreSQL-ready configuration with Redis support for cache/rate-limit storage.
- Manual PostgreSQL backup script.
- English and Bangla JSON translation files.

## Project Structure

```text
app/
  __init__.py                  Flask app factory, routes, error handlers, blueprint registration
  config.py                    Environment-driven configuration
  extensions.py                Flask extension instances
  models/                      SQLAlchemy models and module registry
  cli.py                       CLI seed command
  translations/                English and Bangla UI translations
  templates/                   Shared layout, module hub, error page
  modules/
    auth/                      Login/logout
    account/                   Profile and password changes
    admin/                     User management and module assignment
    construction/
      routes/                  Dashboard, project, cost, and admin/audit routes
      services/                Dashboard/module overview calculations
      templates/               Construction module UI
      utils/                   Dropdown seeding and PDF generation
migrations/                    Flask-Migrate/Alembic database migrations
scripts/                       Utility scripts, including database backup
main.py                        Application entry point
requirements.txt              Python runtime dependencies
.env.example                  Example environment variables
```

## Main URLs

- `/login` - sign in
- `/modules` - module hub
- `/construction/` - Construction module entry
- `/construction/admin-dashboard` - admin dashboard
- `/construction/operator-dashboard` - operator dashboard
- `/construction/viewer-dashboard` - viewer dashboard
- `/construction/add-project` - add projects
- `/construction/view-projects` - project ledger
- `/construction/add-cost` - cost entry
- `/construction/view-costs` - reports and PDF export
- `/construction/dropdown-options` - sector/cost type options
- `/construction/audit-log` - audit hub
- `/register` - add/manage users
- `/account/profile` - profile
- `/account/change-password` - password update

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create an environment file:

```powershell
Copy-Item .env.example .env
```

For local development, SQLite is used if `DATABASE_URL` is not set and `FLASK_ENV=development` or `FLASK_DEBUG=1`.

Run migrations:

```powershell
.\.venv\Scripts\python.exe -m flask --app main.py db upgrade
```

Seed dropdown defaults and the first admin account:

```powershell
.\.venv\Scripts\python.exe -m flask --app main.py seed-defaults
```

Run the app:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Production Environment

Set these values in the production server environment, not in source control:

```text
SECRET_KEY=your-fixed-long-random-secret
DATABASE_URL=postgresql+psycopg://user:password@host:5432/database
REDIS_URL=redis://host:6379/0
RATELIMIT_STORAGE_URI=redis://host:6379/0
WTF_CSRF_TIME_LIMIT=3600
```

Production notes:

- `SECRET_KEY` is required outside development.
- `DATABASE_URL` is required outside development.
- Redis or another persistent rate-limit backend is required outside development.
- `WTF_CSRF_TIME_LIMIT=3600` means CSRF form tokens expire after one hour.
- The app enables secure cookie settings outside development.
- Use migrations for database changes instead of manual table edits.

## Database Backups

Backup files are sensitive and must not be committed to Git. Generated backup files are ignored through `.gitignore`.

The backup script creates a timestamped PostgreSQL custom-format dump under `backups/database/`:

```powershell
.\.venv\Scripts\python.exe scripts\backup_database.py
```

The script expects `DATABASE_URL` and PostgreSQL client tools such as `pg_dump`.

## Verification Commands

```powershell
.\.venv\Scripts\python.exe -m compileall app migrations scripts
.\.venv\Scripts\python.exe -c "import json; json.load(open('app/translations/en.json', encoding='utf-8')); json.load(open('app/translations/bn.json', encoding='utf-8')); print('translations valid')"
.\.venv\Scripts\python.exe -m flask --app main.py routes
```

## Security Note

This showcase excludes private runtime files. Do not commit `.env`, SQLite databases, logs, uploaded files, generated reports, or production backups.

## License

MIT License. See `LICENSE`.
