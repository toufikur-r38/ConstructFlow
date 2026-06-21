from datetime import timedelta, timezone

from flask_login import UserMixin

from app.extensions import db

BD_TZ = timezone(timedelta(hours=6))

AVAILABLE_MODULES = {
    "construction": "Construction",
}


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    # Added unique index for faster login lookups
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # DB-level validation for roles
    role = db.Column(db.String(20), nullable=False, default="operator")
    is_super_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "role IN ('admin', 'operator', 'viewer')",
            name="check_user_role",
        ),
    )

    def has_module(self, module_name):
        if self.is_super_admin:
            return True
        return any(module.module_name == module_name for module in self.module_access)

    def module_names(self):
        return [module.module_name for module in self.module_access]

    def can_manage_system(self):
        return self.is_super_admin


class UserModule(db.Model):
    __tablename__ = "user_module"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    module_name = db.Column(db.String(50), nullable=False, index=True)

    user = db.relationship(
        "User",
        backref=db.backref("module_access", lazy=True, cascade="all, delete-orphan"),
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "module_name", name="uq_user_module_access"),
    )
