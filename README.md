# ConstructFlow

ConstructFlow is a Flask-based construction project cost tracker for project ledgers, expenditure entries, PDF reporting, audit trails, user roles, and managed dropdown options.

This repository is a public showcase version. It does not include production secrets, private database files, logs, uploads, or real project data.

## Features

- Role-based dashboards for admin, operator, and viewer users
- Project ledger with completed project visibility
- Cost entry management with edit, void, and restore workflows
- Password confirmation for sensitive actions
- Managed project sector and cost type dropdowns
- Filtered cost views with PDF export confirmation
- Audit, security, access, error, and app logging setup
- CSRF protection, rate limiting, and environment-based configuration

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Limiter
- Flask-Caching
- ReportLab
- SQLite for local development

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set your own values.
4. Run the app:

```bash
python main.py
```

The app creates a local SQLite database on first run. Keep that database out of Git.

## Environment Variables

See `.env.example` for the required variables. Use a strong password and a strong secret key for any real deployment.

## Security Note

This showcase excludes private runtime files. Do not commit `.env`, SQLite databases, logs, uploaded files, generated reports, or production backups.

## Screenshots

Add screenshots of the login page, dashboard, project ledger, cost view, dropdown management, and PDF export flow before publishing the repo widely.

## License

MIT License. See `LICENSE`.
