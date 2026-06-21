import json
import re
from functools import lru_cache
from pathlib import Path

from flask import current_app, session

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {
    "en": "English",
    "bn": "বাংলা",
}

# Temporary bridge while templates move from phrase keys to namespaced JSON keys.
LEGACY_KEY_MAP = {
    "Dashboard": "common.dashboard",
    "Project Ledger": "common.project_ledger",
    "Add Project": "common.add_project",
    "Cost Entry": "common.cost_entry",
    "Reports": "common.reports",
    "Dropdown Items": "common.dropdown_items",
    "Add User": "common.add_user",
    "Audit Log": "common.audit_log",
    "Construction": "modules.construction",
    "My Profile": "common.my_profile",
    "Change Password": "common.change_password",
    "Toggle Theme": "common.toggle_theme",
    "Logout": "common.logout",
    "Language": "common.language",
    "English": "common.english",
    "Bangla": "common.bangla",
    "Switch to dark mode": "common.switch_to_dark_mode",
    "Switch to light mode": "common.switch_to_light_mode",
    "Toggle dark mode": "common.toggle_dark_mode",
    "Too many requests. Please wait before trying again.": "auth.too_many_requests",
    "Welcome back, {name}!": "auth.welcome_back",
    "Your account has been deactivated. Contact the Admin.": "auth.deactivated_account",
    "Invalid username or password.": "auth.invalid_credentials",
    "Secure Workspace": "auth.secure_workspace",
    "Sign in to continue": "auth.sign_in_to_continue",
    "Verify your credentials to access the ConstructFlow project tracker.": "auth.login_intro",
    "Username": "auth.username",
    "Password": "auth.password",
    "Enter username": "auth.enter_username",
    "Enter password": "auth.enter_password",
    "Verify & Login": "auth.verify_login",
    "Verifying...": "auth.verifying",
    "Verifying credentials": "auth.verifying_credentials",
    "Please wait while we securely check your access.": "auth.verifying_access",
    "Authorized staff access only. All activity is logged.": "auth.authorized_access_only",
    "Construction Project Cost Management for project ledgers, cost tracking, reporting, and audit control.": "common.app_subtitle",
    "For locked accounts or lost credentials, contact the system administrator.": "auth.login_help",
    "Show password": "auth.show_password",
    "Hide password": "auth.hide_password",
    "Admin Dashboard": "dashboard.admin_title",
    "Operator Dashboard": "dashboard.operator_title",
    "Viewer Dashboard": "dashboard.viewer_title",
    "Live Financial Status": "dashboard.live_financial_status",
    "Running Projects": "dashboard.running_projects",
    "Expenses This Month": "dashboard.expenses_this_month",
    "Expenses Today": "dashboard.expenses_today",
    "Budget Alerts": "dashboard.budget_alerts",
    "Admin Actions": "dashboard.admin_actions",
    "Quick Actions": "dashboard.quick_actions",
    "Available Information": "dashboard.available_information",
    "Add New Project": "dashboard.add_new_project",
    "Register a new contract": "dashboard.register_new_contract",
    "View all project details": "dashboard.view_all_project_details",
    "View all project status and details": "dashboard.view_all_project_status_details",
    "Daily Cost Entry": "dashboard.daily_cost_entry",
    "Log materials & expenses": "dashboard.log_materials_expenses",
    "Financial Reports": "dashboard.financial_reports",
    "View categorized spending": "dashboard.view_categorized_spending",
    "View categorized project spending": "dashboard.view_categorized_project_spending",
    "Add Authorized User": "dashboard.add_authorized_user",
    "Create new team login": "dashboard.create_team_login",
    "View all edits and voided records": "dashboard.view_edits_voids",
    "Manage sectors and cost types": "dashboard.manage_sectors_cost_types",
    "Active Projects Breakdown": "dashboard.active_projects_breakdown",
    "Project Name": "dashboard.project_name",
    "Total Budget": "dashboard.total_budget",
    "Cost Spent": "dashboard.cost_spent",
    "Budget Left": "dashboard.budget_left",
    "Budget Used": "dashboard.budget_used",
    "No active projects found.": "dashboard.no_active_projects",
    "Add one now.": "dashboard.add_one_now",
    "Unauthorized. Admins only.": "flash.unauthorized_admins_only",
    "Unauthorized. Only Admins and Operators can modify data.": "flash.unauthorized_write_access",
    "Current password is incorrect. No changes were made.": "flash.current_password_incorrect",
    "New password must be at least 8 characters.": "flash.password_min_length",
    "New password and confirmation do not match.": "flash.password_mismatch",
    "Your password has been updated successfully.": "flash.password_updated",
    "All fields are required.": "flash.all_fields_required",
    "Invalid role selected.": "flash.invalid_role",
    "Username already taken. Please choose another.": "flash.username_taken",
    "User not found.": "flash.user_not_found",
    "You cannot remove your own Admin privileges.": "flash.cannot_remove_own_admin",
    "You cannot deactivate your own account.": "flash.cannot_deactivate_self",
    "Authentication failed. Incorrect password. No changes were made.": "flash.auth_failed_no_changes",
    "Authentication Failed! Incorrect password. No changes were made.": "flash.auth_failed_no_changes",
    "Project name is required.": "flash.project_name_required",
    "Please select a valid project sector from the managed dropdown list.": "flash.invalid_project_sector",
    "Invalid NOA date. Please use YYYY-MM-DD format.": "flash.invalid_noa_date",
    "Work order year must be a 4-digit year (e.g. 2024) or range (e.g. 2023-2024).": "flash.invalid_work_order_year",
    "Invalid contract price. Please enter a positive number.": "flash.invalid_contract_price",
    "New project saved successfully!": "flash.project_saved",
    "Date is required.": "flash.date_required",
    "Invalid date format. Please use YYYY-MM-DD.": "flash.invalid_date_format",
    "Invalid completion date format. Please use YYYY-MM-DD.": "flash.invalid_completion_date_format",
    "Please select a valid project.": "flash.select_valid_project",
    "Selected project does not exist or has been voided.": "flash.project_missing_or_voided",
    "Costs can only be added to running projects.": "flash.costs_running_only",
    "Cost type is required.": "flash.cost_type_required",
    "Please select a valid cost type from the managed dropdown list.": "flash.invalid_cost_type",
    "Invalid quantity. Please enter a valid number.": "flash.invalid_quantity",
    "Invalid unit rate. Please enter a valid number.": "flash.invalid_unit_rate",
    "Cost entry saved successfully!": "flash.cost_saved",
    "Late costs are only needed for completed projects.": "flash.late_cost_completed_only",
    "A clear remark is required for late costs on completed projects.": "flash.late_cost_remark_required",
    "Late cost entry saved successfully!": "flash.late_cost_saved",
    "Invalid project filter selected.": "flash.invalid_project_filter",
    "Invalid start date format.": "flash.invalid_start_date",
    "Invalid end date format.": "flash.invalid_end_date",
    "Please select at least one filter before generating a PDF report.": "flash.select_filter_for_pdf",
    "Invalid start date selected for PDF export.": "flash.invalid_pdf_start_date",
    "Invalid end date selected for PDF export.": "flash.invalid_pdf_end_date",
    "PDF export end date cannot be before start date.": "flash.pdf_end_before_start",
    "Project not found.": "flash.project_not_found",
    "This project is already voided.": "flash.project_already_voided",
    "A reason for voiding is required.": "flash.project_void_reason_required",
    "Completion date is required when project status is Completed.": "flash.completion_date_required",
    "No changes detected. Nothing was updated.": "flash.no_changes",
    "Entry not found.": "flash.entry_not_found",
    "This entry has already been voided.": "flash.entry_already_voided",
    "A reason is required to void an entry.": "flash.entry_void_reason_required",
    "Cost entry has been successfully restored.": "flash.cost_restored",
    "Cost entry not found.": "flash.cost_not_found",
    "Invalid project selected.": "flash.invalid_project_selected",
    "Selected project does not exist.": "flash.selected_project_missing",
    "Costs cannot be moved to a voided project. Restore the project first.": "flash.cost_move_voided_project",
    "Changes saved and audit log updated.": "flash.changes_saved_audit",
    "Invalid dropdown type selected.": "flash.invalid_dropdown_type",
    "Option name is required.": "flash.option_name_required",
    "Option name must be 100 characters or fewer.": "flash.option_name_too_long",
}

