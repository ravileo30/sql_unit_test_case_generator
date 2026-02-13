from flask import jsonify, request

from services.sqltest_service import SqlTestService


class SqlTestController:
    def __init__(self) -> None:
        self.service = SqlTestService()

    def list_procedures(self):
        try:
            return jsonify({"procedures": self.service.list_procedures()}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    def generate(self):
        payload = request.get_json(silent=True) or {}
        proc_full_name = payload.get("proc_full_name")
        if not proc_full_name:
            return jsonify({"error": "proc_full_name is required"}), 400

        try:
            tests = self.service.generate_tests(
                proc_full_name=proc_full_name,
                number_of_tests=int(payload.get("number_of_tests", 8)),
                notes=payload.get("notes", ""),
            )
            return jsonify({"tests": tests}), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 404
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    def list_tests(self):
        proc_full_name = request.args.get("proc_full_name", "")
        if not proc_full_name:
            return jsonify({"error": "proc_full_name is required"}), 400
        try:
            return jsonify({"tests": self.service.get_tests(proc_full_name)}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    def update_test(self, test_case_id: int):
        payload = request.get_json(silent=True) or {}
        try:
            test_case = self.service.update_test(test_case_id, payload)
            return jsonify(test_case), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    def run_tests(self):
        payload = request.get_json(silent=True) or {}
        ids = payload.get("test_case_ids", [])
        if not ids:
            return jsonify({"error": "test_case_ids are required"}), 400
        try:
            runs = self.service.run_tests([int(x) for x in ids])
            return jsonify({"runs": runs}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    def accept_baseline(self, test_case_id: int):
        payload = request.get_json(silent=True) or {}
        run_id = payload.get("run_id")
        if not run_id:
            return jsonify({"error": "run_id is required"}), 400
        try:
            self.service.accept_baseline(test_case_id, int(run_id))
            return jsonify({"message": "baseline accepted"}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    def list_runs(self):
        test_case_id = request.args.get("test_case_id")
        if not test_case_id:
            return jsonify({"error": "test_case_id is required"}), 400
        try:
            return jsonify({"runs": self.service.get_runs(int(test_case_id))}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500
