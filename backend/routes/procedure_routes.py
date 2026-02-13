from flask import Blueprint

from controllers.procedure_controller import ProcedureController


procedure_bp = Blueprint("procedure_bp", __name__, url_prefix="/api/procedures")
controller = ProcedureController()

procedure_bp.get("/")(controller.list_procedures)
procedure_bp.post("/generate-tests")(controller.generate_tests)
procedure_bp.patch("/test-status")(controller.update_test_status)
