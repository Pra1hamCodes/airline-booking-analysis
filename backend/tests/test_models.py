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
