from datetime import datetime

from app.extensions import db

from .core import BD_TZ


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    sector = db.Column(db.String(100), index=True)
    firm_name = db.Column(db.String(200))
    tender_id = db.Column(db.String(100), index=True)
    noa_date = db.Column(db.Date, nullable=True)
    work_order_year = db.Column(db.String(50), index=True)

    # REPLACED FLOAT WITH NUMERIC (15 digits total, 2 after decimal)
    contract_price = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)

    address = db.Column(db.String(500))
    additional_details = db.Column(db.Text)  # Changed to Text for large data
    status = db.Column(db.String(20), default="Running", index=True, nullable=False)
    completion_date = db.Column(db.Date, nullable=True, index=True)
    is_void = db.Column(db.Boolean, default=False, index=True, nullable=False)
    logged_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(BD_TZ).replace(tzinfo=None),
    )

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    # CASCADE RULES: If a project is deleted, clean up its logs and costs
    creator = db.relationship("User", backref="projects_created")
    costs = db.relationship(
        "CostEntry",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # UNIQUE CONSTRAINT: Prevent duplicate Project Names for the same Tender ID
        db.UniqueConstraint("project_name", "tender_id", name="uq_project_tender"),
        # VALIDATION: Price cannot be negative
        db.CheckConstraint("contract_price >= 0", name="check_positive_contract_price"),
        db.CheckConstraint(
            "status IN ('Running', 'Completed', 'On Hold')",
            name="check_project_status",
        ),
        db.Index("ix_project_status_void", "status", "is_void"),
    )


class CostEntry(db.Model):
    __tablename__ = "cost_entry"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id"),
        nullable=False,
        index=True,
    )
    date = db.Column(db.Date, nullable=False, index=True)
    cost_type = db.Column(db.String(50), nullable=False, index=True)

    # REPLACED FLOAT WITH NUMERIC
    quantity = db.Column(db.Numeric(15, 2), default=0.00)
    unit_rate = db.Column(db.Numeric(15, 2), default=0.00)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)

    remarks = db.Column(db.String(500))
    logged_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(BD_TZ).replace(tzinfo=None),
    )
    is_void = db.Column(db.Boolean, default=False, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    user = db.relationship("User", backref="costs_logged")

    __table_args__ = (
        db.Index("ix_cost_project_void_date", "project_id", "is_void", "date"),
        db.Index("ix_cost_void_date", "is_void", "date"),
        db.Index("ix_cost_project_type_date", "project_id", "cost_type", "date"),
    )


class DropdownOption(db.Model):
    __tablename__ = "dropdown_option"

    id = db.Column(db.Integer, primary_key=True)
    option_type = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(BD_TZ).replace(tzinfo=None),
    )
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)

    creator = db.relationship("User", backref="dropdown_options_created")

    __table_args__ = (
        db.UniqueConstraint("option_type", "name", name="uq_dropdown_option_type_name"),
        db.CheckConstraint(
            "option_type IN ('project_sector', 'cost_type')",
            name="check_dropdown_option_type",
        ),
    )


class ProjectEditLog(db.Model):
    __tablename__ = "project_edit_log"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    changed_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    changed_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(BD_TZ).replace(tzinfo=None),
        index=True,
    )
    project_name_snapshot = db.Column(db.String(200))

    # Snapshots stored as JSON strings
    before_snapshot = db.Column(db.Text, nullable=False)
    after_snapshot = db.Column(db.Text, nullable=False)

    editor = db.relationship("User", backref="project_edits")
    project_rel = db.relationship(
        "Project",
        backref=db.backref("edit_logs", cascade="all, delete-orphan"),
    )


class ProjectDeletedLog(db.Model):
    __tablename__ = "project_deleted_log"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=False, index=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    deleted_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(BD_TZ).replace(tzinfo=None),
        index=True,
    )
    project_snapshot = db.Column(db.Text, nullable=False)  # JSON
    costs_voided_count = db.Column(db.Integer, default=0)
    void_reason = db.Column(db.String(500), nullable=False)

    remover = db.relationship("User", backref="project_deletions")


class EditLog(db.Model):
    __tablename__ = "edit_log"

    id = db.Column(db.Integer, primary_key=True)
    cost_id = db.Column(db.Integer, nullable=False, index=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    changed_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(BD_TZ).replace(tzinfo=None),
        index=True,
    )
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    project_name_snapshot = db.Column(db.String(200))
    before_snapshot = db.Column(db.Text, nullable=False)
    after_snapshot = db.Column(db.Text, nullable=False)

    editor = db.relationship("User", backref="edits")


class DeletedLog(db.Model):
    __tablename__ = "deleted_log"

    id = db.Column(db.Integer, primary_key=True)
    cost_id = db.Column(db.Integer, nullable=True, index=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    deleted_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(BD_TZ).replace(tzinfo=None),
        index=True,
    )
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    project_name_snapshot = db.Column(db.String(200), nullable=False)
    data_snapshot = db.Column(db.Text, nullable=False)
    void_reason = db.Column(db.String(500))

    remover = db.relationship("User", backref="deletions")