VALUE_KEY_MAP = {
    "Project name": "flash.value.project_name",
    "Sector": "flash.value.sector",
    "Firm name": "flash.value.firm_name",
    "Tender ID": "flash.value.tender_id",
    "Address": "flash.value.address",
    "Cost type": "flash.value.cost_type",
    "Remarks": "flash.value.remarks",
    "Running": "project.running",
    "Completed": "project.completed",
    "On Hold": "edit_project.on_hold",
    "activated": "flash.value.activated",
    "deactivated": "flash.value.deactivated",
    "ADMIN": "admin.admin_role",
    "OPERATOR": "admin.operator_role",
    "VIEWER": "admin.viewer_role",
    "admin": "admin.admin_role",
    "operator": "admin.operator_role",
    "viewer": "admin.viewer_role",
    "Project Sector": "dropdown.project_sector",
    "Cost Type": "dropdown.cost_type",
    "Dropdown option": "dropdown.dropdown_item",
    "save this project": "flash.action.save_this_project",
    "save this cost entry": "flash.action.save_this_cost_entry",
    "save this late cost entry": "flash.action.save_this_late_cost_entry",
    "save your project changes": "flash.action.save_your_project_changes",
    "save your cost changes": "flash.action.save_your_cost_changes",
}

REGEX_KEY_MAP = (
    (re.compile(r"^(?P<field>.+) must be (?P<limit>\d+) characters or fewer\.$"), "flash.field_too_long"),
    (re.compile(r"^User '(?P<name>.+)' created successfully as (?P<role>.+)!$"), "flash.user_created_as"),
    (re.compile(r"^User '(?P<name>.+)' updated successfully\.$"), "flash.user_updated"),
    (re.compile(r"^User '(?P<name>.+)' has been (?P<status>activated|deactivated)\.$"), "flash.user_status_changed"),
    (re.compile(r"^A project named '(?P<project>.+)' with Tender ID '(?P<tender>.*)' already exists\.$"), "flash.duplicate_project"),
    (re.compile(r"^Project '(?P<project>.+)' and (?P<count>\d+) linked cost entries have been successfully voided\.$"), "flash.project_voided_with_costs"),
    (re.compile(r"^An error occurred during the voiding process: (?P<error>.+)$"), "flash.voiding_error"),
    (re.compile(r"^Project '(?P<project>.+)' and (?P<count>\d+) linked costs have been successfully restored\.$"), "flash.project_restored_with_costs"),
    (re.compile(r"^Invalid status\. Allowed values: (?P<statuses>.+)\.$"), "flash.invalid_status_allowed"),
    (re.compile(r"^Project '(?P<project>.+)' updated and audit log saved\.$"), "flash.project_updated_audit"),
    (re.compile(r"^Entry from (?P<date>.+) has been successfully voided\.$"), "flash.entry_voided_date"),
    (re.compile(r"^An error occurred while voiding the cost entry: (?P<error>.+)$"), "flash.cost_void_error"),
    (re.compile(r"^First restore the project '(?P<project>.+)', then restore this cost\.$"), "flash.restore_project_first"),
    (re.compile(r"^(?P<option_type>Project Sector|Cost Type) '(?P<name>.+)' already exists\.$"), "flash.dropdown_exists"),
    (re.compile(r"^(?P<option_type>Project Sector|Cost Type) '(?P<name>.+)' added\.$"), "flash.dropdown_added"),
    (re.compile(r"^(?P<option_type>Project Sector|Cost Type|Dropdown option) '(?P<name>.+)' removed from future dropdowns\.$"), "flash.dropdown_removed"),
    (re.compile(r"^Could not (?P<action>.+) because the database connection was interrupted\. Please try again\.$"), "flash.db_connection_interrupted"),
    (re.compile(r"^Could not (?P<action>.+)\. One text field is too long\. Limits: (?P<limits>.+)\.$"), "flash.db_text_too_long_limits"),
    (re.compile(r"^Could not (?P<action>.+)\. One text field is too long\. Please shorten it and try again\.$"), "flash.db_text_too_long"),
    (re.compile(r"^Could not (?P<action>.+)\. Please check the amount, quantity, and rate values\.$"), "flash.db_numeric_error"),
    (re.compile(r"^Could not (?P<action>.+)\. Please check the entered values and try again\.$"), "flash.db_check_values"),
    (re.compile(r"^Could not (?P<action>.+)\. A project with the same name and tender ID already exists\.$"), "flash.db_duplicate_project"),
    (re.compile(r"^Could not (?P<action>.+)\. A selected linked record no longer exists\. Please refresh and try again\.$"), "flash.db_linked_record_missing"),
    (re.compile(r"^Could not (?P<action>.+)\. A required field is missing\.$"), "flash.db_required_missing"),
    (re.compile(r"^Could not (?P<action>.+)\. Please choose a valid project status\.$"), "flash.db_invalid_project_status"),
    (re.compile(r"^Could not (?P<action>.+)\. Contract price cannot be negative\.$"), "flash.db_negative_contract_price"),
    (re.compile(r"^Could not (?P<action>.+)\. Please check for duplicate or missing values\.$"), "flash.db_duplicate_or_missing"),
)


