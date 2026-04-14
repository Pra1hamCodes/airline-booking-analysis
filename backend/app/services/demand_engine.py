from datetime import date, timedelta


AU_SCHOOL_HOLIDAYS = [
    # 2024
    (date(2024, 1, 1), date(2024, 1, 28)),
    (date(2024, 4, 6), date(2024, 4, 22)),
    (date(2024, 6, 29), date(2024, 7, 14)),
    (date(2024, 9, 21), date(2024, 10, 7)),
    (date(2024, 12, 18), date(2024, 12, 31)),
    # 2025
    (date(2025, 1, 1), date(2025, 1, 27)),
    (date(2025, 4, 5), date(2025, 4, 21)),
    (date(2025, 6, 28), date(2025, 7, 13)),
    (date(2025, 9, 20), date(2025, 10, 6)),
    (date(2025, 12, 17), date(2025, 12, 31)),
    # 2026
    (date(2026, 1, 1), date(2026, 1, 26)),
    (date(2026, 4, 4), date(2026, 4, 20)),
    (date(2026, 6, 27), date(2026, 7, 12)),
    (date(2026, 9, 19), date(2026, 10, 5)),
    (date(2026, 12, 16), date(2026, 12, 31)),
]

AU_PUBLIC_HOLIDAYS = [
    # 2024
    date(2024, 1, 1), date(2024, 1, 26), date(2024, 3, 29), date(2024, 4, 1),
    date(2024, 4, 25), date(2024, 6, 10), date(2024, 12, 25), date(2024, 12, 26),
    # 2025
    date(2025, 1, 1), date(2025, 1, 27), date(2025, 4, 18), date(2025, 4, 21),
    date(2025, 4, 25), date(2025, 6, 9), date(2025, 12, 25), date(2025, 12, 26),
    # 2026
    date(2026, 1, 1), date(2026, 1, 26), date(2026, 4, 3), date(2026, 4, 6),
    date(2026, 4, 25), date(2026, 6, 8), date(2026, 12, 25), date(2026, 12, 26),
]

ROUTE_POPULARITY = {
    ("Sydney", "Melbourne"): 1.0,
    ("Melbourne", "Sydney"): 1.0,
    ("Sydney", "Brisbane"): 0.85,
    ("Brisbane", "Sydney"): 0.85,
    ("Melbourne", "Brisbane"): 0.75,
    ("Brisbane", "Melbourne"): 0.75,
    ("Sydney", "Perth"): 0.70,
    ("Perth", "Sydney"): 0.70,
    ("Sydney", "Adelaide"): 0.60,
    ("Adelaide", "Sydney"): 0.60,
    ("Melbourne", "Perth"): 0.65,
    ("Perth", "Melbourne"): 0.65,
    ("Melbourne", "Adelaide"): 0.55,
    ("Adelaide", "Melbourne"): 0.55,
    ("Brisbane", "Perth"): 0.40,
    ("Perth", "Brisbane"): 0.40,
    ("Brisbane", "Adelaide"): 0.35,
    ("Adelaide", "Brisbane"): 0.35,
    ("Brisbane", "Darwin"): 0.45,
    ("Darwin", "Brisbane"): 0.45,
    ("Sydney", "Darwin"): 0.50,
    ("Darwin", "Sydney"): 0.50,
    ("Melbourne", "Darwin"): 0.40,
    ("Darwin", "Melbourne"): 0.40,
    ("Perth", "Adelaide"): 0.30,
    ("Adelaide", "Perth"): 0.30,
    ("Perth", "Darwin"): 0.35,
    ("Darwin", "Perth"): 0.35,
    ("Adelaide", "Darwin"): 0.25,
    ("Darwin", "Adelaide"): 0.25,
}


class DemandScoreEngine:
    def calculate(
        self,
        origin: str,
        destination: str,
        flight_date: date,
        days_until_departure: int,
        day_of_week: int,
    ) -> float:
        route_pop = self._route_popularity(origin, destination)
        season = self._seasonality_factor(flight_date)
        days_factor = self._days_until_factor(days_until_departure)
        dow_factor = self._day_of_week_factor(day_of_week)
        holiday = self._holiday_proximity_factor(flight_date)

        score = (
            0.30 * route_pop
            + 0.25 * season
            + 0.20 * days_factor
            + 0.15 * dow_factor
            + 0.10 * holiday
        )
        return max(0.0, min(1.0, score))

    def _route_popularity(self, origin: str, destination: str) -> float:
        return ROUTE_POPULARITY.get((origin, destination), 0.3)

    def _seasonality_factor(self, flight_date: date) -> float:
        for start, end in AU_SCHOOL_HOLIDAYS:
            if start <= flight_date <= end:
                return 1.0
        month = flight_date.month
        if month in (12, 1, 2):
            return 0.9
        if month in (6, 7, 8):
            return 0.6
        return 0.4

    def _days_until_factor(self, days: int) -> float:
        if days <= 7:
            return 0.9
        if days <= 21:
            return 0.6
        if days <= 60:
            return 0.4
        return 0.2

    def _day_of_week_factor(self, dow: int) -> float:
        if dow in (0, 4):
            return 0.8
        if dow in (5, 6):
            return 0.9
        return 0.5

    def _holiday_proximity_factor(self, flight_date: date) -> float:
        for holiday in AU_PUBLIC_HOLIDAYS:
            if abs((flight_date - holiday).days) <= 14:
                return 0.8
        return 0.1
