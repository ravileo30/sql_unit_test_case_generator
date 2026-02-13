import json
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import pyodbc


class SqlTestRepository:
    def __init__(self) -> None:
        self.connection_string = os.getenv("SQLSERVER_CONNECTION_STRING", "")

    @contextmanager
    def _connect(self):
        if not self.connection_string:
            raise RuntimeError("SQLSERVER_CONNECTION_STRING is not configured")
        conn = pyodbc.connect(self.connection_string)
        try:
            yield conn
        finally:
            conn.close()

    def list_procedures(self) -> List[Dict[str, Any]]:
        query = """
        SELECT s.name AS [schema],
               p.name AS [name],
               CONCAT(s.name, '.', p.name) AS full_name
        FROM sys.procedures p
        JOIN sys.schemas s ON p.schema_id = s.schema_id
        ORDER BY s.name, p.name;
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(query).fetchall()
            return [
                {
                    "schema": row.schema,
                    "name": row.name,
                    "full_name": row.full_name,
                }
                for row in rows
            ]

    def get_procedure_metadata(self, proc_full_name: str) -> Dict[str, Any]:
        query = """
        DECLARE @proc_full_name NVARCHAR(256) = ?;

        SELECT OBJECT_DEFINITION(OBJECT_ID(@proc_full_name)) AS definition_sql;

        SELECT p.name AS param_name,
               TYPE_NAME(p.user_type_id) AS sql_type,
               p.max_length,
               p.precision,
               p.scale,
               p.is_output
        FROM sys.parameters p
        WHERE p.object_id = OBJECT_ID(@proc_full_name)
        ORDER BY p.parameter_id;
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, proc_full_name)
            definition_row = cursor.fetchone()
            definition_sql = definition_row.definition_sql if definition_row else None
            cursor.nextset()
            param_rows = cursor.fetchall()

            if not definition_sql:
                raise ValueError(f"Procedure '{proc_full_name}' not found")

            return {
                "definition_sql": definition_sql,
                "parameters": [
                    {
                        "name": row.param_name,
                        "type": row.sql_type,
                        "max_length": row.max_length,
                        "precision": row.precision,
                        "scale": row.scale,
                        "is_output": bool(row.is_output),
                    }
                    for row in param_rows
                ],
            }

    def insert_test_cases(self, proc_full_name: str, tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sql = """
        INSERT INTO sql_test_cases (
            proc_full_name, name, description, params_json, setup_sql, act_sql, assertion_type,
            assert_sql, actual_schema_sql, expected_schema_sql, openjson_with_clause, status
        )
        OUTPUT INSERTED.id, INSERTED.proc_full_name, INSERTED.name, INSERTED.description,
               INSERTED.params_json, INSERTED.setup_sql, INSERTED.act_sql, INSERTED.assert_sql,
               INSERTED.assertion_type, INSERTED.status, INSERTED.last_run_at, INSERTED.last_duration_ms,
               INSERTED.actual_schema_sql, INSERTED.expected_schema_sql, INSERTED.openjson_with_clause
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft');
        """
        saved: List[Dict[str, Any]] = []
        with self._connect() as conn:
            cursor = conn.cursor()
            for test in tests:
                row = cursor.execute(
                    sql,
                    proc_full_name,
                    test.get("name"),
                    test.get("description"),
                    json.dumps(test.get("params", {})),
                    test.get("setup_sql", ""),
                    test.get("act_sql", ""),
                    test.get("assertion_type", "EXCEPT_FULL_COMPARE"),
                    test.get("assert_sql", ""),
                    test.get("actual_schema_sql", ""),
                    test.get("expected_schema_sql", ""),
                    test.get("openjson_with_clause", ""),
                ).fetchone()
                saved.append(self._serialize_test_case(row))
            conn.commit()
        return saved

    def list_test_cases(self, proc_full_name: str) -> List[Dict[str, Any]]:
        query = """
        SELECT id, proc_full_name, name, description, params_json, setup_sql, act_sql, assert_sql,
               assertion_type, status, last_run_at, last_duration_ms, actual_schema_sql,
               expected_schema_sql, openjson_with_clause
        FROM sql_test_cases
        WHERE proc_full_name = ?
        ORDER BY created_at DESC;
        """
        with self._connect() as conn:
            rows = conn.cursor().execute(query, proc_full_name).fetchall()
            return [self._serialize_test_case(row) for row in rows]

    def update_test_case(self, test_case_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = """
        UPDATE sql_test_cases
        SET name = ?,
            description = ?,
            params_json = ?,
            setup_sql = ?,
            act_sql = ?,
            assert_sql = ?,
            assertion_type = ?,
            actual_schema_sql = ?,
            expected_schema_sql = ?,
            openjson_with_clause = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;

        SELECT id, proc_full_name, name, description, params_json, setup_sql, act_sql, assert_sql,
               assertion_type, status, last_run_at, last_duration_ms, actual_schema_sql,
               expected_schema_sql, openjson_with_clause
        FROM sql_test_cases
        WHERE id = ?;
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                payload.get("name"),
                payload.get("description"),
                payload.get("params_json", "{}"),
                payload.get("setup_sql", ""),
                payload.get("act_sql", ""),
                payload.get("assert_sql", ""),
                payload.get("assertion_type", "EXCEPT_FULL_COMPARE"),
                payload.get("actual_schema_sql", ""),
                payload.get("expected_schema_sql", ""),
                payload.get("openjson_with_clause", ""),
                test_case_id,
                test_case_id,
            )
            cursor.nextset()
            row = cursor.fetchone()
            conn.commit()
            return self._serialize_test_case(row)

    def get_test_cases_by_ids(self, ids: List[int]) -> List[Dict[str, Any]]:
        placeholders = ",".join(["?"] * len(ids))
        query = f"""
        SELECT id, proc_full_name, name, description, params_json, setup_sql, act_sql, assert_sql,
               assertion_type, status, last_run_at, last_duration_ms, actual_schema_sql,
               expected_schema_sql, openjson_with_clause
        FROM sql_test_cases
        WHERE id IN ({placeholders});
        """
        with self._connect() as conn:
            rows = conn.cursor().execute(query, *ids).fetchall()
            return [self._serialize_test_case(row) for row in rows]

    def save_test_run(self, run: Dict[str, Any]) -> Dict[str, Any]:
        query = """
        INSERT INTO sql_test_runs (test_case_id, status, duration_ms, diff_preview_json, log_text, actual_output_json)
        OUTPUT INSERTED.id, INSERTED.test_case_id, INSERTED.status, INSERTED.duration_ms,
               INSERTED.diff_preview_json, INSERTED.log_text, INSERTED.created_at
        VALUES (?, ?, ?, ?, ?, ?);
        """
        with self._connect() as conn:
            row = conn.cursor().execute(
                query,
                run["test_case_id"],
                run["status"],
                run["duration_ms"],
                json.dumps(run.get("diff_preview", [])),
                run.get("log_text", ""),
                json.dumps(run.get("actual_output", [])),
            ).fetchone()
            conn.commit()
            return {
                "id": row.id,
                "test_case_id": row.test_case_id,
                "status": row.status,
                "duration_ms": row.duration_ms,
                "diff_preview": json.loads(row.diff_preview_json) if row.diff_preview_json else [],
                "log_text": row.log_text,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }

    def finalize_test_case_status(self, test_case_id: int, status: str, duration_ms: int) -> None:
        query = """
        UPDATE sql_test_cases
        SET status = ?,
            last_run_at = SYSUTCDATETIME(),
            last_duration_ms = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
        """
        with self._connect() as conn:
            conn.cursor().execute(query, status, duration_ms, test_case_id)
            conn.commit()

    def list_runs(self, test_case_id: int) -> List[Dict[str, Any]]:
        query = """
        SELECT id, test_case_id, status, duration_ms, diff_preview_json, log_text, created_at
        FROM sql_test_runs
        WHERE test_case_id = ?
        ORDER BY created_at DESC;
        """
        with self._connect() as conn:
            rows = conn.cursor().execute(query, test_case_id).fetchall()
            return [
                {
                    "id": row.id,
                    "test_case_id": row.test_case_id,
                    "status": row.status,
                    "duration_ms": row.duration_ms,
                    "diff_preview": json.loads(row.diff_preview_json) if row.diff_preview_json else [],
                    "log_text": row.log_text,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ]

    def accept_baseline(self, test_case_id: int, run_id: int) -> None:
        query = """
        DECLARE @actual_output NVARCHAR(MAX);
        SELECT @actual_output = actual_output_json
        FROM sql_test_runs
        WHERE id = ? AND test_case_id = ?;

        IF @actual_output IS NULL
            THROW 50000, 'Run does not include actual output', 1;

        MERGE sql_test_baselines AS target
        USING (SELECT ? AS test_case_id, @actual_output AS baseline_json) AS source
        ON target.test_case_id = source.test_case_id
        WHEN MATCHED THEN
            UPDATE SET baseline_json = source.baseline_json, updated_at = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
            INSERT (test_case_id, baseline_json)
            VALUES (source.test_case_id, source.baseline_json);

        UPDATE sql_test_cases
        SET baseline_exists = 1,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
        """
        with self._connect() as conn:
            conn.cursor().execute(query, run_id, test_case_id, test_case_id, test_case_id)
            conn.commit()

    def get_baseline_json(self, test_case_id: int) -> Optional[str]:
        query = "SELECT baseline_json FROM sql_test_baselines WHERE test_case_id = ?;"
        with self._connect() as conn:
            row = conn.cursor().execute(query, test_case_id).fetchone()
            return row.baseline_json if row else None

    def execute_harness(self, test_case: Dict[str, Any], baseline_json: Optional[str]) -> Dict[str, Any]:
        sql = f"""
        SET NOCOUNT ON;
        DECLARE @baseline_json NVARCHAR(MAX) = ?;

        BEGIN TRY
            BEGIN TRAN;

            {test_case.get('setup_sql') or ''}

            {test_case.get('actual_schema_sql') or ''}
            INSERT INTO #Actual
            {test_case.get('act_sql') or ''};

            IF OBJECT_ID('tempdb..#Expected') IS NOT NULL DROP TABLE #Expected;
            {test_case.get('expected_schema_sql') or test_case.get('actual_schema_sql') or ''}

            IF @baseline_json IS NOT NULL AND LEN(@baseline_json) > 0 AND '{test_case.get('openjson_with_clause') or ''}' <> ''
            BEGIN
                INSERT INTO #Expected
                SELECT * FROM OPENJSON(@baseline_json)
                WITH ({test_case.get('openjson_with_clause') or ''});
            END

            IF @baseline_json IS NULL OR LEN(@baseline_json) = 0
            BEGIN
                SELECT 'needs_baseline' AS harness_status,
                       (SELECT * FROM #Actual FOR JSON PATH, INCLUDE_NULL_VALUES) AS actual_output_json,
                       NULL AS diff_preview_json,
                       'No baseline found. Accept baseline to lock expected output.' AS log_text;
                ROLLBACK;
                RETURN;
            END

            SELECT * INTO #OnlyExpected FROM (
                SELECT * FROM #Expected
                EXCEPT
                SELECT * FROM #Actual
            ) x;

            SELECT * INTO #OnlyActual FROM (
                SELECT * FROM #Actual
                EXCEPT
                SELECT * FROM #Expected
            ) y;

            IF EXISTS (SELECT 1 FROM #OnlyExpected) OR EXISTS (SELECT 1 FROM #OnlyActual)
            BEGIN
                SELECT 'fail' AS harness_status,
                       (SELECT TOP 200 * FROM #OnlyExpected FOR JSON PATH, INCLUDE_NULL_VALUES) AS diff_preview_json,
                       (SELECT * FROM #Actual FOR JSON PATH, INCLUDE_NULL_VALUES) AS actual_output_json,
                       'EXCEPT comparison failed' AS log_text;
                ROLLBACK;
                RETURN;
            END

            SELECT 'pass' AS harness_status,
                   '[]' AS diff_preview_json,
                   (SELECT * FROM #Actual FOR JSON PATH, INCLUDE_NULL_VALUES) AS actual_output_json,
                   'Assertion succeeded' AS log_text;
            ROLLBACK;
        END TRY
        BEGIN CATCH
            IF @@TRANCOUNT > 0 ROLLBACK;
            SELECT 'fail' AS harness_status,
                   '[]' AS diff_preview_json,
                   '[]' AS actual_output_json,
                   ERROR_MESSAGE() AS log_text;
        END CATCH;
        """
        with self._connect() as conn:
            row = conn.cursor().execute(sql, baseline_json).fetchone()
            return {
                "status": row.harness_status,
                "diff_preview": json.loads(row.diff_preview_json) if row.diff_preview_json else [],
                "actual_output": json.loads(row.actual_output_json) if row.actual_output_json else [],
                "log_text": row.log_text,
            }

    def _serialize_test_case(self, row: Any) -> Dict[str, Any]:
        if row is None:
            return {}
        return {
            "id": row.id,
            "proc_full_name": row.proc_full_name,
            "name": row.name,
            "description": row.description,
            "params_json": row.params_json or "{}",
            "setup_sql": row.setup_sql or "",
            "act_sql": row.act_sql or "",
            "assert_sql": row.assert_sql or "",
            "assertion_type": row.assertion_type,
            "status": row.status,
            "last_run_at": row.last_run_at.isoformat() if row.last_run_at else None,
            "last_duration_ms": row.last_duration_ms,
            "actual_schema_sql": getattr(row, "actual_schema_sql", "") or "",
            "expected_schema_sql": getattr(row, "expected_schema_sql", "") or "",
            "openjson_with_clause": getattr(row, "openjson_with_clause", "") or "",
        }
