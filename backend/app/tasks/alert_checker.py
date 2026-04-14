import structlog
from datetime import datetime, timezone

from app.extensions import db
from app.models.alert import AlertRule, AlertFired
from app.models.notification import Notification
from app.models.flight import Route, PriceSnapshot

logger = structlog.get_logger()


def check_alerts():
    """Evaluate all active alert rules against latest data."""
    rules = AlertRule.query.filter_by(is_active=True).all()
    logger.info("Checking alerts", rule_count=len(rules))

    for rule in rules:
        parts = rule.route.replace(" ", "").split("-")
        if len(parts) != 2:
            continue
        origin, dest = parts

        route = Route.query.filter_by(origin=origin, destination=dest).first()
        if not route:
            # Try city name lookup
            route = _find_route_by_code(origin, dest)
        if not route:
            continue

        query = PriceSnapshot.query.filter_by(route_id=route.id)
        if rule.airline:
            query = query.filter_by(airline=rule.airline)

        latest = query.order_by(PriceSnapshot.snapshot_at.desc()).first()
        if not latest:
            continue

        triggered = False
        current_value = latest.price
        message = ""

        if rule.condition == "price_below" and current_value < rule.threshold_value:
            triggered = True
            message = (
                f"Price for {route.origin}-{route.destination} "
                f"dropped to ${current_value:.2f}, below threshold ${rule.threshold_value:.2f}"
            )
        elif rule.condition == "price_above" and current_value > rule.threshold_value:
            triggered = True
            message = (
                f"Price for {route.origin}-{route.destination} "
                f"rose to ${current_value:.2f}, above threshold ${rule.threshold_value:.2f}"
            )
        elif rule.condition == "demand_spike" and latest.demand_score > rule.threshold_value:
            triggered = True
            current_value = latest.demand_score
            message = (
                f"Demand spike on {route.origin}-{route.destination}: "
                f"score {current_value:.2f}, above threshold {rule.threshold_value:.2f}"
            )

        if triggered:
            fired = AlertFired(
                rule_id=rule.id,
                user_id=rule.user_id,
                current_value=current_value,
                threshold_value=rule.threshold_value,
                message=message,
            )
            db.session.add(fired)

            notif = Notification(
                user_id=rule.user_id,
                title="Alert Triggered",
                body=message,
                type="alert",
            )
            db.session.add(notif)
            logger.info("Alert triggered", rule_id=rule.id, message=message)

    db.session.commit()


CITY_CODES = {
    "SYD": "Sydney", "MEL": "Melbourne", "BNE": "Brisbane",
    "PER": "Perth", "ADL": "Adelaide", "DRW": "Darwin",
}


def _find_route_by_code(code1: str, code2: str):
    """Try to find a route by 3-letter city codes."""
    city1 = CITY_CODES.get(code1.upper(), code1)
    city2 = CITY_CODES.get(code2.upper(), code2)
    route = Route.query.filter_by(origin=city1, destination=city2).first()
    if not route:
        route = Route.query.filter_by(origin=city2, destination=city1).first()
    return route
