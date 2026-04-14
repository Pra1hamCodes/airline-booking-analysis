"""Seed script - builds ~60 days of historical snapshots, aggregates, anomalies, forecasts."""
import random
import uuid
from datetime import date, datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models.flight import Flight, Route, PriceSnapshot, ForecastSnapshot
from app.services.data_scraper import (
    CITIES, AIRLINES, AIRLINE_PRICE_MULTIPLIERS, ROUTE_BASE_PRICES,
    _get_base_price, _get_distance, _get_season,
)
from app.services.demand_engine import DemandScoreEngine
from app.services.data_processor import DataProcessor
from app.services.forecast_engine import PriceForecastEngine


def seed():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        # Clear existing
        db.session.query(ForecastSnapshot).delete()
        db.session.query(PriceSnapshot).delete()
        db.session.query(Flight).delete()
        db.session.query(Route).delete()
        db.session.commit()

        # Create all routes
        for (o, d) in ROUTE_BASE_PRICES.keys():
            for origin, dest in ((o, d), (d, o)):
                db.session.add(Route(
                    origin=origin, destination=dest,
                    distance_km=_get_distance(origin, dest),
                ))
        db.session.commit()
        routes = Route.query.all()
        print(f"Routes: {len(routes)}")

        engine = DemandScoreEngine()
        today = date.today()

        # Create 60 days of snapshots + forward flights
        run_id = str(uuid.uuid4())
        snap_count = 0
        flight_count = 0
        for route in routes:
            for days_back in range(60, 0, -1):
                snap_date = today - timedelta(days=days_back)
                for airline in AIRLINES:
                    if random.random() > 0.75:
                        continue
                    future_days = random.randint(3, 60)
                    flight_date = snap_date + timedelta(days=future_days)
                    dow = flight_date.weekday()
                    demand = engine.calculate(
                        origin=route.origin, destination=route.destination,
                        flight_date=flight_date, days_until_departure=future_days,
                        day_of_week=dow,
                    )
                    base = _get_base_price(route.origin, route.destination)
                    mult = AIRLINE_PRICE_MULTIPLIERS[airline]
                    price = round(max(base * mult * (1 + demand * 0.6) * random.gauss(1.0, 0.07), 50.0), 2)

                    snap = PriceSnapshot(
                        route_id=route.id, airline=airline,
                        price=price, demand_score=round(demand, 4),
                    )
                    # set snapshot time to past
                    snap.snapshot_at = datetime.combine(snap_date, datetime.min.time(), tzinfo=timezone.utc)
                    db.session.add(snap)
                    snap_count += 1

                    db.session.add(Flight(
                        run_id=run_id, origin=route.origin, destination=route.destination,
                        price=price, date=flight_date, airline=airline,
                        demand_score=round(demand, 4), days_until_departure=future_days,
                        day_of_week=dow, season=_get_season(flight_date),
                    ))
                    flight_count += 1
            if snap_count % 2000 == 0:
                db.session.commit()
        db.session.commit()
        print(f"Snapshots: {snap_count}, Flights: {flight_count}")

        # Aggregates + anomalies
        processor = DataProcessor()
        processor.update_route_aggregates()
        processor.detect_anomalies()
        print("Aggregates + anomalies computed")

        # Forecasts
        fe = PriceForecastEngine()
        fe.generate_all_forecasts()
        print(f"Forecasts: {ForecastSnapshot.query.count()}")


if __name__ == "__main__":
    seed()
