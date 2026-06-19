from sqlalchemy.exc import DataError, IntegrityError, OperationalError


def _format_text_limits(text_limits):
    if not text_limits:
        return None

    return ", ".join(
        f"{field} max {limit} characters"
        for field, limit in text_limits
    )


def friendly_database_error(error, action, text_limits=None):
    """Return a user-safe explanation for common database failures."""
    message = str(getattr(error, "orig", error)).lower()

    if isinstance(error, OperationalError):
        return f"Could not {action} because the database connection was interrupted. Please try again."

    if isinstance(error, DataError):
        if "value too long" in message or "string data" in message:
            limits = _format_text_limits(text_limits)
            if limits:
                return f"Could not {action}. One text field is too long. Limits: {limits}."
            return f"Could not {action}. One text field is too long. Please shorten it and try again."
        if "numeric" in message or "decimal" in message:
            return f"Could not {action}. Please check the amount, quantity, and rate values."
        return f"Could not {action}. Please check the entered values and try again."

    if isinstance(error, IntegrityError):
        if "uq_project_tender" in message or "unique" in message:
            return f"Could not {action}. A project with the same name and tender ID already exists."
        if "foreign key" in message:
            return f"Could not {action}. A selected linked record no longer exists. Please refresh and try again."
        if "not null" in message:
            return f"Could not {action}. A required field is missing."
        if "check_project_status" in message:
            return f"Could not {action}. Please choose a valid project status."
        if "check_positive_contract_price" in message:
            return f"Could not {action}. Contract price cannot be negative."
        return f"Could not {action}. Please check for duplicate or missing values."

    return f"Could not {action}. Please check the entered values and try again."
