import io
from datetime import date
from typing import List, Optional

import pandas as pd

from app.models.flight import Flight, Route, PriceSnapshot


class ReportGenerator:
    def generate_csv(self, date_from: Optional[date] = None, date_to: Optional[date] = None) -> bytes:
        """Generate CSV report bytes."""
        query = Flight.query.order_by(Flight.created_at.desc())
        if date_from:
            query = query.filter(Flight.date >= date_from)
        if date_to:
            query = query.filter(Flight.date <= date_to)

        flights = query.limit(5000).all()

        output = io.StringIO()
        import csv
        writer = csv.writer(output)
        writer.writerow([
            "origin", "destination", "price", "date", "airline",
            "demand_score", "days_until_departure", "season", "is_anomaly",
        ])
        for f in flights:
            writer.writerow([
                f.origin, f.destination, f.price, f.date.isoformat() if f.date else "",
                f.airline, f.demand_score, f.days_until_departure, f.season, f.is_anomaly,
            ])

        return output.getvalue().encode("utf-8")

    def generate_excel(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        route_filters: Optional[List[str]] = None,
    ) -> bytes:
        """Generate Excel report bytes with multiple sheets."""
        query = Flight.query.order_by(Flight.created_at.desc())
        if date_from:
            query = query.filter(Flight.date >= date_from)
        if date_to:
            query = query.filter(Flight.date <= date_to)

        flights = query.limit(5000).all()
        routes = Route.query.all()

        flights_df = pd.DataFrame([
            {
                "Origin": f.origin, "Destination": f.destination,
                "Price (AUD)": f.price,
                "Date": f.date.isoformat() if f.date else "",
                "Airline": f.airline,
                "Demand Score": f.demand_score,
                "Season": f.season,
                "Anomaly": f.is_anomaly,
            }
            for f in flights
        ])

        routes_df = pd.DataFrame([
            {
                "Origin": r.origin, "Destination": r.destination,
                "Distance (km)": r.distance_km,
                "Avg Price 7d": r.avg_price_7d,
                "Avg Price 30d": r.avg_price_30d,
                "Avg Demand 7d": r.avg_demand_7d,
                "Demand Trend": r.demand_trend,
            }
            for r in routes
        ])

        from app.services.data_processor import DataProcessor
        processor = DataProcessor()
        insights = processor.get_market_insights()

        overview_df = pd.DataFrame([
            {"Metric": "Total Flights", "Value": insights["total_flights"]},
            {"Metric": "Average Price (AUD)", "Value": insights["avg_price"]},
            {"Metric": "Peak Demand Score", "Value": insights["peak_demand_score"]},
            {"Metric": "Report Period", "Value": f"{date_from or 'all'} to {date_to or 'all'}"},
        ])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            overview_df.to_excel(writer, sheet_name="Overview", index=False)
            routes_df.to_excel(writer, sheet_name="Routes", index=False)
            flights_df.to_excel(writer, sheet_name="Flights", index=False)
        output.seek(0)
        return output.read()

    def generate_pdf_report(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        route_filters: Optional[List[str]] = None,
        include_forecast: bool = False,
    ) -> bytes:
        """Generate PDF report. Returns PDF bytes."""
        from app.services.data_processor import DataProcessor

        processor = DataProcessor()
        insights = processor.get_market_insights()

        top_routes_html = ""
        for r in insights.get("popular_routes", [])[:10]:
            top_routes_html += (
                f"<tr><td>{r['route']}</td>"
                f"<td>${r['price']:.2f}</td>"
                f"<td>{r['demand_score']:.2f}</td></tr>"
            )

        airline_html = ""
        for a in insights.get("airline_stats", []):
            airline_html += (
                f"<tr><td>{a['airline']}</td>"
                f"<td>${a['price']:.2f}</td>"
                f"<td>{a['demand_score']:.2f}</td></tr>"
            )

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Helvetica, Arial, sans-serif; margin: 40px; color: #333; }}
                h1 {{ color: #2D7EF7; }}
                h2 {{ color: #0A0F1E; border-bottom: 2px solid #2D7EF7; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #2D7EF7; color: white; }}
                .metric {{ font-size: 24px; font-weight: bold; color: #2D7EF7; }}
                .metric-label {{ font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <h1>Airline Market Demand Report</h1>
            <p>Period: {date_from or 'All time'} to {date_to or 'Present'}</p>

            <h2>Market Overview</h2>
            <div style="display: flex; gap: 40px;">
                <div>
                    <div class="metric">{insights['total_flights']}</div>
                    <div class="metric-label">Total Flights</div>
                </div>
                <div>
                    <div class="metric">${insights['avg_price']:.2f}</div>
                    <div class="metric-label">Avg Price (AUD)</div>
                </div>
                <div>
                    <div class="metric">{insights['peak_demand_score']:.2f}</div>
                    <div class="metric-label">Peak Demand</div>
                </div>
            </div>

            <h2>Top Routes by Demand</h2>
            <table>
                <tr><th>Route</th><th>Avg Price</th><th>Demand Score</th></tr>
                {top_routes_html}
            </table>

            <h2>Airline Comparison</h2>
            <table>
                <tr><th>Airline</th><th>Avg Price</th><th>Demand Score</th></tr>
                {airline_html}
            </table>
        </body>
        </html>
        """

        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html).write_pdf()
            return pdf_bytes
        except ImportError:
            # WeasyPrint not available (Windows dev), return HTML as fallback
            return html.encode("utf-8")
