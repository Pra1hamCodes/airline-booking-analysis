import uuid
import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List

from .demand_engine import DemandScoreEngine

CITIES = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Darwin"]

ROUTE_BASE_PRICES = {
    ("Sydney", "Melbourne"): 120,
    ("Sydney", "Brisbane"): 180,
    ("Sydney", "Perth"): 350,
    ("Sydney", "Adelaide"): 200,
    ("Sydney", "Darwin"): 420,
    ("Melbourne", "Brisbane"): 220,
    ("Melbourne", "Perth"): 380,
    ("Melbourne", "Adelaide"): 150,
    ("Melbourne", "Darwin"): 450,
    ("Brisbane", "Perth"): 480,
    ("Brisbane", "Adelaide"): 280,
    ("Brisbane", "Darwin"): 320,
    ("Perth", "Adelaide"): 300,
    ("Perth", "Darwin"): 260,
    ("Adelaide", "Darwin"): 380,
}

AIRLINE_PRICE_MULTIPLIERS = {
    "Qantas": 1.25,
    "Virgin Australia": 1.10,
    "Jetstar": 0.85,
    "Tiger Airways": 0.75,
}

AIRLINES = list(AIRLINE_PRICE_MULTIPLIERS.keys())

ROUTE_DISTANCES_KM = {
    ("Sydney", "Melbourne"): 878,
    ("Sydney", "Brisbane"): 732,
    ("Sydney", "Perth"): 3290,
    ("Sydney", "Adelaide"): 1165,
    ("Sydney", "Darwin"): 3150,
    ("Melbourne", "Brisbane"): 1378,
    ("Melbourne", "Perth"): 2721,
    ("Melbourne", "Adelaide"): 654,
    ("Melbourne", "Darwin"): 3144,
    ("Brisbane", "Perth"): 3604,
    ("Brisbane", "Adelaide"): 1600,
    ("Brisbane", "Darwin"): 2852,
    ("Perth", "Adelaide"): 2130,
    ("Perth", "Darwin"): 2644,
    ("Adelaide", "Darwin"): 2622,
}


def _get_base_price(origin: str, destination: str) -> int:
    key = (origin, destination)
    if key in ROUTE_BASE_PRICES:
        return ROUTE_BASE_PRICES[key]
    reverse_key = (destination, origin)
    if reverse_key in ROUTE_BASE_PRICES:
        return ROUTE_BASE_PRICES[reverse_key]
    return 250


def _get_distance(origin: str, destination: str) -> int:
    key = (origin, destination)
    if key in ROUTE_DISTANCES_KM:
        return ROUTE_DISTANCES_KM[key]
    reverse_key = (destination, origin)
    if reverse_key in ROUTE_DISTANCES_KM:
        return ROUTE_DISTANCES_KM[reverse_key]
    return 1500


def _get_season(d: date) -> str:
    month = d.month
    if month in (12, 1, 2):
        return "summer"
    if month in (3, 4, 5):
        return "autumn"
    if month in (6, 7, 8):
        return "winter"
    return "spring"


@dataclass
class GeneratedFlight:
    run_id: str
    origin: str
    destination: str
    price: float
    date: date
    airline: str
    demand_score: float
    days_until_departure: int
    day_of_week: int
    season: str
    distance_km: int = 0


class DataScraper:
    def __init__(self):
        self.demand_engine = DemandScoreEngine()

    def generate_flights(self, count: int = 200) -> List[GeneratedFlight]:
        run_id = str(uuid.uuid4())
        today = date.today()
        flights = []

        for _ in range(count):
            origin = random.choice(CITIES)
            destination = random.choice([c for c in CITIES if c != origin])
            airline = random.choice(AIRLINES)
            days_until = random.randint(1, 90)
            flight_date = today + timedelta(days=days_until)
            dow = flight_date.weekday()

            demand_score = self.demand_engine.calculate(
                origin=origin,
                destination=destination,
                flight_date=flight_date,
                days_until_departure=days_until,
                day_of_week=dow,
            )

            base_price = _get_base_price(origin, destination)
            multiplier = AIRLINE_PRICE_MULTIPLIERS[airline]
            price = base_price * multiplier * (1 + demand_score * 0.6) * random.gauss(1.0, 0.05)
            price = round(max(price, 50.0), 2)

            flights.append(
                GeneratedFlight(
                    run_id=run_id,
                    origin=origin,
                    destination=destination,
                    price=price,
                    date=flight_date,
                    airline=airline,
                    demand_score=round(demand_score, 4),
                    days_until_departure=days_until,
                    day_of_week=dow,
                    season=_get_season(flight_date),
                    distance_km=_get_distance(origin, destination),
                )
            )

        return flights
