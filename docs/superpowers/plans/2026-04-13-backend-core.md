# Backend Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete Flask backend with app factory, all database models, realistic data generation, demand scoring, REST API endpoints, authentication, and security hardening.

**Architecture:** Flask 3.x app factory with blueprints (api_v1, auth, dashboard). SQLAlchemy models for flights, routes, users, alerts, notifications. Services layer for data generation/processing. Flask-RESTX for auto-documented API. Flask-Login + Flask-JWT-Extended for dual auth (session + JWT). Flask-Limiter + Flask-Bcrypt + bleach for security.

**Tech Stack:** Python 3.11+, Flask 3.x, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-Bcrypt, Flask-JWT-Extended, Flask-RESTX, Flask-Limiter, Flask-Caching, Flask-CORS, Flask-Mail, marshmallow, bleach, pandas, numpy, plotly, structlog, python-dotenv, cryptography

---

## File Structure

```
backend/
  app/
    __init__.py              # App factory: create_app(config_name)
    extensions.py            # All Flask extension instances
    models/
      __init__.py            # Import all models
      user.py                # User, Organization
      flight.py              # Flight, Route, PriceSnapshot, ForecastSnapshot
      alert.py               # AlertRule, AlertFired
      notification.py        # Notification
    services/
      __init__.py
      data_scraper.py        # DataScraper with realistic synthetic generation
      data_processor.py      # DataProcessor with anomaly detection
      demand_engine.py       # DemandScoreEngine
    api/
      v1/
        __init__.py          # Blueprint + Flask-RESTX Api
        routes.py            # /api/v1/routes endpoints
        prices.py            # /api/v1/prices endpoints
        insights.py          # /api/v1/insights endpoints (placeholder, no AI yet)
        alerts.py            # /api/v1/alerts CRUD
        export.py            # /api/v1/export CSV/Excel (no PDF yet)
    auth/
      __init__.py            # Auth blueprint
      routes.py              # register, login, logout, JWT refresh, password reset, email verify
    dashboard/
      __init__.py            # Dashboard blueprint
      routes.py              # Serve SPA catch-all
    utils/
      __init__.py
      security.py            # Input sanitization, token helpers, encryption
      validators.py          # Marshmallow schemas
      helpers.py             # Date utils, chart builders
  config.py                  # Config classes (Dev, Test, Prod)
  wsgi.py                    # Gunicorn entry point
  requirements.txt           # Production dependencies
  requirements-dev.txt       # Test/dev dependencies
  .env.example               # Placeholder env vars
  tests/
    conftest.py              # Fixtures: app, client, db, auth headers
    test_models.py           # Model creation, relationships, constraints
    test_services.py         # DataScraper, DemandScoreEngine tests
    test_api.py              # API endpoint tests
    test_auth.py             # Auth flow tests
```

---

### Task 1: Project scaffold and dependencies

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/.env.example`
- Create: `backend/config.py`

- [ ] **Step 1: Create backend directory structure**

```bash
cd d:/airline-booking-analysis-main
mkdir -p backend/app/models backend/app/services backend/app/api/v1 backend/app/auth backend/app/dashboard backend/app/utils backend/app/tasks backend/tests backend/migrations
```

- [ ] **Step 2: Write requirements.txt**

Create `backend/requirements.txt`:

```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.1.0
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
Flask-JWT-Extended==4.7.1
flask-restx==1.3.0
Flask-Limiter==3.12
Flask-Caching==2.3.1
Flask-CORS==5.0.1
Flask-Mail==0.10.0
Flask-WTF==1.2.2
marshmallow==3.25.1
bleach==6.2.0
pandas==2.2.3
numpy==2.2.4
plotly==6.0.1
scikit-learn==1.6.1
statsmodels==0.14.4
anthropic==0.52.0
structlog==25.1.0
python-dotenv==1.1.0
gunicorn==23.0.0
cryptography==44.0.2
celery[redis]==5.4.0
redis==5.2.1
APScheduler==3.11.0
sentry-sdk[flask]==2.22.0
WeasyPrint==63.1
openpyxl==3.1.5
```

- [ ] **Step 3: Write requirements-dev.txt**

Create `backend/requirements-dev.txt`:

```
-r requirements.txt
pytest==8.3.5
pytest-cov==6.1.1
pytest-flask==1.3.0
factory-boy==3.3.3
bandit==1.9.0
```

- [ ] **Step 4: Write .env.example**

Create `backend/.env.example`:

```bash
# Flask
SECRET_KEY=your-secret-key-here-minimum-32-chars
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///airline_data.db

# Redis (optional for dev)
REDIS_URL=redis://localhost:6379/0

# Anthropic (Claude API)
ANTHROPIC_API_KEY=your-anthropic-api-key

# AviationStack (optional)
AVIATIONSTACK_API_KEY=your-aviationstack-api-key

# Email (SendGrid, optional for dev)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# Encryption key for stored third-party API keys
ENCRYPTION_KEY=your-fernet-encryption-key-base64

# Frontend
CORS_ORIGINS=http://localhost:5173

# Sentry (optional)
SENTRY_DSN=
```

- [ ] **Step 5: Write config.py**

Create `backend/config.py`:

```python
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_DEFAULT = "1000/hour"

    # Caching
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = 300

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.sendgrid.net")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@example.com")

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Anthropic
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

    # AviationStack
    AVIATIONSTACK_API_KEY = os.environ.get("AVIATIONSTACK_API_KEY")

    # Encryption
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

    # Sentry
    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    # Celery
    CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///airline_data.db")
    CACHE_TYPE = "SimpleCache"
    RATELIMIT_STORAGE_URI = "memory://"
    JWT_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CACHE_TYPE = "SimpleCache"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_ENABLED = False
    JWT_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SERVER_NAME = "localhost"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    JWT_COOKIE_SECURE = True
    CACHE_TYPE = "RedisCache"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
```

- [ ] **Step 6: Commit**

```bash
cd d:/airline-booking-analysis-main
git init
git add backend/requirements.txt backend/requirements-dev.txt backend/.env.example backend/config.py
git commit -m "feat: add backend scaffold with dependencies and config"
```

---

### Task 2: Extensions and app factory

**Files:**
- Create: `backend/app/extensions.py`
- Create: `backend/app/__init__.py`
- Create: `backend/wsgi.py`

- [ ] **Step 1: Write extensions.py**

Create `backend/app/extensions.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_mail import Mail
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
mail = Mail()
cors = CORS()
csrf = CSRFProtect()
```

- [ ] **Step 2: Write app factory**

Create `backend/app/__init__.py`:

```python
import structlog
from flask import Flask, jsonify

from .extensions import db, migrate, login_manager, bcrypt, jwt, limiter, cache, mail, cors, csrf


def create_app(config_name="default"):
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
    cache.init_app(app)
    mail.init_app(app)
    cors.init_app(app, origins=app.config.get("CORS_ORIGINS", []))
    csrf.init_app(app)

    # Exempt API from CSRF (uses JWT)
    from .api.v1 import api_v1_bp
    csrf.exempt(api_v1_bp)

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

    # Register blueprints
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")

    from .auth import auth_bp
    csrf.exempt(auth_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

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

    return app
```

- [ ] **Step 3: Create minimal blueprint stubs so imports work**

Create `backend/app/api/__init__.py` (empty):
```python
```

Create `backend/app/api/v1/__init__.py`:
```python
from flask import Blueprint
from flask_restx import Api

api_v1_bp = Blueprint("api_v1", __name__)
api = Api(
    api_v1_bp,
    version="1.0",
    title="Airline Market Demand API",
    description="REST API for airline booking trend analysis",
    doc="/docs",
)
```

Create `backend/app/auth/__init__.py`:
```python
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from . import routes  # noqa: E402, F401
```

Create `backend/app/auth/routes.py` (minimal stub):
```python
from flask import jsonify
from . import auth_bp


@auth_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
```

Create `backend/app/dashboard/__init__.py`:
```python
from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__)

from . import routes  # noqa: E402, F401
```

Create `backend/app/dashboard/routes.py`:
```python
from flask import jsonify
from . import dashboard_bp


@dashboard_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
```

Create `backend/app/models/__init__.py` (empty for now):
```python
```

Create `backend/app/services/__init__.py` (empty):
```python
```

Create `backend/app/utils/__init__.py` (empty):
```python
```

Create `backend/app/tasks/__init__.py` (empty):
```python
```

- [ ] **Step 4: Write wsgi.py**

Create `backend/wsgi.py`:

```python
import os
from app import create_app

config_name = os.environ.get("FLASK_ENV", "default")
app = create_app(config_name)

if __name__ == "__main__":
    app.run()
```

- [ ] **Step 5: Install dependencies and verify app starts**

```bash
cd d:/airline-booking-analysis-main/backend
pip install -r requirements.txt
python -c "from app import create_app; app = create_app('development'); print('App factory OK')"
```

Expected: `App factory OK`

- [ ] **Step 6: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/ backend/wsgi.py
git commit -m "feat: add Flask app factory with extensions and blueprint stubs"
```

---

### Task 3: Database models

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/flight.py`
- Create: `backend/app/models/alert.py`
- Create: `backend/app/models/notification.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write User and Organization models**

Create `backend/app/models/user.py`:

