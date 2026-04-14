import uuid
from datetime import datetime, timezone

from app.extensions import db, bcrypt, login_manager


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    plan = db.Column(db.String(20), nullable=False, default="free")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    users = db.relationship("User", backref="organization", lazy="dynamic")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    organization_id = db.Column(db.String(36), db.ForeignKey("organizations.id"), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="member")
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
        locked = self.locked_until
        if locked.tzinfo is None:
            locked = locked.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < locked


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
