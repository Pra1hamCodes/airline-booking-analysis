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
    demand_trend = db.Column(db.String(20), default="stable")
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