```python
import uuid
from datetime import datetime, timezone

from app.extensions import db, bcrypt, login_manager


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    plan = db.Column(db.String(20), nullable=False, default="free")  # free, pro
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    users = db.relationship("User", backref="organization", lazy="dynamic")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id"), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="member")  # admin, member
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    api_key_hash = db.Column(db.String(255), nullable=True)
    notification_email = db.Column(db.String(255), nullable=True)
    webhook_url = db.Column(db.String(500), nullable=True)
    webhook_secret = db.Column(db.String(255), nullable=True)
    watched_routes = db.Column(db.JSON, default=list)
    personal_api_keys = db.Column(db.JSON, default=dict)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    alert_rules = db.relationship("AlertRule", backref="user", lazy="dynamic")
    alerts_fired = db.relationship("AlertFired", backref="user", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password, rounds=12).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def is_locked(self):
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
```

- [ ] **Step 2: Write Flight, Route, PriceSnapshot, ForecastSnapshot models**

Create `backend/app/models/flight.py`:

```python
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Flight(db.Model):
    __tablename__ = "flights"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = db.Column(db.String(36), nullable=False, index=True)
    origin = db.Column(db.String(50), nullable=False, index=True)
    destination = db.Column(db.String(50), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    airline = db.Column(db.String(100), nullable=False, index=True)
    demand_score = db.Column(db.Float, nullable=False, default=0.0)
    days_until_departure = db.Column(db.Integer, nullable=False, default=0)
    day_of_week = db.Column(db.Integer, nullable=False, default=0)
    season = db.Column(db.String(20), nullable=False, default="summer")
    is_anomaly = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Route(db.Model):
    __tablename__ = "routes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    origin = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    distance_km = db.Column(db.Integer, nullable=False)
    avg_price_7d = db.Column(db.Float, nullable=True)
    avg_price_30d = db.Column(db.Float, nullable=True)
    avg_demand_7d = db.Column(db.Float, nullable=True)
    demand_trend = db.Column(db.String(20), default="stable")  # rising, falling, stable
    last_updated = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("origin", "destination", name="uq_route_origin_dest"),
    )

    price_snapshots = db.relationship("PriceSnapshot", backref="route", lazy="dynamic")
    forecast_snapshots = db.relationship("ForecastSnapshot", backref="route", lazy="dynamic")


class PriceSnapshot(db.Model):
    __tablename__ = "price_snapshots"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id = db.Column(db.String(36), db.ForeignKey("routes.id"), nullable=False, index=True)
    airline = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    demand_score = db.Column(db.Float, nullable=False)
    is_anomaly = db.Column(db.Boolean, default=False)
    snapshot_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ForecastSnapshot(db.Model):
    __tablename__ = "forecast_snapshots"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id = db.Column(db.String(36), db.ForeignKey("routes.id"), nullable=False, index=True)
    airline = db.Column(db.String(100), nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    lower_bound = db.Column(db.Float, nullable=False)
    upper_bound = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 3: Write AlertRule and AlertFired models**

Create `backend/app/models/alert.py`:

```python
import uuid
from datetime import datetime, timezone

from app.extensions import db


class AlertRule(db.Model):
    __tablename__ = "alert_rules"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    route = db.Column(db.String(100), nullable=False)  # "ORIGIN-DEST"
    airline = db.Column(db.String(100), nullable=True)
    condition = db.Column(db.String(30), nullable=False)  # price_below, price_above, demand_spike
    threshold_value = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    alerts_fired = db.relationship("AlertFired", backref="rule", lazy="dynamic")


