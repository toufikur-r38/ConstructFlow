import os
import secrets

import click
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User, UserModule
from app.modules.construction.utils.dropdown_options import seed_dropdown_options


def register_cli_commands(app):
    @app.cli.command("seed-defaults")
    def seed_defaults():
        """Seed dropdown defaults and create the first admin account if needed."""
        seed_dropdown_options()

        if User.query.filter_by(username='admin').first():
            click.echo("Admin user already exists.")
            return

        default_admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD') or secrets.token_urlsafe(18)
        admin_user = User(
            username='admin',
            full_name='System Administrator',
            password=generate_password_hash(default_admin_password, method='pbkdf2:sha256'),
            role='admin',
            is_super_admin=True,
        )
        admin_user.module_access.append(UserModule(module_name='construction'))

        db.session.add(admin_user)
        db.session.commit()

        click.echo("Default admin created.")
        if not os.getenv('DEFAULT_ADMIN_PASSWORD'):
            click.echo(f"Generated default admin password: {default_admin_password}")

