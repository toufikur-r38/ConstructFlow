from flask import Flask, redirect, url_for, flash, request, g, session, render_template
from flask_wtf.csrf import CSRFError
from flask_login import current_user
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.exceptions import BadRequest, Forbidden, HTTPException, InternalServerError, MethodNotAllowed, NotFound
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import json
import time
from urllib.parse import urlencode, urlparse
from .config import Config
from .extensions import db, login_manager, csrf, cache, limiter, migrate
from .utils.logging_config import configure_logging
from .utils.i18n import current_language, normalize_language, supported_languages, translate as t


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Login settings
    login_manager.login_view = "auth.login"

    # Logging setup
    configure_logging(app)

    app.logger.info("Construction Ledger Application initialized successfully.")
    @app.template_filter('fromjson')
    def fromjson_filter(value):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return {}

    @app.template_global()
    def page_url(page, per_page=None):
        args = request.args.to_dict(flat=False)
        args['page'] = [str(page)]
        if per_page is not None:
            args['per_page'] = [str(per_page)]

        query_string = urlencode(args, doseq=True)
        base_url = url_for(request.endpoint, **(request.view_args or {}))
        return f"{base_url}?{query_string}" if query_string else base_url

    @app.context_processor
    def inject_i18n_helpers():
        from app.models import AVAILABLE_MODULES

        visible_modules = {}
        module_home_url = None
        if current_user and current_user.is_authenticated:
            visible_modules = {
                module_name: module_label
                for module_name, module_label in AVAILABLE_MODULES.items()
                if current_user.has_module(module_name)
            }
            if current_user.is_super_admin or len(visible_modules) > 1:
                module_home_url = url_for('module_hub')
            elif 'construction' in visible_modules:
                module_home_url = url_for('dashboard.index')
            else:
                module_home_url = url_for('account.profile')

        return {
            "t": t,
            "current_lang": current_language(),
            "supported_languages": supported_languages(),
            "available_modules": AVAILABLE_MODULES,
            "visible_modules": visible_modules,
            "module_home_url": module_home_url,
        }

    @app.route('/set-language/<lang>')
    def set_language(lang):
        session['lang'] = normalize_language(lang)
        return redirect(_safe_redirect_target())

    @app.route('/')
    @app.route('/modules')
    def module_hub():
        if not current_user or not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        from app.models import AVAILABLE_MODULES

        visible_modules = {
            module_name: module_label
            for module_name, module_label in AVAILABLE_MODULES.items()
            if current_user.has_module(module_name)
        }

        if not current_user.is_super_admin and len(visible_modules) == 1 and 'construction' in visible_modules:
            return redirect(url_for('dashboard.index'))

        module_overviews = {}
        if 'construction' in visible_modules:
            from app.modules.construction.services.dashboard_service import get_dashboard_math
            module_overviews['construction'] = get_dashboard_math()

        return render_template(
            'modules.html',
            visible_modules=visible_modules,
            module_overviews=module_overviews,
        )

    # Import models
    from . import models
    from .cli import register_cli_commands
    register_cli_commands(app)
    # Register blueprints
    from .modules.account.routes import account_bp
    from .modules.auth.routes import auth_bp
    from .modules.admin.routes import admin_bp
    from .modules.construction.routes.admin_actions import construction_admin_bp
    from .modules.construction.routes.dashboard import dashboard_bp
    from .modules.construction.routes.projects import projects_bp
    from .modules.construction.routes.costs import costs_bp
    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(construction_admin_bp, url_prefix='/construction')
    app.register_blueprint(dashboard_bp, url_prefix='/construction')
    app.register_blueprint(projects_bp, url_prefix='/construction')
    app.register_blueprint(costs_bp, url_prefix='/construction')

    # Error Handlers
    def _safe_redirect_target(default_endpoint='module_hub'):
        target = request.referrer or url_for(default_endpoint)
        parsed_target = urlparse(target)
        if parsed_target.netloc and parsed_target.netloc != request.host:
            return url_for(default_endpoint)
        return target

    def _render_error(status_code, title_key, message_key):
        return render_template(
            'error.html',
            status_code=status_code,
            title_key=title_key,
            message_key=message_key,
        ), status_code

    @app.errorhandler(CSRFError)
    def csrf_error_handler(e):
        logging.warning(
            "SECURITY: CSRF validation failed for %s %s from %s: %s",
            request.method,
            request.path,
            request.remote_addr,
            e.description,
        )
        flash("errors.csrf_expired", "warning")
        return redirect(url_for('auth.login') if not current_user.is_authenticated else _safe_redirect_target())

    @app.errorhandler(429)
    def ratelimit_handler(e):
        logging.warning(
            f"SECURITY: Rate limit exceeded by IP {request.remote_addr}"
        )

        flash("Too many requests. Please wait before trying again.", "danger")

        return redirect(_safe_redirect_target())

    @app.errorhandler(BadRequest)
    def bad_request_handler(e):
        logging.warning("Bad request at %s %s: %s", request.method, request.path, e)
        return _render_error(400, "errors.bad_request_title", "errors.bad_request_message")

    @app.errorhandler(Forbidden)
    def forbidden_handler(e):
        logging.warning("Forbidden request at %s %s: %s", request.method, request.path, e)
        return _render_error(403, "errors.forbidden_title", "errors.forbidden_message")

    @app.errorhandler(NotFound)
    def not_found_handler(e):
        return _render_error(404, "errors.not_found_title", "errors.not_found_message")

    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed_handler(e):
        logging.warning("Method not allowed at %s %s", request.method, request.path)
        return _render_error(405, "errors.method_not_allowed_title", "errors.method_not_allowed_message")

    @app.errorhandler(OperationalError)
    def database_connection_error_handler(e):
        db.session.rollback()
        logging.exception("Database connection error at %s %s", request.method, request.path)
        flash("errors.database_connection_lost", "danger")
        return redirect(_safe_redirect_target())

    @app.errorhandler(SQLAlchemyError)
    def database_error_handler(e):
        db.session.rollback()
        logging.exception("Database error at %s %s", request.method, request.path)
        return _render_error(500, "errors.database_error_title", "errors.database_error_message")

    @app.errorhandler(InternalServerError)
    def internal_server_error_handler(e):
        db.session.rollback()
        logging.exception("Internal server error at %s %s", request.method, request.path)
        return _render_error(500, "errors.server_error_title", "errors.server_error_message")

    @app.errorhandler(Exception)
    def unhandled_error_handler(e):
        if isinstance(e, HTTPException):
            return e
        db.session.rollback()
        logging.exception("Unhandled error at %s %s", request.method, request.path)
        return _render_error(500, "errors.server_error_title", "errors.server_error_message")

    @app.before_request
    def start_request_timer():
        g.request_started_at = time.perf_counter()
        if current_user and current_user.is_authenticated:
            g.request_user = current_user.username
            g.request_role = current_user.role
            construction_endpoints = ('dashboard.', 'projects.', 'costs.', 'construction_admin.')
            if request.endpoint and request.endpoint.startswith(construction_endpoints):
                if not current_user.has_module('construction'):
                    logging.warning(
                        "SECURITY: '%s' (Role: %s) attempted unauthorized construction module access to %s",
                        current_user.username,
                        current_user.role,
                        request.path,
                    )
                    flash("flash.no_construction_module_access", "danger")
                    return redirect(url_for('account.profile'))
        else:
            g.request_user = 'anonymous'
            g.request_role = '-'

    # Security headers
    @app.after_request
    def security_headers(response):
        if request.endpoint != 'static':
            duration_ms = (time.perf_counter() - g.get('request_started_at', time.perf_counter())) * 1000
            logging.getLogger('construction.access').info(
                "HTTP %s %s completed with %s in %.2f ms",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )

        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://code.jquery.com; "
            "font-src 'self' data: https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        if not app.config.get('IS_DEVELOPMENT'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    return app
