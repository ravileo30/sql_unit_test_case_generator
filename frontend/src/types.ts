export interface IProcedure {
  schema: string
  name: string
  full_name: string
  last_generated_at?: string
}

export type AssertionType = 'EXCEPT_FULL_COMPARE' | 'ROWCOUNT' | 'CHECKSUM' | 'ERROR_EXPECTED'

export interface ITestCase {
  id: number
  proc_full_name: string
  name: string
  description?: string
  params_json: string
  setup_sql: string
  act_sql: string
  assert_sql: string
  assertion_type: AssertionType
  status?: string
  last_run_at?: string
  last_duration_ms?: number
  actual_schema_sql?: string
  expected_schema_sql?: string
  openjson_with_clause?: string
}

export interface ITestRun {
  id: number
  test_case_id: number
  status: 'pass' | 'fail'
  duration_ms: number
  diff_preview?: Array<Record<string, unknown>>
  log_text?: string
  created_at: string
}
