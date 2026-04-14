import numpy as np
from datetime import date, timedelta, datetime, timezone
from typing import List, Optional, Tuple

from app.extensions import db
from app.models.flight import Route, PriceSnapshot, ForecastSnapshot


class PriceForecastEngine:
    def get_forecast(
        self,
        origin: str,
        destination: str,
        airline: str,
        days: int = 14,
    ) -> Optional[List[dict]]:
        """
        Produce forward price forecasts for a route+airline.
        Returns list of {date, predicted_price, lower_bound, upper_bound} or None if insufficient data.
        """
        route = Route.query.filter_by(origin=origin, destination=destination).first()
        if not route:
            route = Route.query.filter_by(origin=destination, destination=origin).first()
        if not route:
            return None

        snapshots = (
            PriceSnapshot.query.filter_by(route_id=route.id, airline=airline)
            .order_by(PriceSnapshot.snapshot_at.asc())
            .all()
        )

        if len(snapshots) < 5:
            return None

        prices = np.array([s.price for s in snapshots])
        n = len(prices)
        x = np.arange(n).reshape(-1, 1)

        if n >= 30:
            forecasts = self._arima_forecast(prices, days)
        else:
            forecasts = self._polynomial_forecast(x, prices, days, n)

        today = date.today()
        results = []
        for i, (pred, lower, upper) in enumerate(forecasts):
            forecast_date = today + timedelta(days=i + 1)
            results.append({
                "date": forecast_date,
                "predicted_price": round(max(pred, 0), 2),
                "lower_bound": round(max(lower, 0), 2),
                "upper_bound": round(max(upper, 0), 2),
            })

        return results

    def _polynomial_forecast(self, x, prices, days, n):
        """Polynomial regression (degree 2) forecast."""
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures

        poly = PolynomialFeatures(degree=2)
        x_poly = poly.fit_transform(x)

        model = LinearRegression()
        model.fit(x_poly, prices)

        residuals = prices - model.predict(x_poly)
        std_err = np.std(residuals)

        forecasts = []
        for i in range(days):
            future_x = np.array([[n + i]])
            future_x_poly = poly.transform(future_x)
            pred = model.predict(future_x_poly)[0]
            forecasts.append((pred, pred - 1.96 * std_err, pred + 1.96 * std_err))

        return forecasts

    def _arima_forecast(self, prices, days):
        """ARIMA(1,1,1) forecast for routes with sufficient history."""
        try:
            from statsmodels.tsa.arima.model import ARIMA

            model = ARIMA(prices, order=(1, 1, 1))
            fitted = model.fit()

            forecast_result = fitted.get_forecast(steps=days)
            predicted = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int(alpha=0.05)

            forecasts = []
            for i in range(days):
                pred = predicted.iloc[i] if hasattr(predicted, 'iloc') else predicted[i]
                lower = conf_int.iloc[i, 0] if hasattr(conf_int, 'iloc') else conf_int[i, 0]
                upper = conf_int.iloc[i, 1] if hasattr(conf_int, 'iloc') else conf_int[i, 1]
                forecasts.append((pred, lower, upper))

            return forecasts
        except Exception:
            # Fall back to polynomial if ARIMA fails
            n = len(prices)
            x = np.arange(n).reshape(-1, 1)
            return self._polynomial_forecast(x, prices, days, n)

    def generate_and_store_forecasts(self, route_id: str, airline: str, days: int = 14):
        """Generate forecasts and persist to DB."""
        route = db.session.get(Route, route_id)
        if not route:
            return

        forecasts = self.get_forecast(route.origin, route.destination, airline, days)
        if not forecasts:
            return

        # Remove old forecasts for this route+airline
        ForecastSnapshot.query.filter_by(route_id=route_id, airline=airline).delete()

        for f in forecasts:
            snap = ForecastSnapshot(
                route_id=route_id,
                airline=airline,
                forecast_date=f["date"],
                predicted_price=f["predicted_price"],
                lower_bound=f["lower_bound"],
                upper_bound=f["upper_bound"],
            )
            db.session.add(snap)

        db.session.commit()

    def generate_all_forecasts(self):
        """Generate forecasts for all route+airline combos with sufficient data."""
        routes = Route.query.all()
        airlines = ["Qantas", "Virgin Australia", "Jetstar", "Tiger Airways"]

        for route in routes:
            for airline in airlines:
                self.generate_and_store_forecasts(route.id, airline)