class AlertFired(db.Model):
    __tablename__ = "alerts_fired"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = db.Column(db.String(36), db.ForeignKey("alert_rules.id"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    triggered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    current_value = db.Column(db.Float, nullable=False)
    threshold_value = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
```

- [ ] **Step 4: Write Notification model**

Create `backend/app/models/notification.py`:

```python
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default="system")  # alert, digest, system
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 5: Update models __init__.py to import all models**

Create `backend/app/models/__init__.py`:

```python
from .user import User, Organization  # noqa: F401
from .flight import Flight, Route, PriceSnapshot, ForecastSnapshot  # noqa: F401
from .alert import AlertRule, AlertFired  # noqa: F401
from .notification import Notification  # noqa: F401
```

- [ ] **Step 6: Initialize migrations and create first migration**

```bash
cd d:/airline-booking-analysis-main/backend
FLASK_ENV=development python -c "
from app import create_app
from app.extensions import db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('All tables created OK')
"
```

Expected: `All tables created OK`

- [ ] **Step 7: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/models/
git commit -m "feat: add all database models (User, Org, Flight, Route, Alert, Notification)"
```

---

### Task 4: Write model tests

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write conftest.py with fixtures**

Create `backend/tests/__init__.py` (empty):
```python
```

Create `backend/tests/conftest.py`:

```python
import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.session.begin_nested()
        yield _db
        _db.session.rollback()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(db):
    from app.models.user import User, Organization

    org = Organization(name="Test Hostel")
    db.session.add(org)
    db.session.flush()

    user = User(
        email="test@example.com",
        name="Test User",
        organization_id=org.id,
    )
    user.set_password("TestPass123!")
    db.session.add(user)
    db.session.flush()
    return user


@pytest.fixture
def auth_headers(client, sample_user):
    """Get JWT auth headers for the sample user."""
    from flask_jwt_extended import create_access_token

    with client.application.app_context():
        token = create_access_token(identity=sample_user.id)
        return {"Authorization": f"Bearer {token}"}
```

- [ ] **Step 2: Write model tests**

Create `backend/tests/test_models.py`:

```python
import pytest
from datetime import date, datetime, timezone
from app.models.user import User, Organization
from app.models.flight import Flight, Route, PriceSnapshot
from app.models.alert import AlertRule, AlertFired
from app.models.notification import Notification


class TestOrganization:
    def test_create_organization(self, db):
        org = Organization(name="Bondi Backpackers")
        db.session.add(org)
        db.session.flush()
        assert org.id is not None
        assert org.name == "Bondi Backpackers"
        assert org.plan == "free"

    def test_organization_users_relationship(self, db):
        org = Organization(name="Test Org")
        db.session.add(org)
        db.session.flush()
        user = User(email="rel@test.com", name="Rel User", organization_id=org.id)
        user.set_password("Pass123!")
        db.session.add(user)
        db.session.flush()
        assert user in org.users.all()


class TestUser:
    def test_create_user(self, db):
        user = User(email="new@test.com", name="New User")
        user.set_password("SecurePass1!")
        db.session.add(user)
        db.session.flush()
        assert user.id is not None
        assert user.email == "new@test.com"
        assert user.role == "member"
        assert user.is_active is True
        assert user.email_verified is False

    def test_password_hashing(self, db):
        user = User(email="pw@test.com", name="PW User")
        user.set_password("MyPassword123!")
        db.session.add(user)
        db.session.flush()
        assert user.check_password("MyPassword123!") is True
        assert user.check_password("WrongPassword") is False
        assert user.password_hash != "MyPassword123!"

    def test_unique_email_constraint(self, db):
        user1 = User(email="dup@test.com", name="User 1")
        user1.set_password("Pass123!")
        db.session.add(user1)
        db.session.flush()
        user2 = User(email="dup@test.com", name="User 2")
        user2.set_password("Pass123!")
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.flush()

    def test_user_locked(self, db):
        user = User(email="lock@test.com", name="Lock User")
        user.set_password("Pass123!")
        assert user.is_locked is False
        user.locked_until = datetime(2099, 1, 1, tzinfo=timezone.utc)
        assert user.is_locked is True


class TestFlight:
    def test_create_flight(self, db):
        flight = Flight(
            run_id="run-001",
            origin="Sydney",
            destination="Melbourne",
            price=245.50,
            date=date(2026, 5, 1),
            airline="Qantas",
            demand_score=0.72,
            days_until_departure=18,
            day_of_week=4,
            season="autumn",
        )
        db.session.add(flight)
        db.session.flush()
        assert flight.id is not None
        assert flight.price == 245.50
        assert flight.is_anomaly is False


class TestRoute:
    def test_create_route(self, db):
        route = Route(origin="Sydney", destination="Melbourne", distance_km=878)
        db.session.add(route)
        db.session.flush()
        assert route.id is not None
        assert route.demand_trend == "stable"

    def test_price_snapshot_relationship(self, db):
        route = Route(origin="Sydney", destination="Brisbane", distance_km=732)
        db.session.add(route)
        db.session.flush()
        snap = PriceSnapshot(
            route_id=route.id, airline="Qantas", price=180.0, demand_score=0.6
        )
        db.session.add(snap)
        db.session.flush()
        assert snap in route.price_snapshots.all()


class TestAlertRule:
    def test_create_alert_rule(self, sample_user, db):
        rule = AlertRule(
            user_id=sample_user.id,
            route="SYD-MEL",
            condition="price_below",
            threshold_value=150.0,
        )
        db.session.add(rule)
        db.session.flush()
        assert rule.is_active is True
        assert rule in sample_user.alert_rules.all()

    def test_alert_fired(self, sample_user, db):
        rule = AlertRule(
            user_id=sample_user.id,
            route="SYD-MEL",
            condition="price_above",
            threshold_value=300.0,
        )
        db.session.add(rule)
        db.session.flush()
        fired = AlertFired(
            rule_id=rule.id,
            user_id=sample_user.id,
            current_value=350.0,
            threshold_value=300.0,
            message="Price for SYD-MEL is $350, above threshold $300",
        )
        db.session.add(fired)
        db.session.flush()
        assert fired.is_read is False
        assert fired in rule.alerts_fired.all()


class TestNotification:
    def test_create_notification(self, sample_user, db):
        notif = Notification(
            user_id=sample_user.id,
            title="Price Alert",
            body="SYD-MEL dropped below $150",
            type="alert",
        )
        db.session.add(notif)
        db.session.flush()
        assert notif.is_read is False
        assert notif in sample_user.notifications.all()
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
cd d:/airline-booking-analysis-main/backend
python -m pytest tests/test_models.py -v
```

Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/tests/
git commit -m "test: add model tests for all database models"
```

---

### Task 5: Demand score engine

**Files:**
- Create: `backend/app/services/demand_engine.py`
- Create: `backend/tests/test_services.py`

- [ ] **Step 1: Write demand engine tests first**

Create `backend/tests/test_services.py`:

```python
import pytest
from datetime import date


class TestDemandScoreEngine:
    def test_demand_score_in_valid_range(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        score = engine.calculate(
            origin="Sydney",
            destination="Melbourne",
            flight_date=date(2026, 1, 15),  # summer, school holiday
            days_until_departure=5,
            day_of_week=4,  # Friday
        )
        assert 0.0 <= score <= 1.0

    def test_high_demand_summer_holiday_soon(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        score = engine.calculate(
            origin="Sydney",
            destination="Melbourne",
            flight_date=date(2026, 1, 10),  # summer
            days_until_departure=3,
            day_of_week=4,  # Friday
        )
        # Summer + soon departure + Friday + popular route = high demand
        assert score > 0.5

    def test_low_demand_offpeak_far_out(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        score = engine.calculate(
            origin="Adelaide",
            destination="Darwin",
            flight_date=date(2026, 5, 13),  # autumn, Wednesday
            days_until_departure=80,
            day_of_week=2,  # Wednesday
        )
        # Off-peak + far out + midweek + less popular route = lower demand
        assert score < 0.5

    def test_popular_route_scores_higher(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        kwargs = dict(
            flight_date=date(2026, 6, 15),
            days_until_departure=14,
            day_of_week=0,  # Monday
        )
        score_popular = engine.calculate(origin="Sydney", destination="Melbourne", **kwargs)
        score_niche = engine.calculate(origin="Adelaide", destination="Darwin", **kwargs)
        assert score_popular > score_niche

    def test_holiday_proximity_boosts_score(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        base_kwargs = dict(
            origin="Sydney",
            destination="Brisbane",
            days_until_departure=14,
            day_of_week=0,
        )
        # Australia Day is Jan 26
        score_near_holiday = engine.calculate(flight_date=date(2026, 1, 20), **base_kwargs)
        score_far_holiday = engine.calculate(flight_date=date(2026, 3, 10), **base_kwargs)
        assert score_near_holiday > score_far_holiday
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd d:/airline-booking-analysis-main/backend
python -m pytest tests/test_services.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: Implement DemandScoreEngine**

Create `backend/app/services/demand_engine.py`:

```python
from datetime import date, timedelta


AU_SCHOOL_HOLIDAYS = [
    # 2024
    (date(2024, 1, 1), date(2024, 1, 28)),
    (date(2024, 4, 6), date(2024, 4, 22)),
    (date(2024, 6, 29), date(2024, 7, 14)),
    (date(2024, 9, 21), date(2024, 10, 7)),
    (date(2024, 12, 18), date(2024, 12, 31)),
    # 2025
    (date(2025, 1, 1), date(2025, 1, 27)),
    (date(2025, 4, 5), date(2025, 4, 21)),
    (date(2025, 6, 28), date(2025, 7, 13)),
    (date(2025, 9, 20), date(2025, 10, 6)),
    (date(2025, 12, 17), date(2025, 12, 31)),
    # 2026
    (date(2026, 1, 1), date(2026, 1, 26)),
    (date(2026, 4, 4), date(2026, 4, 20)),
    (date(2026, 6, 27), date(2026, 7, 12)),
    (date(2026, 9, 19), date(2026, 10, 5)),
    (date(2026, 12, 16), date(2026, 12, 31)),
]

AU_PUBLIC_HOLIDAYS = [
    # 2024
    date(2024, 1, 1), date(2024, 1, 26), date(2024, 3, 29), date(2024, 4, 1),
    date(2024, 4, 25), date(2024, 6, 10), date(2024, 12, 25), date(2024, 12, 26),
    # 2025
    date(2025, 1, 1), date(2025, 1, 27), date(2025, 4, 18), date(2025, 4, 21),
    date(2025, 4, 25), date(2025, 6, 9), date(2025, 12, 25), date(2025, 12, 26),
    # 2026
    date(2026, 1, 1), date(2026, 1, 26), date(2026, 4, 3), date(2026, 4, 6),
    date(2026, 4, 25), date(2026, 6, 8), date(2026, 12, 25), date(2026, 12, 26),
]

# Popularity rank: higher = more popular. SYD-MEL is the busiest domestic route.
ROUTE_POPULARITY = {
    ("Sydney", "Melbourne"): 1.0,
    ("Melbourne", "Sydney"): 1.0,
    ("Sydney", "Brisbane"): 0.85,
    ("Brisbane", "Sydney"): 0.85,
    ("Melbourne", "Brisbane"): 0.75,
    ("Brisbane", "Melbourne"): 0.75,
    ("Sydney", "Perth"): 0.70,
    ("Perth", "Sydney"): 0.70,
    ("Sydney", "Adelaide"): 0.60,
    ("Adelaide", "Sydney"): 0.60,
    ("Melbourne", "Perth"): 0.65,
    ("Perth", "Melbourne"): 0.65,
    ("Melbourne", "Adelaide"): 0.55,
    ("Adelaide", "Melbourne"): 0.55,
    ("Brisbane", "Perth"): 0.40,
    ("Perth", "Brisbane"): 0.40,
    ("Brisbane", "Adelaide"): 0.35,
    ("Adelaide", "Brisbane"): 0.35,
    ("Brisbane", "Darwin"): 0.45,
    ("Darwin", "Brisbane"): 0.45,
    ("Sydney", "Darwin"): 0.50,
    ("Darwin", "Sydney"): 0.50,
    ("Melbourne", "Darwin"): 0.40,
    ("Darwin", "Melbourne"): 0.40,
    ("Perth", "Adelaide"): 0.30,
    ("Adelaide", "Perth"): 0.30,
    ("Perth", "Darwin"): 0.35,
    ("Darwin", "Perth"): 0.35,
    ("Adelaide", "Darwin"): 0.25,
    ("Darwin", "Adelaide"): 0.25,
}


class DemandScoreEngine:
    def calculate(
        self,
        origin: str,
        destination: str,
        flight_date: date,
        days_until_departure: int,
        day_of_week: int,
    ) -> float:
        route_pop = self._route_popularity(origin, destination)
        season = self._seasonality_factor(flight_date)
        days_factor = self._days_until_factor(days_until_departure)
        dow_factor = self._day_of_week_factor(day_of_week)
        holiday = self._holiday_proximity_factor(flight_date)

        score = (
            0.30 * route_pop
            + 0.25 * season
            + 0.20 * days_factor
            + 0.15 * dow_factor
            + 0.10 * holiday
        )
        return max(0.0, min(1.0, score))

    def _route_popularity(self, origin: str, destination: str) -> float:
        return ROUTE_POPULARITY.get((origin, destination), 0.3)

    def _seasonality_factor(self, flight_date: date) -> float:
        for start, end in AU_SCHOOL_HOLIDAYS:
            if start <= flight_date <= end:
                return 1.0
        month = flight_date.month
        if month in (12, 1, 2):  # summer
            return 0.9
        if month in (6, 7, 8):  # winter
            return 0.6
        return 0.4  # off-peak

    def _days_until_factor(self, days: int) -> float:
        if days <= 7:
            return 0.9
        if days <= 21:
            return 0.6
        if days <= 60:
            return 0.4
        return 0.2

    def _day_of_week_factor(self, dow: int) -> float:
        if dow in (0, 4):  # Monday, Friday
            return 0.8
        if dow in (5, 6):  # Saturday, Sunday
            return 0.9
        return 0.5  # Tue-Thu

    def _holiday_proximity_factor(self, flight_date: date) -> float:
        for holiday in AU_PUBLIC_HOLIDAYS:
            if abs((flight_date - holiday).days) <= 14:
                return 0.8
        return 0.1
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd d:/airline-booking-analysis-main/backend
python -m pytest tests/test_services.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/services/demand_engine.py backend/tests/test_services.py
git commit -m "feat: add DemandScoreEngine with formula-based demand scoring"
```

---

### Task 6: Realistic data generator (DataScraper)

**Files:**
- Create: `backend/app/services/data_scraper.py`
- Modify: `backend/tests/test_services.py` (add DataScraper tests)

- [ ] **Step 1: Add DataScraper tests to test_services.py**

Append to `backend/tests/test_services.py`:

```python
class TestDataScraper:
    def test_generates_200_flights(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        assert len(flights) == 200

    def test_flight_fields_present(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        flight = flights[0]
        assert hasattr(flight, "origin")
        assert hasattr(flight, "destination")
        assert hasattr(flight, "price")
        assert hasattr(flight, "airline")
        assert hasattr(flight, "demand_score")
        assert hasattr(flight, "days_until_departure")

    def test_airline_multipliers_affect_price(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        import pandas as pd

        df = pd.DataFrame([vars(f) for f in flights])
        avg_prices = df.groupby("airline")["price"].mean()
        # Qantas should be more expensive than Tiger on average
        if "Qantas" in avg_prices.index and "Tiger Airways" in avg_prices.index:
            assert avg_prices["Qantas"] > avg_prices["Tiger Airways"]

    def test_demand_scores_in_range(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        for f in flights:
            assert 0.0 <= f.demand_score <= 1.0

    def test_all_cities_represented(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        origins = {f.origin for f in flights}
        destinations = {f.destination for f in flights}
        all_cities = origins | destinations
        expected = {"Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Darwin"}
        assert expected.issubset(all_cities)

    def test_origin_never_equals_destination(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        for f in flights:
            assert f.origin != f.destination

    def test_run_id_is_consistent(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        run_ids = {f.run_id for f in flights}
        assert len(run_ids) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd d:/airline-booking-analysis-main/backend
python -m pytest tests/test_services.py::TestDataScraper -v
```

Expected: FAIL

- [ ] **Step 3: Implement DataScraper**

Create `backend/app/services/data_scraper.py`:

```python
import uuid
import random
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List

from .demand_engine import DemandScoreEngine

CITIES = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Darwin"]

ROUTE_BASE_PRICES = {
    ("Sydney", "Melbourne"): 120,
    ("Sydney", "Brisbane"): 180,
    ("Sydney", "Perth"): 350,
    ("Sydney", "Adelaide"): 200,
    ("Sydney", "Darwin"): 420,
    ("Melbourne", "Brisbane"): 220,
    ("Melbourne", "Perth"): 380,
    ("Melbourne", "Adelaide"): 150,
    ("Melbourne", "Darwin"): 450,
    ("Brisbane", "Perth"): 480,
    ("Brisbane", "Adelaide"): 280,
    ("Brisbane", "Darwin"): 320,
    ("Perth", "Adelaide"): 300,
    ("Perth", "Darwin"): 260,
    ("Adelaide", "Darwin"): 380,
}

AIRLINE_PRICE_MULTIPLIERS = {
    "Qantas": 1.25,
    "Virgin Australia": 1.10,
    "Jetstar": 0.85,
    "Tiger Airways": 0.75,
}

AIRLINES = list(AIRLINE_PRICE_MULTIPLIERS.keys())

ROUTE_DISTANCES_KM = {
    ("Sydney", "Melbourne"): 878,
    ("Sydney", "Brisbane"): 732,
    ("Sydney", "Perth"): 3290,
    ("Sydney", "Adelaide"): 1165,
    ("Sydney", "Darwin"): 3150,
    ("Melbourne", "Brisbane"): 1378,
    ("Melbourne", "Perth"): 2721,
    ("Melbourne", "Adelaide"): 654,
    ("Melbourne", "Darwin"): 3144,
    ("Brisbane", "Perth"): 3604,
    ("Brisbane", "Adelaide"): 1600,
    ("Brisbane", "Darwin"): 2852,
    ("Perth", "Adelaide"): 2130,
    ("Perth", "Darwin"): 2644,
    ("Adelaide", "Darwin"): 2622,
}


def _get_base_price(origin: str, destination: str) -> int:
    key = (origin, destination)
    if key in ROUTE_BASE_PRICES:
        return ROUTE_BASE_PRICES[key]
    reverse_key = (destination, origin)
    if reverse_key in ROUTE_BASE_PRICES:
        return ROUTE_BASE_PRICES[reverse_key]
    return 250  # fallback


def _get_distance(origin: str, destination: str) -> int:
    key = (origin, destination)
    if key in ROUTE_DISTANCES_KM:
        return ROUTE_DISTANCES_KM[key]
    reverse_key = (destination, origin)
    if reverse_key in ROUTE_DISTANCES_KM:
        return ROUTE_DISTANCES_KM[reverse_key]
    return 1500


def _get_season(d: date) -> str:
    month = d.month
    if month in (12, 1, 2):
        return "summer"
    if month in (3, 4, 5):
        return "autumn"
    if month in (6, 7, 8):
        return "winter"
    return "spring"


@dataclass
class GeneratedFlight:
    run_id: str
    origin: str
    destination: str
    price: float
    date: date
    airline: str
    demand_score: float
    days_until_departure: int
    day_of_week: int
    season: str
    distance_km: int = 0


class DataScraper:
    def __init__(self):
        self.demand_engine = DemandScoreEngine()

    def generate_flights(self, count: int = 200) -> List[GeneratedFlight]:
        run_id = str(uuid.uuid4())
        today = date.today()
        flights = []

        for _ in range(count):
            origin = random.choice(CITIES)
            destination = random.choice([c for c in CITIES if c != origin])
            airline = random.choice(AIRLINES)
            days_until = random.randint(1, 90)
            flight_date = today + timedelta(days=days_until)
            dow = flight_date.weekday()

            demand_score = self.demand_engine.calculate(
                origin=origin,
                destination=destination,
                flight_date=flight_date,
                days_until_departure=days_until,
                day_of_week=dow,
            )

            base_price = _get_base_price(origin, destination)
            multiplier = AIRLINE_PRICE_MULTIPLIERS[airline]
            price = base_price * multiplier * (1 + demand_score * 0.6) * random.gauss(1.0, 0.05)
            price = round(max(price, 50.0), 2)

            flights.append(
                GeneratedFlight(
                    run_id=run_id,
                    origin=origin,
                    destination=destination,
                    price=price,
                    date=flight_date,
                    airline=airline,
                    demand_score=round(demand_score, 4),
                    days_until_departure=days_until,
                    day_of_week=dow,
                    season=_get_season(flight_date),
                    distance_km=_get_distance(origin, destination),
                )
            )

        return flights
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd d:/airline-booking-analysis-main/backend
python -m pytest tests/test_services.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/services/data_scraper.py backend/tests/test_services.py
git commit -m "feat: add DataScraper with realistic synthetic flight data generation"
```

---

### Task 7: Data processor with anomaly detection

**Files:**
- Create: `backend/app/services/data_processor.py`

- [ ] **Step 1: Implement DataProcessor**

Create `backend/app/services/data_processor.py`:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.extensions import db
from app.models.flight import Flight, Route, PriceSnapshot
from app.services.data_scraper import DataScraper, GeneratedFlight, _get_distance, ROUTE_DISTANCES_KM


class DataProcessor:
    def __init__(self):
        self.scraper = DataScraper()

    def persist_flights(self, flights: List[GeneratedFlight]) -> str:
        """Save generated flights to DB. Returns run_id."""
        if not flights:
            return ""
        run_id = flights[0].run_id
        for f in flights:
            flight = Flight(
                run_id=run_id,
                origin=f.origin,
                destination=f.destination,
                price=f.price,
                date=f.date,
                airline=f.airline,
                demand_score=f.demand_score,
                days_until_departure=f.days_until_departure,
                day_of_week=f.day_of_week,
                season=f.season,
                is_anomaly=False,
            )
            db.session.add(flight)

            # Ensure route exists
            self._ensure_route(f.origin, f.destination)

            # Add price snapshot
            route = Route.query.filter_by(origin=f.origin, destination=f.destination).first()
            if route:
                snap = PriceSnapshot(
                    route_id=route.id,
                    airline=f.airline,
                    price=f.price,
                    demand_score=f.demand_score,
                )
                db.session.add(snap)

        db.session.commit()
        return run_id

    def _ensure_route(self, origin: str, destination: str):
        existing = Route.query.filter_by(origin=origin, destination=destination).first()
        if not existing:
            route = Route(
                origin=origin,
                destination=destination,
                distance_km=_get_distance(origin, destination),
            )
            db.session.add(route)
            db.session.flush()

    def update_route_aggregates(self):
        """Recompute avg_price_7d, avg_price_30d, demand_trend for all routes."""
        routes = Route.query.all()
        now = datetime.now(timezone.utc)
        for route in routes:
            snapshots = (
                PriceSnapshot.query.filter_by(route_id=route.id)
                .order_by(PriceSnapshot.snapshot_at.desc())
                .all()
            )
            if not snapshots:
                continue

            df = pd.DataFrame(
                [{"price": s.price, "demand_score": s.demand_score, "at": s.snapshot_at} for s in snapshots]
            )
            df["at"] = pd.to_datetime(df["at"], utc=True)

            seven_days_ago = now - pd.Timedelta(days=7)
            thirty_days_ago = now - pd.Timedelta(days=30)

            recent_7 = df[df["at"] >= seven_days_ago]
            recent_30 = df[df["at"] >= thirty_days_ago]

            route.avg_price_7d = round(recent_7["price"].mean(), 2) if len(recent_7) > 0 else None
            route.avg_price_30d = round(recent_30["price"].mean(), 2) if len(recent_30) > 0 else None
            route.avg_demand_7d = round(recent_7["demand_score"].mean(), 4) if len(recent_7) > 0 else None

            # Demand trend: compare this week avg to previous week avg
            fourteen_days_ago = now - pd.Timedelta(days=14)
            prev_week = df[(df["at"] >= fourteen_days_ago) & (df["at"] < seven_days_ago)]
            if len(recent_7) > 0 and len(prev_week) > 0:
                curr_avg = recent_7["demand_score"].mean()
                prev_avg = prev_week["demand_score"].mean()
                if curr_avg > prev_avg * 1.1:
                    route.demand_trend = "rising"
                elif curr_avg < prev_avg * 0.9:
                    route.demand_trend = "falling"
                else:
                    route.demand_trend = "stable"

            route.last_updated = now

        db.session.commit()

    def detect_anomalies(self):
        """Flag flights as anomalies if price deviates >2 std from 7-day rolling mean per route/airline."""
        routes = Route.query.all()
        for route in routes:
            snapshots = (
                PriceSnapshot.query.filter_by(route_id=route.id)
                .order_by(PriceSnapshot.snapshot_at.asc())
                .all()
            )
            if len(snapshots) < 7:
                continue

            for airline in set(s.airline for s in snapshots):
                airline_snaps = [s for s in snapshots if s.airline == airline]
                if len(airline_snaps) < 7:
                    continue

                prices = [s.price for s in airline_snaps]
                series = pd.Series(prices)
                rolling_mean = series.rolling(window=7, min_periods=7).mean()
                rolling_std = series.rolling(window=7, min_periods=7).std()

                for i in range(len(airline_snaps)):
                    if pd.isna(rolling_mean.iloc[i]) or pd.isna(rolling_std.iloc[i]):
                        continue
                    if rolling_std.iloc[i] == 0:
                        continue
                    if abs(prices[i] - rolling_mean.iloc[i]) > 2 * rolling_std.iloc[i]:
                        airline_snaps[i].is_anomaly = True

        db.session.commit()

    def get_market_insights(self) -> Dict[str, Any]:
        """Compute market insights from persisted data."""
        flights = Flight.query.order_by(Flight.created_at.desc()).limit(1000).all()
        if not flights:
            return {
                "popular_routes": [],
                "price_trends": [],
                "demand_periods": [],
                "airline_stats": [],
                "total_flights": 0,
                "avg_price": 0,
                "peak_demand_score": 0,
            }

        df = pd.DataFrame(
            [
                {
                    "origin": f.origin,
                    "destination": f.destination,
                    "price": f.price,
                    "date": f.date.isoformat() if f.date else "",
                    "airline": f.airline,
                    "demand_score": f.demand_score,
                }
                for f in flights
            ]
        )

        popular_routes = (
            df.groupby(["origin", "destination"])
            .agg({"price": "mean", "demand_score": "mean"})
            .reset_index()
        )
        popular_routes["route"] = popular_routes["origin"] + " - " + popular_routes["destination"]
        popular_routes = popular_routes.sort_values("demand_score", ascending=False).head(10)

        price_trends = df.groupby("date")["price"].mean().reset_index()

        demand_periods = df.groupby("date")["demand_score"].mean().reset_index()
        demand_periods = demand_periods.sort_values("demand_score", ascending=False).head(5)

        airline_stats = (
            df.groupby("airline").agg({"price": "mean", "demand_score": "mean"}).reset_index()
        )

        return {
            "popular_routes": popular_routes.to_dict("records"),
            "price_trends": price_trends.to_dict("records"),
            "demand_periods": demand_periods.to_dict("records"),
            "airline_stats": airline_stats.to_dict("records"),
            "total_flights": len(flights),
            "avg_price": round(df["price"].mean(), 2),
            "peak_demand_score": round(df["demand_score"].max(), 4),
        }
```

- [ ] **Step 2: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/services/data_processor.py
git commit -m "feat: add DataProcessor with persistence, route aggregates, and anomaly detection"
```

---

### Task 8: Marshmallow validators and utility helpers

**Files:**
- Create: `backend/app/utils/validators.py`
- Create: `backend/app/utils/security.py`
- Create: `backend/app/utils/helpers.py`

- [ ] **Step 1: Write marshmallow schemas**

Create `backend/app/utils/validators.py`:

```python
from marshmallow import Schema, fields, validate, validates, ValidationError


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    org_name = fields.Str(validate=validate.Length(max=200))

    @validates("password")
    def validate_password_strength(self, value):
        if not any(c.isupper() for c in value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise ValidationError("Password must contain at least one digit.")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class AlertRuleSchema(Schema):
    route = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    airline = fields.Str(validate=validate.Length(max=100), allow_none=True, load_default=None)
    condition = fields.Str(
        required=True,
        validate=validate.OneOf(["price_below", "price_above", "demand_spike"]),
    )
    threshold_value = fields.Float(required=True, validate=validate.Range(min=0))
    is_active = fields.Bool(load_default=True)


class AlertRuleUpdateSchema(Schema):
    route = fields.Str(validate=validate.Length(min=3, max=100))
    airline = fields.Str(validate=validate.Length(max=100), allow_none=True)
    condition = fields.Str(
        validate=validate.OneOf(["price_below", "price_above", "demand_spike"]),
    )
    threshold_value = fields.Float(validate=validate.Range(min=0))
    is_active = fields.Bool()


class RouteQuerySchema(Schema):
    origin = fields.Str(validate=validate.Length(max=50))
    destination = fields.Str(validate=validate.Length(max=50))
    airline = fields.Str(validate=validate.Length(max=100))
    date_from = fields.Date()
    date_to = fields.Date()
    sort_by = fields.Str(
        validate=validate.OneOf(["price", "demand_score", "origin", "destination"]),
        load_default="demand_score",
    )
    order = fields.Str(validate=validate.OneOf(["asc", "desc"]), load_default="desc")
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)


class ProfileUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    notification_email = fields.Email(allow_none=True)
    webhook_url = fields.Url(allow_none=True)
    watched_routes = fields.List(fields.Str(validate=validate.Length(max=100)))


class ExportPDFSchema(Schema):
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    routes = fields.List(fields.Str(), load_default=[])
    include_forecast = fields.Bool(load_default=False)
    include_ai_summary = fields.Bool(load_default=False)
```

- [ ] **Step 2: Write security utilities**

Create `backend/app/utils/security.py`:

```python
import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bleach
from cryptography.fernet import Fernet

from app.extensions import bcrypt


def sanitize_text(text: str) -> str:
    """Strip all HTML tags from input text."""
    return bleach.clean(text, tags=[], strip=True)


def generate_api_key() -> tuple[str, str]:
    """Generate a new API key. Returns (raw_key, hashed_key)."""
    raw_key = f"ak_{uuid.uuid4().hex}"
    hashed_key = bcrypt.generate_password_hash(raw_key, rounds=12).decode("utf-8")
    return raw_key, hashed_key


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    return bcrypt.check_password_hash(hashed_key, raw_key)


def generate_token() -> str:
    """Generate a cryptographically random token for email verification / password reset."""
    return secrets.token_urlsafe(32)


def generate_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def encrypt_value(plaintext: str, encryption_key: str) -> str:
    """AES-256 encrypt a value using Fernet (which uses AES-CBC under the hood)."""
    f = Fernet(encryption_key.encode())
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str, encryption_key: str) -> str:
    f = Fernet(encryption_key.encode())
    return f.decrypt(ciphertext.encode()).decode()


def sign_webhook_payload(payload: bytes, secret: str) -> str:
    """HMAC-SHA256 sign a webhook payload."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_webhook_signature(payload: bytes, secret: str, signature: str) -> bool:
    expected = sign_webhook_payload(payload, secret)
    return hmac.compare_digest(expected, signature)
```

- [ ] **Step 3: Write helper utilities**

Create `backend/app/utils/helpers.py`:

```python
from datetime import date


def get_season(d: date) -> str:
    month = d.month
    if month in (12, 1, 2):
        return "summer"
    if month in (3, 4, 5):
        return "autumn"
    if month in (6, 7, 8):
        return "winter"
    return "spring"


def paginate_query(query, page: int, per_page: int):
    """Apply pagination to a SQLAlchemy query. Returns (items, total, pages)."""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination.total, pagination.pages
```

- [ ] **Step 4: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/utils/
git commit -m "feat: add marshmallow validators, security utils, and helpers"
```

---

### Task 9: REST API endpoints (routes, prices, insights, alerts, export, notifications)

**Files:**
- Modify: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/routes.py`
- Create: `backend/app/api/v1/prices.py`
- Create: `backend/app/api/v1/insights.py`
- Create: `backend/app/api/v1/alerts.py`
- Create: `backend/app/api/v1/export.py`
- Create: `backend/app/api/v1/webhooks.py`

- [ ] **Step 1: Update API v1 __init__ to register all namespaces**

Replace `backend/app/api/v1/__init__.py`:

```python
from flask import Blueprint
from flask_restx import Api

api_v1_bp = Blueprint("api_v1", __name__)
api = Api(
    api_v1_bp,
    version="1.0",
    title="Airline Market Demand API",
    description="REST API for airline booking trend analysis",
    doc="/docs",
)

from .routes import ns as routes_ns  # noqa: E402
from .prices import ns as prices_ns  # noqa: E402
from .insights import ns as insights_ns  # noqa: E402
from .alerts import ns as alerts_ns  # noqa: E402
from .export import ns as export_ns  # noqa: E402
from .webhooks import ns as webhooks_ns  # noqa: E402

api.add_namespace(routes_ns, path="/routes")
api.add_namespace(prices_ns, path="/prices")
api.add_namespace(insights_ns, path="/insights")
api.add_namespace(alerts_ns, path="/alerts")
api.add_namespace(export_ns, path="/export")
api.add_namespace(webhooks_ns, path="/webhooks")
```

- [ ] **Step 2: Write routes endpoint**

Create `backend/app/api/v1/routes.py`:

```python
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from marshmallow import ValidationError

from app.extensions import cache, db
from app.models.flight import Route, PriceSnapshot, Flight, ForecastSnapshot
from app.utils.validators import RouteQuerySchema
from app.utils.helpers import paginate_query

ns = Namespace("routes", description="Route operations")


@ns.route("/")
class RouteList(Resource):
    @cache.cached(timeout=300, query_string=True)
    def get(self):
        """List all routes with filtering and pagination."""
        schema = RouteQuerySchema()
        try:
            params = schema.load(request.args)
        except ValidationError as e:
            return {"error": "Validation error", "messages": e.messages}, 400

        query = Route.query
        if params.get("origin"):
            query = query.filter(Route.origin.ilike(params["origin"]))
        if params.get("destination"):
            query = query.filter(Route.destination.ilike(params["destination"]))

        sort_col = getattr(Route, params["sort_by"], Route.avg_demand_7d)
        if sort_col is not None:
            query = query.order_by(sort_col.desc() if params["order"] == "desc" else sort_col.asc())

        items, total, pages = paginate_query(query, params["page"], params["per_page"])

        return {
            "routes": [
                {
                    "id": r.id,
                    "origin": r.origin,
                    "destination": r.destination,
                    "distance_km": r.distance_km,
                    "avg_price_7d": r.avg_price_7d,
                    "avg_price_30d": r.avg_price_30d,
                    "avg_demand_7d": r.avg_demand_7d,
                    "demand_trend": r.demand_trend,
                    "last_updated": r.last_updated.isoformat() if r.last_updated else None,
                }
                for r in items
            ],
            "total": total,
            "pages": pages,
            "page": params["page"],
            "per_page": params["per_page"],
        }


@ns.route("/<string:origin>/<string:destination>")
class RouteDetail(Resource):
    @cache.cached(timeout=300)
    def get(self, origin, destination):
        """Full route detail with price history, forecast, anomalies, airline breakdown."""
        route = Route.query.filter_by(origin=origin, destination=destination).first()
        if not route:
            # Try reverse
            route = Route.query.filter_by(origin=destination, destination=origin).first()
        if not route:
            return {"error": "Route not found"}, 404

        snapshots = (
            PriceSnapshot.query.filter_by(route_id=route.id)
            .order_by(PriceSnapshot.snapshot_at.desc())
            .limit(500)
            .all()
        )

        anomalies = [s for s in snapshots if s.is_anomaly]

        # Airline breakdown
        airline_data = {}
        for s in snapshots:
            if s.airline not in airline_data:
                airline_data[s.airline] = {"prices": [], "demand_scores": []}
            airline_data[s.airline]["prices"].append(s.price)
            airline_data[s.airline]["demand_scores"].append(s.demand_score)

        airline_breakdown = []
        for airline, data in airline_data.items():
            airline_breakdown.append({
                "airline": airline,
                "avg_price": round(sum(data["prices"]) / len(data["prices"]), 2),
                "avg_demand": round(sum(data["demand_scores"]) / len(data["demand_scores"]), 4),
                "count": len(data["prices"]),
            })

        # Forecasts
        forecasts = (
            ForecastSnapshot.query.filter_by(route_id=route.id)
            .order_by(ForecastSnapshot.forecast_date.asc())
            .limit(56)  # 14 days * 4 airlines
            .all()
        )

        return {
            "route": {
                "id": route.id,
                "origin": route.origin,
                "destination": route.destination,
                "distance_km": route.distance_km,
                "avg_price_7d": route.avg_price_7d,
                "avg_price_30d": route.avg_price_30d,
                "avg_demand_7d": route.avg_demand_7d,
                "demand_trend": route.demand_trend,
            },
            "price_history": [
                {
                    "airline": s.airline,
                    "price": s.price,
                    "demand_score": s.demand_score,
                    "is_anomaly": s.is_anomaly,
                    "snapshot_at": s.snapshot_at.isoformat(),
                }
                for s in snapshots
            ],
            "anomalies": [
                {
                    "airline": s.airline,
                    "price": s.price,
                    "snapshot_at": s.snapshot_at.isoformat(),
                }
                for s in anomalies
            ],
            "airline_breakdown": airline_breakdown,
            "forecasts": [
                {
                    "airline": f.airline,
                    "date": f.forecast_date.isoformat(),
                    "predicted_price": f.predicted_price,
                    "lower_bound": f.lower_bound,
                    "upper_bound": f.upper_bound,
                }
                for f in forecasts
            ],
        }
```

- [ ] **Step 3: Write prices endpoint**

Create `backend/app/api/v1/prices.py`:

```python
from flask import request
from flask_restx import Namespace, Resource

from app.extensions import cache, db
from app.models.flight import PriceSnapshot, Route, Flight

ns = Namespace("prices", description="Price operations")


@ns.route("/")
class PriceHistory(Resource):
    @cache.cached(timeout=300, query_string=True)
    def get(self):
        """PriceSnapshot history for charting."""
        route_id = request.args.get("route_id")
        airline = request.args.get("airline")
        limit = min(int(request.args.get("limit", 200)), 1000)

        query = PriceSnapshot.query.order_by(PriceSnapshot.snapshot_at.desc())
        if route_id:
            query = query.filter_by(route_id=route_id)
        if airline:
            query = query.filter_by(airline=airline)

        snapshots = query.limit(limit).all()

        return {
            "prices": [
                {
                    "id": s.id,
                    "route_id": s.route_id,
                    "airline": s.airline,
                    "price": s.price,
                    "demand_score": s.demand_score,
                    "is_anomaly": s.is_anomaly,
                    "snapshot_at": s.snapshot_at.isoformat(),
                }
                for s in snapshots
            ]
        }


@ns.route("/trends")
class PriceTrends(Resource):
    @cache.cached(timeout=300, query_string=True)
    def get(self):
        """Daily avg price per route, last 30 days."""
        import pandas as pd
        from datetime import datetime, timedelta, timezone

        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        flights = (
            Flight.query.filter(Flight.created_at >= thirty_days_ago)
            .all()
        )

        if not flights:
            return {"trends": []}

        df = pd.DataFrame(
            [
                {
                    "origin": f.origin,
                    "destination": f.destination,
                    "price": f.price,
                    "date": f.date.isoformat() if f.date else "",
                    "airline": f.airline,
                }
                for f in flights
            ]
        )

        trends = (
            df.groupby(["origin", "destination", "date"])["price"]
            .mean()
            .reset_index()
        )
        trends["route"] = trends["origin"] + " - " + trends["destination"]
        trends["price"] = trends["price"].round(2)

        return {
            "trends": trends[["route", "date", "price"]].to_dict("records")
        }
```

- [ ] **Step 4: Write insights endpoint (placeholder for AI, real data)**

Create `backend/app/api/v1/insights.py`:

```python
from flask import request, Response, current_app
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import cache
from app.services.data_processor import DataProcessor

ns = Namespace("insights", description="Market insights")


@ns.route("/summary")
class InsightsSummary(Resource):
    @cache.cached(timeout=300)
    def get(self):
        """Full market summary from processed data."""
        processor = DataProcessor()
        insights = processor.get_market_insights()
        return {"insights": insights}


@ns.route("/briefing")
class Briefing(Resource):
    @cache.cached(timeout=3600)
    def get(self):
        """Today's morning briefing. Returns structured data; AI generation added later."""
        processor = DataProcessor()
        insights = processor.get_market_insights()

        briefing_points = []
        if insights["popular_routes"]:
            top = insights["popular_routes"][0]
            briefing_points.append(
                f"Highest demand route: {top['route']} with avg demand score {top['demand_score']:.2f}"
            )
        if insights["avg_price"]:
            briefing_points.append(f"Market avg price: ${insights['avg_price']:.2f} AUD")
        if insights["airline_stats"]:
            cheapest = min(insights["airline_stats"], key=lambda x: x["price"])
            briefing_points.append(
                f"Most affordable airline: {cheapest['airline']} at avg ${cheapest['price']:.2f}"
            )

        return {"briefing": briefing_points, "data": insights}


@ns.route("/stream")
class InsightsStream(Resource):
    @jwt_required()
    def get(self):
        """SSE endpoint - streams AI analysis. Full implementation in backend-services plan."""
        processor = DataProcessor()
        insights = processor.get_market_insights()

        def generate():
            # Placeholder: will be replaced with Claude API streaming
            summary = (
                f"Market Analysis: {insights['total_flights']} flights analyzed. "
                f"Average price ${insights['avg_price']:.2f} AUD. "
                f"Peak demand score: {insights['peak_demand_score']:.2f}."
            )
            for word in summary.split():
                yield f"data: {word} \n\n"
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype="text/event-stream")
```

- [ ] **Step 5: Write alerts CRUD endpoint**

Create `backend/app/api/v1/alerts.py`:

```python
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.alert import AlertRule, AlertFired
from app.models.notification import Notification
from app.utils.validators import AlertRuleSchema, AlertRuleUpdateSchema
from app.utils.security import sanitize_text

ns = Namespace("alerts", description="Alert rule operations")


@ns.route("/")
class AlertRuleList(Resource):
    @jwt_required()
    def get(self):
        """List alert rules for current user."""
        user_id = get_jwt_identity()
        rules = AlertRule.query.filter_by(user_id=user_id).order_by(AlertRule.created_at.desc()).all()
        return {
            "alerts": [
                {
                    "id": r.id,
                    "route": r.route,
                    "airline": r.airline,
                    "condition": r.condition,
                    "threshold_value": r.threshold_value,
                    "is_active": r.is_active,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rules
            ]
        }

    @jwt_required()
    def post(self):
        """Create a new alert rule."""
        schema = AlertRuleSchema()
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as e:
            return {"error": "Validation error", "messages": e.messages}, 400

        user_id = get_jwt_identity()
        rule = AlertRule(
            user_id=user_id,
            route=sanitize_text(data["route"]),
            airline=sanitize_text(data["airline"]) if data.get("airline") else None,
            condition=data["condition"],
            threshold_value=data["threshold_value"],
            is_active=data.get("is_active", True),
        )
        db.session.add(rule)
        db.session.commit()

        return {
            "id": rule.id,
            "route": rule.route,
            "airline": rule.airline,
            "condition": rule.condition,
            "threshold_value": rule.threshold_value,
            "is_active": rule.is_active,
        }, 201


@ns.route("/<string:rule_id>")
class AlertRuleDetail(Resource):
    @jwt_required()
    def put(self, rule_id):
        """Update an alert rule."""
        user_id = get_jwt_identity()
        rule = AlertRule.query.filter_by(id=rule_id, user_id=user_id).first()
        if not rule:
            return {"error": "Alert rule not found"}, 404

        schema = AlertRuleUpdateSchema()
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as e:
            return {"error": "Validation error", "messages": e.messages}, 400

        if "route" in data:
            rule.route = sanitize_text(data["route"])
        if "airline" in data:
            rule.airline = sanitize_text(data["airline"]) if data["airline"] else None
        if "condition" in data:
            rule.condition = data["condition"]
        if "threshold_value" in data:
            rule.threshold_value = data["threshold_value"]
        if "is_active" in data:
            rule.is_active = data["is_active"]

        db.session.commit()
        return {"message": "Updated", "id": rule.id}

    @jwt_required()
    def delete(self, rule_id):
        """Delete an alert rule."""
        user_id = get_jwt_identity()
        rule = AlertRule.query.filter_by(id=rule_id, user_id=user_id).first()
        if not rule:
            return {"error": "Alert rule not found"}, 404

        db.session.delete(rule)
        db.session.commit()
        return {"message": "Deleted"}, 200


@ns.route("/fired")
class AlertFiredList(Resource):
    @jwt_required()
    def get(self):
        """AlertFired history for current user."""
        user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        query = AlertFired.query.filter_by(user_id=user_id).order_by(AlertFired.triggered_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "alerts_fired": [
                {
                    "id": a.id,
                    "rule_id": a.rule_id,
                    "triggered_at": a.triggered_at.isoformat(),
                    "current_value": a.current_value,
                    "threshold_value": a.threshold_value,
                    "message": a.message,
                    "is_read": a.is_read,
                }
                for a in pagination.items
            ],
            "total": pagination.total,
            "page": page,
        }


@ns.route("/notifications")
class NotificationList(Resource):
    @jwt_required()
    def get(self):
        """Unread notifications for current user."""
        user_id = get_jwt_identity()
        notifications = (
            Notification.query.filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )
        return {
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "body": n.body,
                    "type": n.type,
                    "created_at": n.created_at.isoformat(),
                }
                for n in notifications
            ]
        }


@ns.route("/notifications/<string:notif_id>/read")
class NotificationRead(Resource):
    @jwt_required()
    def post(self, notif_id):
        """Mark notification as read."""
        user_id = get_jwt_identity()
        notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
        if not notif:
            return {"error": "Notification not found"}, 404
        notif.is_read = True
        db.session.commit()
        return {"message": "Marked as read"}
```

- [ ] **Step 6: Write export endpoint (CSV + Excel)**

Create `backend/app/api/v1/export.py`:

```python
import io
import csv
from flask import request, send_file
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required

from app.models.flight import Flight

ns = Namespace("export", description="Data export operations")


@ns.route("/csv")
class CSVExport(Resource):
    @jwt_required()
    def get(self):
        """Export flight data as CSV."""
        flights = Flight.query.order_by(Flight.created_at.desc()).limit(5000).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "origin", "destination", "price", "date", "airline",
            "demand_score", "days_until_departure", "season", "is_anomaly",
        ])
        for f in flights:
            writer.writerow([
                f.origin, f.destination, f.price, f.date.isoformat() if f.date else "",
                f.airline, f.demand_score, f.days_until_departure, f.season, f.is_anomaly,
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="flight_data.csv",
        )


@ns.route("/excel")
class ExcelExport(Resource):
    @jwt_required()
    def get(self):
        """Export formatted Excel with Overview, Routes, Prices, Insights sheets."""
        import pandas as pd
        from app.models.flight import Route, PriceSnapshot
        from app.services.data_processor import DataProcessor

        flights = Flight.query.order_by(Flight.created_at.desc()).limit(5000).all()
        routes = Route.query.all()

        # Flights sheet
        flights_df = pd.DataFrame([
            {
                "Origin": f.origin, "Destination": f.destination, "Price (AUD)": f.price,
                "Date": f.date.isoformat() if f.date else "", "Airline": f.airline,
                "Demand Score": f.demand_score, "Season": f.season,
            }
            for f in flights
        ])

        # Routes sheet
        routes_df = pd.DataFrame([
            {
                "Origin": r.origin, "Destination": r.destination, "Distance (km)": r.distance_km,
                "Avg Price 7d": r.avg_price_7d, "Avg Price 30d": r.avg_price_30d,
                "Demand Trend": r.demand_trend,
            }
            for r in routes
        ])

        # Overview sheet
        processor = DataProcessor()
        insights = processor.get_market_insights()
        overview_df = pd.DataFrame([
            {"Metric": "Total Flights", "Value": insights["total_flights"]},
            {"Metric": "Average Price (AUD)", "Value": insights["avg_price"]},
            {"Metric": "Peak Demand Score", "Value": insights["peak_demand_score"]},
        ])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            overview_df.to_excel(writer, sheet_name="Overview", index=False)
            routes_df.to_excel(writer, sheet_name="Routes", index=False)
            flights_df.to_excel(writer, sheet_name="Flights", index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="airline_report.xlsx",
        )
```

- [ ] **Step 7: Write webhooks endpoint**

Create `backend/app/api/v1/webhooks.py`:

```python
import json
import requests
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.utils.security import sign_webhook_payload

ns = Namespace("webhooks", description="Webhook operations")


@ns.route("/test")
class WebhookTest(Resource):
    @jwt_required()
    def post(self):
        """Send a test webhook payload to user's configured URL."""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user or not user.webhook_url:
            return {"error": "No webhook URL configured"}, 400

        payload = json.dumps({
            "event": "test",
            "message": "This is a test webhook from Airline Market Demand API",
            "user_id": user.id,
        }).encode()

        signature = sign_webhook_payload(payload, user.webhook_secret or "default-secret")

        try:
            resp = requests.post(
                user.webhook_url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature-256": signature,
                },
                timeout=10,
            )
            return {
                "status": "sent",
                "response_code": resp.status_code,
            }
        except requests.RequestException as e:
            return {"error": f"Webhook delivery failed: {str(e)}"}, 502
```

- [ ] **Step 8: Verify app starts with all endpoints**

```bash
cd d:/airline-booking-analysis-main/backend
python -c "
from app import create_app
app = create_app('development')
with app.app_context():
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        print(f'{rule.methods - {\"OPTIONS\", \"HEAD\"}} {rule.rule}')
"
```

Expected: should list /api/v1/routes/, /api/v1/prices/, etc.

- [ ] **Step 9: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/api/
git commit -m "feat: add all REST API endpoints (routes, prices, insights, alerts, export, webhooks)"
```

---

### Task 10: Authentication system

**Files:**
- Modify: `backend/app/auth/routes.py`

- [ ] **Step 1: Implement full auth routes**

Replace `backend/app/auth/routes.py`:

```python
import secrets
from datetime import datetime, timedelta, timezone

from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from flask_login import login_user, logout_user, current_user
from marshmallow import ValidationError

from . import auth_bp
from app.extensions import db, bcrypt, limiter
from app.models.user import User, Organization
from app.utils.validators import RegisterSchema, LoginSchema, ProfileUpdateSchema
from app.utils.security import (
    sanitize_text,
    generate_token,
    generate_token_hash,
    generate_api_key,
    encrypt_value,
    decrypt_value,
)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5/minute")
def register():
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Validation error", "messages": e.messages}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    org = None
    if data.get("org_name"):
        org = Organization(name=sanitize_text(data["org_name"]))
        db.session.add(org)
        db.session.flush()

    user = User(
        email=data["email"],
        name=sanitize_text(data["name"]),
        organization_id=org.id if org else None,
        email_verified=False,
    )
    user.set_password(data["password"])

    # Generate email verification token (store hash)
    verify_token = generate_token()
    # In production, send email with this token. For now, auto-verify in dev.
    if current_app.debug:
        user.email_verified = True

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful" + (" (auto-verified in dev)" if current_app.debug else ". Check email to verify."),
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "email_verified": user.email_verified,
        },
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Validation error", "messages": e.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if user.is_locked:
        return jsonify({"error": "Account locked. Try again later."}), 423

    if not user.check_password(data["password"]):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        db.session.commit()
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.email_verified:
        return jsonify({"error": "Email not verified"}), 403

    # Reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Session login for web
    login_user(user)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "organization_id": user.organization_id,
        },
    })


@auth_bp.route("/logout", methods=["POST"])
@jwt_required(optional=True)
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token})


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3/minute")
def forgot_password():
    email = (request.get_json() or {}).get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    # Always return success to prevent email enumeration
    return jsonify({"message": "If the email exists, a reset link has been sent."})


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("password")
    if not token or not new_password:
        return jsonify({"error": "Token and password required"}), 400
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    # In production: verify token hash, find user, update password
    return jsonify({"message": "Password reset successful"})


@auth_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    # In production: hash token, find user, set email_verified=True
    return jsonify({"message": "Email verification endpoint. Full implementation with email service."})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "organization_id": user.organization_id,
        "notification_email": user.notification_email,
        "webhook_url": user.webhook_url,
        "watched_routes": user.watched_routes or [],
        "email_verified": user.email_verified,
        "created_at": user.created_at.isoformat(),
    })


@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    schema = ProfileUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Validation error", "messages": e.messages}), 400

    if "name" in data:
        user.name = sanitize_text(data["name"])
    if "notification_email" in data:
        user.notification_email = data["notification_email"]
    if "webhook_url" in data:
        user.webhook_url = data["webhook_url"]
        if not user.webhook_secret:
            user.webhook_secret = secrets.token_hex(32)
    if "watched_routes" in data:
        user.watched_routes = data["watched_routes"]

    db.session.commit()
    return jsonify({"message": "Profile updated"})


@auth_bp.route("/me/api-keys", methods=["PUT"])
@jwt_required()
def update_api_keys():
    """Store personal AviationStack key (encrypted)."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    aviationstack_key = data.get("aviationstack_key")

    encryption_key = current_app.config.get("ENCRYPTION_KEY")
    if not encryption_key:
        return jsonify({"error": "Encryption not configured"}), 500

    if aviationstack_key:
        encrypted = encrypt_value(aviationstack_key, encryption_key)
        user.personal_api_keys = {"aviationstack_key_enc": encrypted}
    else:
        user.personal_api_keys = {}

    db.session.commit()
    return jsonify({"message": "API keys updated"})


@auth_bp.route("/me/api-key", methods=["GET"])
@jwt_required()
def generate_user_api_key():
    """Generate/rotate user's REST API key. Shows full key only once."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    raw_key, hashed_key = generate_api_key()
    user.api_key_hash = hashed_key
    db.session.commit()

    return jsonify({
        "api_key": raw_key,
        "message": "Save this key - it will not be shown again.",
    })
```

- [ ] **Step 2: Verify auth endpoints work**

```bash
cd d:/airline-booking-analysis-main/backend
python -c "
from app import create_app
app = create_app('development')
with app.app_context():
    rules = [r.rule for r in app.url_map.iter_rules() if r.rule.startswith('/auth')]
    for r in sorted(rules):
        print(r)
"
```

Expected: lists /auth/register, /auth/login, /auth/me, etc.

- [ ] **Step 3: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/auth/
git commit -m "feat: add full auth system (register, login, JWT, profile, API keys)"
```

---

### Task 11: Auth and API tests

**Files:**
- Create: `backend/tests/test_auth.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: Write auth tests**

Create `backend/tests/test_auth.py`:

```python
import pytest


class TestRegister:
    def test_register_success(self, client, db):
        resp = client.post("/auth/register", json={
            "email": "new@example.com",
            "password": "SecurePass1!",
            "name": "Test User",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client, sample_user, db):
        resp = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass1!",
            "name": "Dup User",
        })
        assert resp.status_code == 409

    def test_register_weak_password(self, client, db):
        resp = client.post("/auth/register", json={
            "email": "weak@example.com",
            "password": "short",
            "name": "Weak",
        })
        assert resp.status_code == 400

    def test_register_invalid_email(self, client, db):
        resp = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePass1!",
            "name": "Invalid",
        })
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client, sample_user, db):
        # sample_user is auto-verified in test/dev mode
        sample_user.email_verified = True
        db.session.flush()
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, sample_user, db):
        sample_user.email_verified = True
        db.session.flush()
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPass123!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client, db):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "Anything1!",
        })
        assert resp.status_code == 401

    def test_account_lockout(self, client, sample_user, db):
        sample_user.email_verified = True
        db.session.flush()
        for _ in range(5):
            client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "WrongPass123!",
            })
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 423


class TestProfile:
    def test_get_profile(self, client, auth_headers, db):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert "email" in resp.get_json()

    def test_get_profile_unauthorized(self, client, db):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_update_profile(self, client, auth_headers, db):
        resp = client.put("/auth/me", headers=auth_headers, json={
            "name": "Updated Name",
        })
        assert resp.status_code == 200
```

- [ ] **Step 2: Write API endpoint tests**

Create `backend/tests/test_api.py`:

```python
import pytest
from app.models.flight import Flight, Route
from app.services.data_processor import DataProcessor
from datetime import date


class TestRoutesAPI:
    def test_list_routes_empty(self, client, db):
        resp = client.get("/api/v1/routes/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "routes" in data
        assert data["total"] == 0

    def test_list_routes_with_data(self, client, db, app):
        with app.app_context():
            route = Route(origin="Sydney", destination="Melbourne", distance_km=878)
            db.session.add(route)
            db.session.flush()
            resp = client.get("/api/v1/routes/")
            assert resp.status_code == 200
            assert resp.get_json()["total"] >= 1

    def test_route_detail_not_found(self, client, db):
        resp = client.get("/api/v1/routes/Fake/City")
        assert resp.status_code == 404


class TestPricesAPI:
    def test_prices_empty(self, client, db):
        resp = client.get("/api/v1/prices/")
        assert resp.status_code == 200
        assert "prices" in resp.get_json()

    def test_price_trends_empty(self, client, db):
        resp = client.get("/api/v1/prices/trends")
        assert resp.status_code == 200
        assert "trends" in resp.get_json()


class TestInsightsAPI:
    def test_insights_summary(self, client, db):
        resp = client.get("/api/v1/insights/summary")
        assert resp.status_code == 200
        assert "insights" in resp.get_json()

    def test_insights_briefing(self, client, db):
        resp = client.get("/api/v1/insights/briefing")
        assert resp.status_code == 200

    def test_insights_stream_requires_auth(self, client, db):
        resp = client.get("/api/v1/insights/stream")
        assert resp.status_code == 401


class TestAlertsAPI:
    def test_alerts_requires_auth(self, client, db):
        resp = client.get("/api/v1/alerts/")
        assert resp.status_code == 401

    def test_create_alert(self, client, auth_headers, db):
        resp = client.post("/api/v1/alerts/", headers=auth_headers, json={
            "route": "SYD-MEL",
            "condition": "price_below",
            "threshold_value": 150.0,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["route"] == "SYD-MEL"
        return data["id"]

    def test_list_alerts(self, client, auth_headers, db):
        # Create one first
        client.post("/api/v1/alerts/", headers=auth_headers, json={
            "route": "SYD-BNE",
            "condition": "price_above",
            "threshold_value": 300.0,
        })
        resp = client.get("/api/v1/alerts/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()["alerts"]) >= 1

    def test_delete_alert(self, client, auth_headers, db):
        resp = client.post("/api/v1/alerts/", headers=auth_headers, json={
            "route": "MEL-PER",
            "condition": "demand_spike",
            "threshold_value": 0.8,
        })
        rule_id = resp.get_json()["id"]
        resp = client.delete(f"/api/v1/alerts/{rule_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_invalid_condition(self, client, auth_headers, db):
        resp = client.post("/api/v1/alerts/", headers=auth_headers, json={
            "route": "SYD-MEL",
            "condition": "invalid_condition",
            "threshold_value": 100.0,
        })
        assert resp.status_code == 400


class TestExportAPI:
    def test_csv_requires_auth(self, client, db):
        resp = client.get("/api/v1/export/csv")
        assert resp.status_code == 401

    def test_excel_requires_auth(self, client, db):
        resp = client.get("/api/v1/export/excel")
        assert resp.status_code == 401
```

- [ ] **Step 3: Run all tests**

```bash
cd d:/airline-booking-analysis-main/backend
python -m pytest tests/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/tests/
git commit -m "test: add auth and API endpoint tests"
```

---

### Task 12: Seed data command

**Files:**
- Modify: `backend/app/__init__.py` (add CLI command)

- [ ] **Step 1: Add seed command to app factory**

Add to the bottom of `create_app()` in `backend/app/__init__.py`, before `return app`:

```python
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
```

- [ ] **Step 2: Test the seed command**

```bash
cd d:/airline-booking-analysis-main/backend
FLASK_APP=wsgi:app FLASK_ENV=development flask init-db
FLASK_APP=wsgi:app FLASK_ENV=development flask seed
```

Expected: prints "Seeded 200 flights..." and "Route aggregates updated..."

- [ ] **Step 3: Commit**

```bash
cd d:/airline-booking-analysis-main
git add backend/app/__init__.py
git commit -m "feat: add seed and init-db CLI commands"
```

---

### Task 13: Rate limiting and security hardening

**Files:**
- Modify: `backend/app/__init__.py` (rate limits already in error handlers)
- Modify: `backend/app/auth/routes.py` (rate limits already applied)

- [ ] **Step 1: Verify rate limits are applied**

Rate limits are already set on:
- `/auth/register`: `@limiter.limit("5/minute")`
- `/auth/login`: `@limiter.limit("10/minute")`
- `/auth/forgot-password`: `@limiter.limit("3/minute")`

Verify security headers are being set (already in app factory `after_request`).

- [ ] **Step 2: Run bandit security scan**

```bash
cd d:/airline-booking-analysis-main/backend
pip install bandit
bandit -r app/ -ll
```

Expected: No HIGH severity issues

- [ ] **Step 3: Run full test suite with coverage**

```bash
cd d:/airline-booking-analysis-main/backend
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

Expected: All PASS, >60% coverage for this phase

- [ ] **Step 4: Commit (if any fixes needed)**

```bash
cd d:/airline-booking-analysis-main
git add -A backend/
git commit -m "chore: security hardening verification and test coverage"
```

---

## Summary

After completing all 13 tasks, you will have:
- Flask app factory with all extensions
- 7 database models with full relationships
- Realistic synthetic data generator (200 flights/run, formula-based demand)
- DemandScoreEngine with weighted factor model
- DataProcessor with persistence, route aggregates, anomaly detection
- Full REST API: routes, prices, insights, alerts, export (CSV/Excel), webhooks
- Auth system: register, login, JWT, profile, API key management, account lockout
- Security: bcrypt, rate limiting, security headers, input validation, AES encryption
- Marshmallow validation on all inputs
- CLI commands for seeding data
- Test suite covering models, services, auth, and API endpoints
- Swagger docs at /api/v1/docs
