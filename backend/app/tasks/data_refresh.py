import structlog
from app.extensions import db, cache
from app.services.data_processor import DataProcessor
from app.services.forecast_engine import PriceForecastEngine

logger = structlog.get_logger()


def refresh_flight_data():
    """Refresh flight data: generate, persist, update aggregates, detect anomalies, run forecasts."""
    logger.info("Starting flight data refresh")

    processor = DataProcessor()

    # 1. Generate new flights
    flights = processor.scraper.generate_flights(count=200)

    # 2. Persist to DB
    run_id = processor.persist_flights(flights)
    logger.info("Persisted flights", run_id=run_id, count=len(flights))

    # 3. Update route aggregates
    processor.update_route_aggregates()
    logger.info("Route aggregates updated")

    # 4. Anomaly detection
    processor.detect_anomalies()
    logger.info("Anomaly detection complete")

    # 5. Generate forecasts
    forecast_engine = PriceForecastEngine()
    forecast_engine.generate_all_forecasts()
    logger.info("Forecasts generated")

    # 6. Invalidate cache
    cache.clear()
    logger.info("Cache invalidated")

    # 7. Check alerts
    from app.tasks.alert_checker import check_alerts
    check_alerts()

    logger.info("Flight data refresh complete", run_id=run_id)
    return run_id
