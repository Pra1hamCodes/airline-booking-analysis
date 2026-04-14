import structlog
from flask import Flask, jsonify

from .extensions import db, migrate, login_manager, bcrypt, jwt, limiter, cache, mail, cors, csrf


def create_app(config_name="default"):
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config as config_map

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    if app.debug or app.testing:
        limiter.enabled = False
    cache.init_app(app)
    mail.init_app(app)
    cors.init_app(app, origins=app.config.get("CORS_ORIGINS", []))
    csrf.init_app(app)

    # Import models so they are registered with SQLAlchemy
    from .models import user, flight, alert, notification  # noqa: F401

    # Register blueprints
    from .api.v1 import api_v1_bp
    csrf.exempt(api_v1_bp)
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")

    from .auth import auth_bp
    csrf.exempt(auth_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    # Sentry
    sentry_dsn = app.config.get("SENTRY_DSN")
    if sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(dsn=sentry_dsn, integrations=[FlaskIntegration()])

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if not app.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e.description)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Rate limit exceeded", "message": str(e.description)}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    # CLI commands
    @app.cli.command("seed")
    def seed_data():
        """Generate and persist initial flight data."""
        import click
        from app.services.data_processor import DataProcessor

        processor = DataProcessor()
        flights = processor.scraper.generate_flights(count=200)
        run_id = processor.persist_flights(flights)
        processor.update_route_aggregates()
        processor.detect_anomalies()
        click.echo(f"Seeded 200 flights with run_id={run_id}")
        click.echo("Route aggregates updated. Anomaly detection complete.")

    @app.cli.command("init-db")
    def init_db():
        """Create all tables."""
        import click
        db.create_all()
        click.echo("Database tables created.")

    return app
