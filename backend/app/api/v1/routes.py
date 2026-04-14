from flask import request
from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from app.extensions import cache
from app.models.flight import Route, PriceSnapshot, ForecastSnapshot
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

        sort_field = params["sort_by"]
        if sort_field == "demand_score":
            sort_col = Route.avg_demand_7d
        elif sort_field == "price":
            sort_col = Route.avg_price_7d
        else:
            sort_col = getattr(Route, sort_field, Route.avg_demand_7d)

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

        forecasts = (
            ForecastSnapshot.query.filter_by(route_id=route.id)
            .order_by(ForecastSnapshot.forecast_date.asc())
            .limit(56)
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
                {"airline": s.airline, "price": s.price, "snapshot_at": s.snapshot_at.isoformat()}
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
