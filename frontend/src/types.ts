export type TestStatus = 'pending' | 'passed' | 'failed'

export interface TransformationTest {
  id: string
  type: string
  description: string
  transformation_sql: string
  dummy_input_data: Array<Record<string, unknown>>
  expected_output_data: Array<Record<string, unknown>>
  status: TestStatus
}

export interface ProcedurePlan {
  procedure_name: string
  procedure_sql: string
  tests: TransformationTest[]
}
