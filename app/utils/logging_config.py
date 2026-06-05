import logging
import os
from logging.handlers import RotatingFileHandler

from flask import g, has_request_context, request
from flask_login import current_user


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.method = request.method
            record.path = request.path
            record.remote_addr = request.remote_addr or '-'
            record.endpoint = request.endpoint or '-'
            if hasattr(g, 'request_user'):
                record.user = g.request_user
                record.role = g.request_role
            elif current_user and current_user.is_authenticated:
                record.user = current_user.username
                record.role = current_user.role
            else:
                record.user = 'anonymous'
                record.role = '-'
        else:
            record.method = '-'
            record.path = '-'
            record.remote_addr = '-'
            record.endpoint = '-'
            record.user = 'system'
            record.role = '-'
        return True


class ErrorOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR


class SecurityFilter(logging.Filter):
    SECURITY_KEYWORDS = (
        'SECURITY',
        'Successful login',
        'Failed login',
        'logged out',
        'Authentication failed',
        'Authentication Failed',
        'Unauthorized',
        'Rate limit exceeded',
    )

    def filter(self, record):
        message = record.getMessage()
        return (
            record.name == 'construction.security'
            or any(keyword in message for keyword in self.SECURITY_KEYWORDS)
        )


class AuditFilter(logging.Filter):
    AUDIT_KEYWORDS = (
        'ADMIN ACTION',
        'SECURITY AUDIT',
        'added cost entry',
        'created project',
        'created a new',
        'edited Cost',
        'edited Project',
        'voided Project',
    )

    def filter(self, record):
        message = record.getMessage()
        return (
            record.name == 'construction.audit'
            or any(keyword in message for keyword in self.AUDIT_KEYWORDS)
        )


def _rotating_handler(log_dir, filename, formatter, level=logging.INFO, extra_filter=None):
    handler = RotatingFileHandler(
        os.path.join(log_dir, filename),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)
    handler.addFilter(RequestContextFilter())
    if extra_filter:
        handler.addFilter(extra_filter)
    return handler


def configure_logging(app):
    log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../logs')
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] user=%(user)s role=%(role)s ip=%(remote_addr)s '
        '%(method)s %(path)s %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    root_logger.addHandler(_rotating_handler(log_dir, 'app.log', formatter))
    root_logger.addHandler(_rotating_handler(log_dir, 'errors.log', formatter, logging.ERROR, ErrorOnlyFilter()))
    root_logger.addHandler(_rotating_handler(log_dir, 'security.log', formatter, logging.INFO, SecurityFilter()))
    root_logger.addHandler(_rotating_handler(log_dir, 'audit.log', formatter, logging.INFO, AuditFilter()))

    access_logger = logging.getLogger('construction.access')
    access_logger.handlers.clear()
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False
    access_logger.addHandler(_rotating_handler(log_dir, 'access.log', formatter))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(RequestContextFilter())
    root_logger.addHandler(console_handler)

    app.logger.handlers.clear()
    app.logger.propagate = True
    app.logger.setLevel(logging.INFO)

    app.logger.info("Logging initialized with separate app, access, security, audit, and error files.")
