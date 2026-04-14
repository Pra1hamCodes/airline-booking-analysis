import pytest
from app.models.flight import Flight, Route
from datetime import date


class TestRoutesAPI:
    def test_list_routes_empty(self, client, db):
        resp = client.get("/api/v1/routes/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "routes" in data
        assert data["total"] == 0

    def test_list_routes_with_data(self, client, db, app):
        from app.extensions import cache as app_cache
        with app.app_context():
            app_cache.clear()
            route = Route(origin="Sydney", destination="Melbourne", distance_km=878)
            db.session.add(route)
            db.session.commit()
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

    def test_list_alerts(self, client, auth_headers, db):
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
