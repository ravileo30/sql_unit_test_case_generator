from typing import Optional, Dict


class ProcedureRepository:
    """
    Replace this adapter with your real DB integration.
    It can be wired to SQL Server/Postgres/Oracle metadata tables.
    """

    def __init__(self) -> None:
        self._mock_procedures: Dict[str, str] = {
            "sp_customer_revenue": """
                CREATE PROCEDURE sp_customer_revenue AS
                WITH base_orders AS (
                    SELECT customer_id, order_id, amount, order_date
                    FROM orders
                    WHERE order_date >= '2024-01-01'
                ),
                enriched_orders AS (
                    SELECT b.customer_id, b.order_id, b.amount, c.region
                    FROM base_orders b
                    JOIN customers c ON b.customer_id = c.customer_id
                )
                SELECT region, SUM(amount) AS total_revenue
                FROM enriched_orders
                GROUP BY region
                UNION ALL
                SELECT 'ALL' AS region, SUM(amount) AS total_revenue
                FROM enriched_orders;
            """.strip()
        }

    def get_procedure_sql(self, procedure_name: str) -> Optional[str]:
        return self._mock_procedures.get(procedure_name)

    def list_procedure_names(self) -> list[str]:
        return sorted(self._mock_procedures.keys())
