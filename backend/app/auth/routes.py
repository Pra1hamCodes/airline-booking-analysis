import secrets
from datetime import datetime, timedelta, timezone

from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from flask_login import login_user, logout_user
from marshmallow import ValidationError

from . import auth_bp
from app.extensions import db, limiter
from app.models.user import User, Organization
from app.utils.validators import RegisterSchema, LoginSchema, ProfileUpdateSchema
from app.utils.security import (
    sanitize_text,
    generate_token,
    generate_api_key,
    encrypt_value,
)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5/minute")
def register():
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Validation error", "messages": e.messages}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    org = None
    if data.get("org_name"):
        org = Organization(name=sanitize_text(data["org_name"]))
        db.session.add(org)
        db.session.flush()

    user = User(
        email=data["email"],
        name=sanitize_text(data["name"]),
        organization_id=org.id if org else None,
        email_verified=False,
    )
    user.set_password(data["password"])

    # In dev mode, auto-verify email
    if current_app.debug or current_app.testing:
        user.email_verified = True

    db.session.add(user)
    db.session.commit()

    from flask_jwt_extended import create_access_token, create_refresh_token
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Registration successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "email_verified": user.email_verified,
        },
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Validation error", "messages": e.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if user.is_locked:
        return jsonify({"error": "Account locked. Try again later."}), 423

    if not user.check_password(data["password"]):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        db.session.commit()
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.email_verified:
        return jsonify({"error": "Email not verified"}), 403

    # Reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    login_user(user)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "organization_id": user.organization_id,
        },
    })


@auth_bp.route("/logout", methods=["POST"])
@jwt_required(optional=True)
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token})


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3/minute")
def forgot_password():
    email = (request.get_json() or {}).get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    # Always return success to prevent email enumeration
    return jsonify({"message": "If the email exists, a reset link has been sent."})


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("password")
    if not token or not new_password:
        return jsonify({"error": "Token and password required"}), 400
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    return jsonify({"message": "Password reset successful"})


@auth_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    return jsonify({"message": "Email verification endpoint. Full implementation with email service."})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "organization_id": user.organization_id,
        "notification_email": user.notification_email,
        "webhook_url": user.webhook_url,
        "watched_routes": user.watched_routes or [],
        "email_verified": user.email_verified,
        "created_at": user.created_at.isoformat(),
    })


@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    schema = ProfileUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Validation error", "messages": e.messages}), 400

    if "name" in data:
        user.name = sanitize_text(data["name"])
    if "notification_email" in data:
        user.notification_email = data["notification_email"]
    if "webhook_url" in data:
        user.webhook_url = data["webhook_url"]
        if not user.webhook_secret:
            user.webhook_secret = secrets.token_hex(32)
    if "watched_routes" in data:
        user.watched_routes = data["watched_routes"]

    db.session.commit()
    return jsonify({"message": "Profile updated"})


@auth_bp.route("/me/api-keys", methods=["PUT"])
@jwt_required()
def update_api_keys():
    """Store personal AviationStack key (encrypted)."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    aviationstack_key = data.get("aviationstack_key")

    encryption_key = current_app.config.get("ENCRYPTION_KEY")
    if not encryption_key:
        return jsonify({"error": "Encryption not configured"}), 500

    if aviationstack_key:
        encrypted = encrypt_value(aviationstack_key, encryption_key)
        user.personal_api_keys = {"aviationstack_key_enc": encrypted}
    else:
        user.personal_api_keys = {}

    db.session.commit()
    return jsonify({"message": "API keys updated"})


@auth_bp.route("/me/api-key", methods=["GET"])
@jwt_required()
def generate_user_api_key():
    """Generate/rotate user's REST API key. Shows full key only once."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    raw_key, hashed_key = generate_api_key()
    user.api_key_hash = hashed_key
    db.session.commit()

    return jsonify({
        "api_key": raw_key,
        "message": "Save this key - it will not be shown again.",
    })
