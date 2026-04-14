from flask import Blueprint
from flask_restx import Api

api_v1_bp = Blueprint("api_v1", __name__)
api = Api(
    api_v1_bp,
    version="1.0",
    title="Airline Market Demand API",
    description="REST API for airline booking trend analysis",
    doc="/docs",
)

from .routes import ns as routes_ns  # noqa: E402
from .prices import ns as prices_ns  # noqa: E402
from .insights import ns as insights_ns  # noqa: E402
from .alerts import ns as alerts_ns  # noqa: E402
from .export import ns as export_ns  # noqa: E402
from .webhooks import ns as webhooks_ns  # noqa: E402

api.add_namespace(routes_ns, path="/routes")
api.add_namespace(prices_ns, path="/prices")
api.add_namespace(insights_ns, path="/insights")
api.add_namespace(alerts_ns, path="/alerts")
api.add_namespace(export_ns, path="/export")
api.add_namespace(webhooks_ns, path="/webhooks")
