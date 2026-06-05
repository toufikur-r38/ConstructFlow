from flask import Flask, redirect, url_for, flash, request, g
from flask_login import current_user
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import json
import time
from urllib.parse import urlencode
from .config import Config
from .extensions import db, login_manager, csrf, cache, limiter, migrate
from .utils.logging_config import configure_logging


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
    app.register_blueprint(construction_admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(costs_bp)

    # Error Handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logging.warning(
            f"SECURITY: Rate limit exceeded by IP {request.remote_addr}"
        )

        flash(
            "Too many requests. Please wait before trying again.",
            "danger"
        )

        return redirect(url_for("dashboard.index"))

    @app.before_request
    def start_request_timer():
        g.request_started_at = time.perf_counter()
        if current_user and current_user.is_authenticated:
            g.request_user = current_user.username
            g.request_role = current_user.role
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
