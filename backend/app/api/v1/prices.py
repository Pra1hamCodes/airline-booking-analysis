from flask import request
from flask_restx import Namespace, Resource

from app.extensions import cache
from app.models.flight import PriceSnapshot, Flight, Route, ForecastSnapshot

ns = Namespace("prices", description="Price operations")


@ns.route("/forecast")
class PriceForecast(Resource):
    @cache.cached(timeout=300, query_string=True)
    def get(self):
        """Return forecast rows for a route string like 'Sydney-Melbourne'."""
        route_str = request.args.get("route", "")
        parts = route_str.split("-")
        if len(parts) != 2:
            return {"error": "route must be 'Origin-Destination'"}, 400
        origin, destination = parts[0].strip(), parts[1].strip()
        route = Route.query.filter_by(origin=origin, destination=destination).first()
        if not route:
            return {"forecast": []}

        rows = (
            ForecastSnapshot.query.filter_by(route_id=route.id)
            .order_by(ForecastSnapshot.forecast_date.asc())
            .limit(56)
            .all()
        )
        # Average across airlines per date for cleaner chart
        by_date = {}
        for r in rows:
            d = r.forecast_date.isoformat()
            if d not in by_date:
                by_date[d] = {"date": d, "pred": [], "lo": [], "hi": []}
            by_date[d]["pred"].append(r.predicted_price)
            by_date[d]["lo"].append(r.lower_bound)
            by_date[d]["hi"].append(r.upper_bound)

        forecast = [
            {
                "date": d,
                "predicted_price": round(sum(v["pred"]) / len(v["pred"]), 2),
                "lower_bound": round(sum(v["lo"]) / len(v["lo"]), 2),
                "upper_bound": round(sum(v["hi"]) / len(v["hi"]), 2),
            }
            for d, v in sorted(by_date.items())
        ]
        return {"route": route_str, "forecast": forecast}


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
        flights = Flight.query.filter(Flight.created_at >= thirty_days_ago).all()

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

        trends = df.groupby(["origin", "destination", "date"])["price"].mean().reset_index()
        trends["route"] = trends["origin"] + " - " + trends["destination"]
        trends["price"] = trends["price"].round(2)

        return {"trends": trends[["route", "date", "price"]].to_dict("records")}
