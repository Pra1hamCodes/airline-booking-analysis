import structlog
from flask_mail import Message

from app.extensions import mail
from app.models.user import User
from app.services.data_processor import DataProcessor

logger = structlog.get_logger()


def send_weekly_digest():
    """Send weekly digest email to all active users with notification_email set."""
    users = User.query.filter(
        User.is_active == True,
        User.email_verified == True,
        User.notification_email.isnot(None),
    ).all()

    if not users:
        logger.info("No users to send digest to")
        return

    processor = DataProcessor()
    insights = processor.get_market_insights()

    top_routes = insights.get("popular_routes", [])[:3]

    top_routes_html = ""
    for r in top_routes:
        top_routes_html += (
            f"<li><strong>{r['route']}</strong>: "
            f"avg ${r['price']:.2f} AUD, demand {r['demand_score']:.2f}</li>\n"
        )

    html_body = f"""
    <html>
    <body style="font-family: Inter, sans-serif; color: #333;">
        <h2>Weekly Airline Market Digest</h2>
        <h3>Top Routes This Week</h3>
        <ul>{top_routes_html}</ul>
        <h3>Market Overview</h3>
        <p>Total flights analyzed: {insights.get('total_flights', 0)}</p>
        <p>Average price: ${insights.get('avg_price', 0):.2f} AUD</p>
        <hr>
        <p style="color: #999; font-size: 12px;">
            Airline Market Demand Analysis Platform
        </p>
    </body>
    </html>
    """

    sent = 0
    for user in users:
        try:
            msg = Message(
                subject="Your Weekly Airline Market Digest",
                recipients=[user.notification_email],
                html=html_body,
            )
            mail.send(msg)
            sent += 1
        except Exception as e:
            logger.error("Failed to send digest", user_id=user.id, error=str(e))

    logger.info("Weekly digest sent", total_users=len(users), sent=sent)
