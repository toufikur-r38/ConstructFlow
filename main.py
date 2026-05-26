import os
import secrets
from dotenv import load_dotenv

from app import create_app
from app.extensions import db
from app.models import User
from app.utils.dropdown_options import seed_dropdown_options
from werkzeug.security import generate_password_hash

load_dotenv()

app = create_app()

with app.app_context():
    db.create_all()
    seed_dropdown_options()

    if not User.query.filter_by(username='admin').first():
        default_admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD') or secrets.token_urlsafe(18)
        admin_user = User(
            username='admin',
            full_name='System Administrator',
            password=generate_password_hash(
                default_admin_password,
                method='pbkdf2:sha256'
            ),
            role='admin'
        )

        db.session.add(admin_user)
        db.session.commit()

        print("Default admin created.")
        if not os.getenv('DEFAULT_ADMIN_PASSWORD'):
            print(f"Generated default admin password: {default_admin_password}")

if __name__ == "__main__":
    app.run(debug=True)

