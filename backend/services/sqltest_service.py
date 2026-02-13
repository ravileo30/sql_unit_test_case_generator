import time
from typing import Any, Dict, List

from repositories.sqltest_repository import SqlTestRepository
from services.sqltest_openai_service import SqlTestOpenAIService


class SqlTestService:
    def __init__(self) -> None:
        self.repo = SqlTestRepository()
        self.ai = SqlTestOpenAIService()

    def list_procedures(self) -> List[Dict[str, Any]]:
        return self.repo.list_procedures()

    def generate_tests(self, proc_full_name: str, number_of_tests: int = 8, notes: str = "") -> List[Dict[str, Any]]:
        metadata = self.repo.get_procedure_metadata(proc_full_name)
        generated = self.ai.generate_tests(
            proc_full_name=proc_full_name,
            definition_sql=metadata["definition_sql"],
            parameters=metadata["parameters"],
            notes=notes,
        )
        trimmed = generated[: max(1, number_of_tests)]
        return self.repo.insert_test_cases(proc_full_name, trimmed)

    def get_tests(self, proc_full_name: str) -> List[Dict[str, Any]]:
        return self.repo.list_test_cases(proc_full_name)

    def update_test(self, test_case_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.repo.update_test_case(test_case_id, payload)

    def run_tests(self, test_case_ids: List[int]) -> List[Dict[str, Any]]:
        cases = self.repo.get_test_cases_by_ids(test_case_ids)
        runs: List[Dict[str, Any]] = []
        for case in cases:
            started = time.time()
            baseline_json = self.repo.get_baseline_json(case["id"])
            harness_result = self.repo.execute_harness(case, baseline_json)
            duration_ms = int((time.time() - started) * 1000)

            status = "pass" if harness_result["status"] in {"pass", "needs_baseline"} else "fail"
            run = self.repo.save_test_run(
                {
                    "test_case_id": case["id"],
                    "status": status,
                    "duration_ms": duration_ms,
                    "diff_preview": harness_result.get("diff_preview", []),
                    "log_text": harness_result.get("log_text", ""),
                    "actual_output": harness_result.get("actual_output", []),
                }
            )
            self.repo.finalize_test_case_status(case["id"], status if harness_result["status"] != "needs_baseline" else "not_run", duration_ms)
            if harness_result["status"] == "needs_baseline":
                run["status"] = "pass"
                run["log_text"] = (run.get("log_text") or "") + "\nBaseline required."
            runs.append(run)
        return runs

    def accept_baseline(self, test_case_id: int, run_id: int) -> None:
        self.repo.accept_baseline(test_case_id, run_id)

    def get_runs(self, test_case_id: int) -> List[Dict[str, Any]]:
        return self.repo.list_runs(test_case_id)
