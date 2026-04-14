from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.alert import AlertRule, AlertFired
from app.models.notification import Notification
from app.utils.validators import AlertRuleSchema, AlertRuleUpdateSchema
from app.utils.security import sanitize_text

ns = Namespace("alerts", description="Alert rule operations")


@ns.route("/")
class AlertRuleList(Resource):
    @jwt_required()
    def get(self):
        """List alert rules for current user."""
        user_id = get_jwt_identity()
        rules = AlertRule.query.filter_by(user_id=user_id).order_by(AlertRule.created_at.desc()).all()
        return {
            "alerts": [
                {
                    "id": r.id,
                    "route": r.route,
                    "airline": r.airline,
                    "condition": r.condition,
                    "threshold_value": r.threshold_value,
                    "is_active": r.is_active,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rules
            ]
        }

    @jwt_required()
    def post(self):
        """Create a new alert rule."""
        schema = AlertRuleSchema()
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as e:
            return {"error": "Validation error", "messages": e.messages}, 400

        user_id = get_jwt_identity()
        rule = AlertRule(
            user_id=user_id,
            route=sanitize_text(data["route"]),
            airline=sanitize_text(data["airline"]) if data.get("airline") else None,
            condition=data["condition"],
            threshold_value=data["threshold_value"],
            is_active=data.get("is_active", True),
        )
        db.session.add(rule)
        db.session.commit()

        return {
            "id": rule.id,
            "route": rule.route,
            "airline": rule.airline,
            "condition": rule.condition,
            "threshold_value": rule.threshold_value,
            "is_active": rule.is_active,
        }, 201


@ns.route("/<string:rule_id>")
class AlertRuleDetail(Resource):
    @jwt_required()
    def put(self, rule_id):
        """Update an alert rule."""
        user_id = get_jwt_identity()
        rule = AlertRule.query.filter_by(id=rule_id, user_id=user_id).first()
        if not rule:
            return {"error": "Alert rule not found"}, 404

        schema = AlertRuleUpdateSchema()
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as e:
            return {"error": "Validation error", "messages": e.messages}, 400

        if "route" in data:
            rule.route = sanitize_text(data["route"])
        if "airline" in data:
            rule.airline = sanitize_text(data["airline"]) if data["airline"] else None
        if "condition" in data:
            rule.condition = data["condition"]
        if "threshold_value" in data:
            rule.threshold_value = data["threshold_value"]
        if "is_active" in data:
            rule.is_active = data["is_active"]

        db.session.commit()
        return {"message": "Updated", "id": rule.id}

    @jwt_required()
    def delete(self, rule_id):
        """Delete an alert rule."""
        user_id = get_jwt_identity()
        rule = AlertRule.query.filter_by(id=rule_id, user_id=user_id).first()
        if not rule:
            return {"error": "Alert rule not found"}, 404

        db.session.delete(rule)
        db.session.commit()
        return {"message": "Deleted"}, 200


@ns.route("/fired")
class AlertFiredList(Resource):
    @jwt_required()
    def get(self):
        """AlertFired history for current user."""
        user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        query = AlertFired.query.filter_by(user_id=user_id).order_by(AlertFired.triggered_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "alerts_fired": [
                {
                    "id": a.id,
                    "rule_id": a.rule_id,
                    "triggered_at": a.triggered_at.isoformat(),
                    "current_value": a.current_value,
                    "threshold_value": a.threshold_value,
                    "message": a.message,
                    "is_read": a.is_read,
                }
                for a in pagination.items
            ],
            "total": pagination.total,
            "page": page,
        }


@ns.route("/notifications")
class NotificationList(Resource):
    @jwt_required()
    def get(self):
        """Unread notifications for current user."""
        user_id = get_jwt_identity()
        notifications = (
            Notification.query.filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )
        return {
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "body": n.body,
                    "type": n.type,
                    "created_at": n.created_at.isoformat(),
                }
                for n in notifications
            ]
        }


@ns.route("/notifications/<string:notif_id>/read")
class NotificationRead(Resource):
    @jwt_required()
    def post(self, notif_id):
        """Mark notification as read."""
        user_id = get_jwt_identity()
        notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
        if not notif:
            return {"error": "Notification not found"}, 404
        notif.is_read = True
        db.session.commit()
        return {"message": "Marked as read"}
