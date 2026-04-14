import pytest
from datetime import date


class TestDemandScoreEngine:
    def test_demand_score_in_valid_range(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        score = engine.calculate(
            origin="Sydney",
            destination="Melbourne",
            flight_date=date(2026, 1, 15),
            days_until_departure=5,
            day_of_week=4,
        )
        assert 0.0 <= score <= 1.0

    def test_high_demand_summer_holiday_soon(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        score = engine.calculate(
            origin="Sydney",
            destination="Melbourne",
            flight_date=date(2026, 1, 10),
            days_until_departure=3,
            day_of_week=4,
        )
        assert score > 0.5

    def test_low_demand_offpeak_far_out(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        score = engine.calculate(
            origin="Adelaide",
            destination="Darwin",
            flight_date=date(2026, 5, 13),
            days_until_departure=80,
            day_of_week=2,
        )
        assert score < 0.5

    def test_popular_route_scores_higher(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        kwargs = dict(
            flight_date=date(2026, 6, 15),
            days_until_departure=14,
            day_of_week=0,
        )
        score_popular = engine.calculate(origin="Sydney", destination="Melbourne", **kwargs)
        score_niche = engine.calculate(origin="Adelaide", destination="Darwin", **kwargs)
        assert score_popular > score_niche

    def test_holiday_proximity_boosts_score(self, app):
        from app.services.demand_engine import DemandScoreEngine

        engine = DemandScoreEngine()
        base_kwargs = dict(
            origin="Sydney",
            destination="Brisbane",
            days_until_departure=14,
            day_of_week=0,
        )
        score_near_holiday = engine.calculate(flight_date=date(2026, 1, 20), **base_kwargs)
        score_far_holiday = engine.calculate(flight_date=date(2026, 3, 10), **base_kwargs)
        assert score_near_holiday > score_far_holiday


class TestDataScraper:
    def test_generates_200_flights(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        assert len(flights) == 200

    def test_flight_fields_present(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        flight = flights[0]
        assert hasattr(flight, "origin")
        assert hasattr(flight, "destination")
        assert hasattr(flight, "price")
        assert hasattr(flight, "airline")
        assert hasattr(flight, "demand_score")
        assert hasattr(flight, "days_until_departure")

    def test_airline_multipliers_affect_price(self, app):
        from app.services.data_scraper import DataScraper
        import pandas as pd

        scraper = DataScraper()
        flights = scraper.generate_flights()
        df = pd.DataFrame([vars(f) for f in flights])
        avg_prices = df.groupby("airline")["price"].mean()
        if "Qantas" in avg_prices.index and "Tiger Airways" in avg_prices.index:
            assert avg_prices["Qantas"] > avg_prices["Tiger Airways"]

    def test_demand_scores_in_range(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        for f in flights:
            assert 0.0 <= f.demand_score <= 1.0

    def test_all_cities_represented(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        origins = {f.origin for f in flights}
        destinations = {f.destination for f in flights}
        all_cities = origins | destinations
        expected = {"Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Darwin"}
        assert expected.issubset(all_cities)

    def test_origin_never_equals_destination(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        for f in flights:
            assert f.origin != f.destination

    def test_run_id_is_consistent(self, app):
        from app.services.data_scraper import DataScraper

        scraper = DataScraper()
        flights = scraper.generate_flights()
        run_ids = {f.run_id for f in flights}
        assert len(run_ids) == 1
