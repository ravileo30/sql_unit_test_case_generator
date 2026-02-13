import type { ProcedurePlan, TestStatus } from '../types'

const API_BASE_URL = 'http://localhost:5000/api/procedures'

export async function getProcedures(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/`)
  if (!response.ok) {
    throw new Error('Failed to load procedures')
  }
  const data = await response.json()
  return data.procedures
}

export async function generateTestPlan(procedureName: string): Promise<ProcedurePlan> {
  const response = await fetch(`${API_BASE_URL}/generate-tests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ procedure_name: procedureName }),
  })

  if (!response.ok) {
    throw new Error('Failed to generate tests')
  }

  return response.json()
}

export async function updateTestStatus(testId: string, status: TestStatus): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/test-status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ test_id: testId, status }),
  })

  if (!response.ok) {
    throw new Error('Failed to update test status')
  }
}
