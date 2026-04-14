from flask_restx import Namespace, Resource

from app.extensions import cache
from app.services.data_processor import DataProcessor

ns = Namespace("insights", description="Market insights")


@ns.route("/summary")
class InsightsSummary(Resource):
    @cache.cached(timeout=300)
    def get(self):
        """Full market summary from processed data."""
        processor = DataProcessor()
        insights = processor.get_market_insights()
        return {"insights": insights}
