from flask import jsonify, request

from services.procedure_service import ProcedureService


class ProcedureController:
    def __init__(self) -> None:
        self.service = ProcedureService()

    def list_procedures(self):
        return jsonify({"procedures": self.service.list_procedures()}), 200

    def generate_tests(self):
        payload = request.get_json(silent=True) or {}
        procedure_name = payload.get("procedure_name")
        if not procedure_name:
            return jsonify({"error": "procedure_name is required"}), 400

        try:
            plan = self.service.generate_test_plan(procedure_name)
            return jsonify(plan), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 404

    def update_test_status(self):
        payload = request.get_json(silent=True) or {}
        test_id = payload.get("test_id")
        status = payload.get("status")

        if not test_id or status not in {"passed", "failed", "pending"}:
            return jsonify({"error": "test_id and valid status (pending/passed/failed) are required"}), 400

        # Stub persistence layer. Wire this to DB in your implementation.
        return jsonify({"test_id": test_id, "status": status, "message": "status updated"}), 200