def normalize_language(lang):
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def current_language():
    return normalize_language(session.get("lang", DEFAULT_LANGUAGE))


def supported_languages():
    return SUPPORTED_LANGUAGES


def _translations_dir():
    if current_app:
        return Path(current_app.root_path) / "translations"
    return Path(__file__).resolve().parents[1] / "translations"


def _translation_file(lang):
    return _translations_dir() / f"{normalize_language(lang)}.json"


@lru_cache(maxsize=None)
def _load_language_from_path(path_string, modified_at):
    path = Path(path_string)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid translation JSON: {path}") from exc


def _load_language(lang):
    path = _translation_file(lang)
    modified_at = path.stat().st_mtime if path.exists() else 0
    translations = _load_language_from_path(str(path), modified_at)
    if translations is not None:
        return translations
    if lang != DEFAULT_LANGUAGE:
        return _load_language(DEFAULT_LANGUAGE)
    return {}


def _lookup(lang, key):
    translations = _load_language(lang)
    if key in translations:
        return translations[key]

    mapped_key = LEGACY_KEY_MAP.get(key)
    if mapped_key and mapped_key in translations:
        return translations[mapped_key]

    dynamic = _lookup_dynamic_message(lang, key, translations)
    if dynamic:
        return dynamic

    if lang != DEFAULT_LANGUAGE:
        return _lookup(DEFAULT_LANGUAGE, key)

    return key


def _translate_value(lang, value):
    mapped_key = VALUE_KEY_MAP.get(value)
    if mapped_key:
        return _lookup(lang, mapped_key)
    if ", " in value:
        return ", ".join(_translate_value(lang, part) for part in value.split(", "))
    limit_match = re.match(r"^(?P<field>.+) max (?P<limit>\d+) characters$", value)
    if limit_match:
        return _lookup(lang, "flash.value.max_characters").format(
            field=_translate_value(lang, limit_match.group("field")),
            limit=limit_match.group("limit"),
        )
    return value


def _lookup_dynamic_message(lang, key, translations):
    for pattern, translation_key in REGEX_KEY_MAP:
        match = pattern.match(key)
        if not match or translation_key not in translations:
            continue

        values = {
            name: _translate_value(lang, value)
            for name, value in match.groupdict().items()
        }
        try:
            return translations[translation_key].format(**values)
        except (KeyError, ValueError):
            return translations[translation_key]
    return None


def translate(key, **kwargs):
    text = _lookup(current_language(), key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text
