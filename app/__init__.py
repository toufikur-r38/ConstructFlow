from flask import Flask, redirect, url_for, flash, request, g
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import json
import time
from .config import Config
from .extensions import db, login_manager, csrf, cache, limiter
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
    # Import models
    from . import models
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
        return response

    return app
