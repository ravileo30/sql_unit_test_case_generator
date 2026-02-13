import json
import os
from typing import Any, Dict, List

from openai import OpenAI


class OpenAIService:
    def __init__(self) -> None:
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = OpenAI(api_key=self._api_key) if self._api_key else None

    def generate_transformation_tests(self, procedure_name: str, procedure_sql: str) -> List[Dict[str, Any]]:
        if not self._client:
            return self._fallback_tests()

        prompt = (
            "You are a SQL unit test generator. Return JSON array only. "
            "For each transformation step (cte, join, union, aggregation, filter), create a test object with keys: "
            "id,type,description,transformation_sql,dummy_input_data,expected_output_data,status. "
            "Use small but realistic dummy rows. status should be pending.\n\n"
            f"Procedure name: {procedure_name}\n"
            f"Procedure SQL:\n{procedure_sql}"
        )

        response = self._client.responses.create(
            model=self._model,
            input=prompt,
            temperature=0.2,
        )

        text = response.output_text.strip()
        return json.loads(text)

    def _fallback_tests(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "cte-1",
                "type": "cte",
                "description": "Validate date filtering in base_orders CTE.",
                "transformation_sql": "SELECT * FROM orders WHERE order_date >= '2024-01-01'",
                "dummy_input_data": [
                    {"table": "orders", "rows": [{"customer_id": 1, "order_id": 10, "amount": 50, "order_date": "2024-02-10"}, {"customer_id": 2, "order_id": 11, "amount": 40, "order_date": "2023-12-15"}]}
                ],
                "expected_output_data": [{"customer_id": 1, "order_id": 10, "amount": 50, "order_date": "2024-02-10"}],
                "status": "pending",
            },
            {
                "id": "join-1",
                "type": "join",
                "description": "Validate customer-region enrichment join.",
                "transformation_sql": "SELECT b.customer_id, b.order_id, b.amount, c.region FROM base_orders b JOIN customers c ON b.customer_id = c.customer_id",
                "dummy_input_data": [
                    {"table": "base_orders", "rows": [{"customer_id": 1, "order_id": 10, "amount": 50}]},
                    {"table": "customers", "rows": [{"customer_id": 1, "region": "NA"}]}
                ],
                "expected_output_data": [{"customer_id": 1, "order_id": 10, "amount": 50, "region": "NA"}],
                "status": "pending",
            },
        ]
