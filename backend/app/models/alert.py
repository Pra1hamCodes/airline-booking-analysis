import uuid
from datetime import datetime, timezone

from app.extensions import db


class AlertRule(db.Model):
    __tablename__ = "alert_rules"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    route = db.Column(db.String(100), nullable=False)
    airline = db.Column(db.String(100), nullable=True)
    condition = db.Column(db.String(30), nullable=False)
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
