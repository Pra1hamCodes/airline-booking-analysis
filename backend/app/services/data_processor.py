import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.extensions import db
from app.models.flight import Flight, Route, PriceSnapshot
from app.services.data_scraper import DataScraper, GeneratedFlight, _get_distance


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

            self._ensure_route(f.origin, f.destination)

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

            route.avg_price_7d = round(float(recent_7["price"].mean()), 2) if len(recent_7) > 0 else None
            route.avg_price_30d = round(float(recent_30["price"].mean()), 2) if len(recent_30) > 0 else None
            route.avg_demand_7d = round(float(recent_7["demand_score"].mean()), 4) if len(recent_7) > 0 else None

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
            "avg_price": round(float(df["price"].mean()), 2),
            "peak_demand_score": round(float(df["demand_score"].max()), 4),
        }
