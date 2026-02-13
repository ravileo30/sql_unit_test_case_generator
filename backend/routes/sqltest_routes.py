from flask import Blueprint

from controllers.sqltest_controller import SqlTestController


sqltest_bp = Blueprint("sqltest_bp", __name__, url_prefix="/api/sqltests")
controller = SqlTestController()

sqltest_bp.get("/procedures")(controller.list_procedures)
sqltest_bp.post("/generate")(controller.generate)
sqltest_bp.get("/")(controller.list_tests)
sqltest_bp.put("/<int:test_case_id>")(controller.update_test)
sqltest_bp.post("/run")(controller.run_tests)
sqltest_bp.post("/<int:test_case_id>/accept-baseline")(controller.accept_baseline)
sqltest_bp.get("/runs")(controller.list_runs)
