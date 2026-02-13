# SQL Unit Test Case Generator

This scaffold matches your requested architecture:

- **Backend:** Python + Flask with `routes` and `controllers`
- **Frontend:** TypeScript + React with `pages` and `components`
- **LLM:** OpenAI API for SQL transformation-level test generation

## Workflow supported

1. Read a procedure from DB metadata (`ProcedureRepository` adapter).
2. Send SQL procedure text to OpenAI and generate tests for each transformation (`CTE`, `JOIN`, `UNION`, `FILTER`, `AGGREGATION`).
3. Return each test with:
   - transformation SQL
   - dummy input rows
   - expected output rows
4. Show a **Test Review Dashboard** where users can mark test results as `passed` or `failed`.

## Project structure

```text
backend/
  app.py
  controllers/
  routes/
  repositories/
  services/
  models/
frontend/
  src/
    components/
    pages/
    services/
```

## Run backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Optional env vars:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default: `gpt-4o-mini`)

If API key is missing, a fallback deterministic test set is returned.

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

## Suggested DB integration points

- Replace `ProcedureRepository.get_procedure_sql` with a query against your procedure catalog.
- Persist pass/fail status in `update_test_status` (currently stubbed).
- Add a run-execution endpoint to execute generated transformation SQL in an isolated test DB/schema.
