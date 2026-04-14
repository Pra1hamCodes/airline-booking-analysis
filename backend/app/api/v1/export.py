import io
import base64
from flask import send_file, request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.services.report_generator import ReportGenerator
from app.utils.validators import ExportPDFSchema

ns = Namespace("export", description="Data export operations")


@ns.route("/csv")
class CSVExport(Resource):
    @jwt_required()
    def get(self):
        data = ReportGenerator().generate_csv()
        return send_file(io.BytesIO(data), mimetype="text/csv", as_attachment=True, download_name="flight_data.csv")


@ns.route("/excel")
class ExcelExport(Resource):
    @jwt_required()
    def get(self):
        data = ReportGenerator().generate_excel()
        return send_file(
            io.BytesIO(data),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="airline_report.xlsx",
        )


@ns.route("/pdf-report")
class PDFExportCreate(Resource):
    @jwt_required()
    def post(self):
        """Async PDF generation. Returns task_id."""
        try:
            data = ExportPDFSchema().load(request.get_json() or {})
        except ValidationError as e:
            return {"error": "Validation error", "messages": e.messages}, 400

        try:
            from celery_worker import generate_pdf_report_task
            task = generate_pdf_report_task.delay(
                date_from=data["date_from"].isoformat(),
                date_to=data["date_to"].isoformat(),
                routes=data.get("routes", []),
                include_forecast=data.get("include_forecast", False),
            )
            return {"task_id": task.id, "status": "pending"}, 202
        except Exception:
            # Celery not available, run synchronously
            pdf_bytes = ReportGenerator().generate_pdf_report(
                data["date_from"], data["date_to"],
                data.get("routes", []),
                data.get("include_forecast", False),
            )
            return {
                "task_id": "sync",
                "status": "completed",
                "pdf_base64": base64.b64encode(pdf_bytes).decode(),
            }


@ns.route("/pdf-report/<string:task_id>")
class PDFExportStatus(Resource):
    @jwt_required()
    def get(self, task_id):
        """Poll for PDF status."""
        try:
            from celery_worker import celery
            result = celery.AsyncResult(task_id)
            if result.ready():
                return {"status": "completed", "pdf_base64": result.result}
            return {"status": "pending"}
        except Exception:
            return {"status": "unknown"}
