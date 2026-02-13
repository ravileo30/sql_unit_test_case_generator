# SQL Unit Test Case Generator

End-to-end SQL unit testing tool for SQL Server procedures.

## What is included

- **Frontend (React + Vite):** `SqlUnitTestManager` screen with procedure listing, test generation, edit dialogs, run controls, and result/baseline actions.
- **Backend (Flask):** `/api/sqltests/*` endpoints for procedures, OpenAI generation, test CRUD, execution harness, run history, and baseline acceptance.
- **Persistence:** SQL Server migration for `sql_test_cases`, `sql_test_runs`, and `sql_test_baselines`.
- **OpenAI:** Responses API structured output schema for strict test JSON generation.

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Environment variables:

- `SQLSERVER_CONNECTION_STRING` (required for metadata queries + harness execution)
- `OPENAI_API_KEY` (optional; fallback generator used when omitted)
- `OPENAI_MODEL` (optional; default `gpt-4o-mini`)

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Optional env var:

- `VITE_API_BASE_URL` (default `http://localhost:5000`)

## Migration

Run SQL script:

- `backend/migrations/20260213_add_sql_unit_test_tables.sql`

## API summary

- `GET /api/sqltests/procedures`
- `POST /api/sqltests/generate`
- `GET /api/sqltests?proc_full_name=...`
- `PUT /api/sqltests/:id`
- `POST /api/sqltests/run`
- `POST /api/sqltests/:id/accept-baseline`
- `GET /api/sqltests/runs?test_case_id=...`

## Example generated JSON

- `backend/examples/sample_generated_test_case.json`
