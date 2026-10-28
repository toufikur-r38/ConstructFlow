import os

import click
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User, UserModule
from app.modules.construction.utils.dropdown_options import seed_dropdown_options


def register_cli_commands(app):
    @app.cli.command("seed-defaults")
    def seed_defaults():
        """Seed dropdown defaults and create the first admin account if needed."""
        default_admin_username = os.getenv('DEFAULT_ADMIN_USERNAME', '').strip()
        default_admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', '')
        if not default_admin_username or not default_admin_password.strip():
            raise click.ClickException(
                "Set DEFAULT_ADMIN_USERNAME and DEFAULT_ADMIN_PASSWORD in your environment or .env file."
            )
        if len(default_admin_username) > 50:
            raise click.ClickException("DEFAULT_ADMIN_USERNAME must be at most 50 characters.")

        seed_dropdown_options()

        if User.query.filter_by(username=default_admin_username).first():
            click.echo("Admin user already exists.")
            return

        admin_user = User(
            username=default_admin_username,
            full_name='System Administrator',
            password=generate_password_hash(default_admin_password, method='pbkdf2:sha256'),
            role='admin',
            is_super_admin=True,
        )
        admin_user.module_access.append(UserModule(module_name='construction'))

        db.session.add(admin_user)
        db.session.commit()

        click.echo("Default admin created.")

