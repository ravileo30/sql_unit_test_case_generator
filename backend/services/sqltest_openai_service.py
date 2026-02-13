import json
import os
from typing import Any, Dict, List

from openai import OpenAI


class SqlTestOpenAIService:
    def __init__(self) -> None:
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = OpenAI(api_key=self._api_key) if self._api_key else None

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "name": "sql_unit_tests",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "tests": {
                        "type": "array",
                        "minItems": 6,
                        "maxItems": 12,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "params": {"type": "object", "additionalProperties": True},
                                "setup_sql": {"type": "string"},
                                "act_sql": {"type": "string"},
                                "actual_schema_sql": {"type": "string"},
                                "expected_schema_sql": {"type": "string"},
                                "openjson_with_clause": {"type": "string"},
                                "assertion_type": {
                                    "type": "string",
                                    "enum": ["EXCEPT_FULL_COMPARE", "ROWCOUNT", "CHECKSUM", "ERROR_EXPECTED"],
                                },
                                "assert_sql": {"type": "string"},
                            },
                            "required": [
                                "name",
                                "description",
                                "params",
                                "setup_sql",
                                "act_sql",
                                "actual_schema_sql",
                                "openjson_with_clause",
                                "assertion_type",
                            ],
                        },
                    }
                },
                "required": ["tests"],
            },
        }

    def build_prompt(self, proc_full_name: str, definition_sql: str, parameters: List[Dict[str, Any]], notes: str) -> str:
        return (
            "You generate SQL Server unit tests for stored procedures. Return STRICT JSON only, no markdown. "
            "Generate 6-12 tests covering nulls, boundaries, empty input, invalid input, and typical paths. "
            "Use minimal setup inserts and never TRUNCATE/DELETE entire production tables. "
            "MVP supports resultset procedures: provide actual_schema_sql for #Actual and openjson_with_clause for loading baseline. "
            "If result has volatile columns prefer ROWCOUNT or CHECKSUM assertion_type. "
            "act_sql must be a SELECT/EXEC fragment intended after `INSERT INTO #Actual`.\n\n"
            f"Procedure: {proc_full_name}\n"
            f"Parameters: {json.dumps(parameters)}\n"
            f"Procedure SQL:\n{definition_sql}\n\n"
            f"Notes from user: {notes or 'None'}"
        )

    def generate_tests(self, proc_full_name: str, definition_sql: str, parameters: List[Dict[str, Any]], notes: str = "") -> List[Dict[str, Any]]:
        if not self._client:
            return self._fallback(proc_full_name)

        response = self._client.responses.create(
            model=self._model,
            input=[{"role": "user", "content": self.build_prompt(proc_full_name, definition_sql, parameters, notes)}],
            text={
                "format": {
                    "type": "json_schema",
                    "name": self.schema["name"],
                    "strict": True,
                    "schema": self.schema["schema"],
                }
            },
        )
        payload = json.loads(response.output_text)
        return payload["tests"]

    def _fallback(self, proc_full_name: str) -> List[Dict[str, Any]]:
        return [
            {
                "name": f"{proc_full_name} typical rows",
                "description": "Valid input returns expected rows.",
                "params": {"CustomerId": 1},
                "setup_sql": "INSERT INTO #Input(CustomerId) VALUES (1);",
                "act_sql": "EXEC " + proc_full_name + " @CustomerId = 1",
                "actual_schema_sql": "CREATE TABLE #Actual(CustomerId INT, TotalAmount DECIMAL(18,2));",
                "expected_schema_sql": "CREATE TABLE #Expected(CustomerId INT, TotalAmount DECIMAL(18,2));",
                "openjson_with_clause": "CustomerId INT '$.CustomerId', TotalAmount DECIMAL(18,2) '$.TotalAmount'",
                "assertion_type": "EXCEPT_FULL_COMPARE",
                "assert_sql": "",
            }
        ] * 6
