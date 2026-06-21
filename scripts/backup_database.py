import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv


BACKUP_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+_(\d{4}-\d{2}-\d{2})_\d{6}\.dump$")


def _load_environment():
    if os.environ.get("FLASK_ENV") != "production":
        load_dotenv()


def _postgres_client_url(database_url):
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to create a database backup.")

    return (
        database_url
        .replace("postgresql+psycopg://", "postgresql://", 1)
        .replace("postgresql+psycopg2://", "postgresql://", 1)
    )


def _database_name(database_url):
    path = urlsplit(database_url).path.strip("/")
    return path or "database"


def _backup_file_path(backup_dir, database_url):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    db_name = re.sub(r"[^A-Za-z0-9_-]+", "_", _database_name(database_url))
    return backup_dir / f"{db_name}_{timestamp}.dump"


def _pretty_size(size_bytes):
    units = ("bytes", "KB", "MB", "GB")
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "bytes" else f"{int(value)} bytes"
        value /= 1024
    return f"{size_bytes} bytes"


def _run_pg_dump(database_url, backup_path):
    pg_dump = os.environ.get("PG_DUMP_PATH") or shutil.which("pg_dump")
    if not pg_dump:
        raise RuntimeError(
            "pg_dump was not found. Install PostgreSQL client tools and make sure pg_dump is on PATH, "
            "or set PG_DUMP_PATH to the full pg_dump executable path."
        )

    command = [
        pg_dump,
        "--format=custom",
        "--no-owner",
        "--no-privileges",
        "--file",
        str(backup_path),
        database_url,
    ]

    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "pg_dump failed without an error message.")


def _monthly_key(path):
    match = BACKUP_NAME_RE.match(path.name)
    if not match:
        return None
    return match.group(1)[:7]


def _cleanup_retention(backup_dir, retention_days, keep_monthly):
    now = datetime.now(timezone.utc)
    matching_files = []
    for path in backup_dir.glob("*.dump"):
        if BACKUP_NAME_RE.match(path.name):
            matching_files.append(path)

    monthly_kept = set()
    deleted = []

    for path in sorted(matching_files, key=lambda item: item.stat().st_mtime, reverse=True):
        file_time = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        age_days = (now - file_time).days
        month = _monthly_key(path)

        if age_days <= retention_days:
            continue

        if month and month not in monthly_kept and len(monthly_kept) < keep_monthly:
            monthly_kept.add(month)
            continue

        path.unlink()
        deleted.append(path)

    return deleted


def main():
    try:
        _load_environment()
        source_url = os.environ.get("DATABASE_URL")
        client_url = _postgres_client_url(source_url)
        backup_dir = Path(os.environ.get("BACKUP_DIR", "backups/database"))
        retention_days = int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
        keep_monthly = int(os.environ.get("BACKUP_KEEP_MONTHLY", "12"))

        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = _backup_file_path(backup_dir, client_url)

        _run_pg_dump(client_url, backup_path)

        if not backup_path.exists() or backup_path.stat().st_size == 0:
            raise RuntimeError("Backup file was not created or is empty.")

        deleted_files = _cleanup_retention(backup_dir, retention_days, keep_monthly)
        size = _pretty_size(backup_path.stat().st_size)

        print("Backup completed successfully.")
        print(f"File: {backup_path.resolve()}")
        print(f"Size: {size}")
        if deleted_files:
            print(f"Retention cleanup removed {len(deleted_files)} old backup file(s).")
        else:
            print("Retention cleanup removed 0 old backup files.")
        return 0
    except Exception as exc:
        print(f"Backup failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
