import json
import requests
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.utils.security import sign_webhook_payload

ns = Namespace("webhooks", description="Webhook operations")


@ns.route("/test")
class WebhookTest(Resource):
    @jwt_required()
    def post(self):
        """Send a test webhook payload to user's configured URL."""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user or not user.webhook_url:
            return {"error": "No webhook URL configured"}, 400

        payload = json.dumps({
            "event": "test",
            "message": "This is a test webhook from Airline Market Demand API",
            "user_id": user.id,
        }).encode()

        signature = sign_webhook_payload(payload, user.webhook_secret or "default-secret")

        try:
            resp = requests.post(
                user.webhook_url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature-256": signature,
                },
                timeout=10,
            )
            return {"status": "sent", "response_code": resp.status_code}
        except requests.RequestException as e:
            return {"error": f"Webhook delivery failed: {str(e)}"}, 502
