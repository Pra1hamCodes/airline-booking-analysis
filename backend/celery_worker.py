import os
from celery import Celery
from celery.schedules import crontab
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "default"))
celery = Celery(app.import_name, broker=app.config["CELERY_BROKER_URL"], backend=app.config["CELERY_RESULT_BACKEND"])
celery.conf.update(app.config)


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask


@celery.task
def refresh_flight_data_task():
    from app.tasks.data_refresh import refresh_flight_data
    return refresh_flight_data()


@celery.task
def check_alerts_task():
    from app.tasks.alert_checker import check_alerts
    return check_alerts()


@celery.task
def send_weekly_digest_task():
    from app.tasks.digest_sender import send_weekly_digest
    return send_weekly_digest()


@celery.task
def generate_pdf_report_task(date_from=None, date_to=None, routes=None, include_forecast=False):
    from app.services.report_generator import ReportGenerator
    import base64
    from datetime import date as date_cls
    df = date_cls.fromisoformat(date_from) if date_from else None
    dt = date_cls.fromisoformat(date_to) if date_to else None
    pdf_bytes = ReportGenerator().generate_pdf_report(df, dt, routes, include_forecast)
    return base64.b64encode(pdf_bytes).decode()


celery.conf.beat_schedule = {
    "refresh-every-6-hours": {"task": "celery_worker.refresh_flight_data_task", "schedule": crontab(minute=0, hour="*/6")},
    "weekly-digest-monday": {"task": "celery_worker.send_weekly_digest_task", "schedule": crontab(minute=0, hour=22, day_of_week=0)},
}
