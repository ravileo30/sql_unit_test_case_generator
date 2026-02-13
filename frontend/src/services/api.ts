import { baseUrl } from '../config/http'
import type { IProcedure, ITestCase, ITestRun } from '../types'

export async function getSqlProcedures(): Promise<IProcedure[]> {
  const response = await fetch(`${baseUrl}/api/sqltests/procedures`)
  if (!response.ok) throw new Error('Failed to load procedures')
  const data = await response.json()
  return data.procedures
}

export async function generateSqlTests(payload: {
  proc_full_name: string
  number_of_tests: number
  notes?: string
}): Promise<ITestCase[]> {
  const response = await fetch(`${baseUrl}/api/sqltests/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error('Failed to generate test cases')
  const data = await response.json()
  return data.tests
}

export async function getSqlTests(procFullName: string): Promise<ITestCase[]> {
  const response = await fetch(`${baseUrl}/api/sqltests?proc_full_name=${encodeURIComponent(procFullName)}`)
  if (!response.ok) throw new Error('Failed to load test cases')
  const data = await response.json()
  return data.tests
}

export async function updateSqlTest(testCaseId: number, payload: Partial<ITestCase>): Promise<ITestCase> {
  const response = await fetch(`${baseUrl}/api/sqltests/${testCaseId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error('Failed to update test case')
  return response.json()
}

export async function runSqlTests(testCaseIds: number[]): Promise<ITestRun[]> {
  const response = await fetch(`${baseUrl}/api/sqltests/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ test_case_ids: testCaseIds }),
  })
  if (!response.ok) throw new Error('Failed to run tests')
  const data = await response.json()
  return data.runs
}

export async function acceptBaseline(testCaseId: number, runId: number): Promise<void> {
  const response = await fetch(`${baseUrl}/api/sqltests/${testCaseId}/accept-baseline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ run_id: runId }),
  })
  if (!response.ok) throw new Error('Failed to accept baseline')
}

export async function getSqlRuns(testCaseId: number): Promise<ITestRun[]> {
  const response = await fetch(`${baseUrl}/api/sqltests/runs?test_case_id=${testCaseId}`)
  if (!response.ok) throw new Error('Failed to load runs')
  const data = await response.json()
  return data.runs
}
