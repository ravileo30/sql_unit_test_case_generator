from typing import Dict, Any

from repositories.procedure_repository import ProcedureRepository
from services.openai_service import OpenAIService


class ProcedureService:
    def __init__(self) -> None:
        self.repo = ProcedureRepository()
        self.llm = OpenAIService()

    def list_procedures(self) -> list[str]:
        return self.repo.list_procedure_names()

    def generate_test_plan(self, procedure_name: str) -> Dict[str, Any]:
        procedure_sql = self.repo.get_procedure_sql(procedure_name)
        if not procedure_sql:
            raise ValueError(f"Procedure '{procedure_name}' not found")

        tests = self.llm.generate_transformation_tests(procedure_name, procedure_sql)

        return {
            "procedure_name": procedure_name,
            "procedure_sql": procedure_sql,
            "tests": tests,
        }
