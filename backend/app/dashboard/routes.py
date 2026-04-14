from flask import jsonify
from . import dashboard_bp


@dashboard_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
