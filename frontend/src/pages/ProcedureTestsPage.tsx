import { useEffect, useMemo, useState } from 'react'

import { ProcedureSelector } from '../components/ProcedureSelector'
import { TransformationTestCard } from '../components/TransformationTestCard'
import { generateTestPlan, getProcedures, updateTestStatus } from '../services/api'
import type { ProcedurePlan, TestStatus } from '../types'

export function ProcedureTestsPage() {
  const [procedures, setProcedures] = useState<string[]>([])
  const [selectedProcedure, setSelectedProcedure] = useState('')
  const [plan, setPlan] = useState<ProcedurePlan | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getProcedures().then(setProcedures).catch(() => setError('Could not load procedures.'))
  }, [])

  const summary = useMemo(() => {
    if (!plan) return { total: 0, passed: 0, failed: 0, pending: 0 }
    const passed = plan.tests.filter((t) => t.status === 'passed').length
    const failed = plan.tests.filter((t) => t.status === 'failed').length
    const pending = plan.tests.filter((t) => t.status === 'pending').length
    return { total: plan.tests.length, passed, failed, pending }
  }, [plan])

  async function handleGenerate() {
    setError('')
    setIsLoading(true)
    try {
      const nextPlan = await generateTestPlan(selectedProcedure)
      setPlan(nextPlan)
    } catch {
      setError('Failed to generate tests.')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleStatusChange(testId: string, status: TestStatus) {
    if (!plan) return
    await updateTestStatus(testId, status)
    setPlan({
      ...plan,
      tests: plan.tests.map((test) => (test.id === testId ? { ...test, status } : test)),
    })
  }

  return (
    <main style={{ margin: '0 auto', maxWidth: 960, padding: 24, fontFamily: 'Arial, sans-serif' }}>
      <h1>SQL Procedure Unit Test Generator</h1>
      <p>
        Generate transformation-level test cases (JOIN/CTE/UNION/FILTER/AGGREGATION) with dummy data and mark each
        one as pass/fail.
      </p>

      <ProcedureSelector
        procedures={procedures}
        selected={selectedProcedure}
        onSelect={setSelectedProcedure}
        onGenerate={handleGenerate}
        isLoading={isLoading}
      />

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {plan && (
        <section style={{ marginBottom: 24 }}>
          <h2>Test Review Dashboard</h2>
          <p>
            <strong>Procedure:</strong> {plan.procedure_name}
          </p>
          <pre style={{ background: '#f7f7f7', padding: 8, overflowX: 'auto' }}>{plan.procedure_sql}</pre>
          <div style={{ display: 'flex', gap: 16 }}>
            <span>Total: {summary.total}</span>
            <span>Passed: {summary.passed}</span>
            <span>Failed: {summary.failed}</span>
            <span>Pending: {summary.pending}</span>
          </div>
        </section>
      )}

      <section>
        {plan?.tests.map((test) => (
          <TransformationTestCard key={test.id} test={test} onChangeStatus={handleStatusChange} />
        ))}
      </section>
    </main>
  )
}
