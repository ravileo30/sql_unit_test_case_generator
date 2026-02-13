import type { TestStatus, TransformationTest } from '../types'

interface TransformationTestCardProps {
  test: TransformationTest
  onChangeStatus: (id: string, status: TestStatus) => void
}

export function TransformationTestCard({ test, onChangeStatus }: TransformationTestCardProps) {
  return (
    <div style={{ border: '1px solid #d9d9d9', borderRadius: 8, padding: 16, marginBottom: 12 }}>
      <h3 style={{ marginTop: 0 }}>
        [{test.type.toUpperCase()}] {test.description}
      </h3>
      <p>
        <strong>Transformation SQL:</strong>
      </p>
      <pre style={{ background: '#f7f7f7', padding: 8, overflowX: 'auto' }}>{test.transformation_sql}</pre>

      <p>
        <strong>Dummy Input Data:</strong>
      </p>
      <pre style={{ background: '#f7f7f7', padding: 8, overflowX: 'auto' }}>
        {JSON.stringify(test.dummy_input_data, null, 2)}
      </pre>

      <p>
        <strong>Expected Output:</strong>
      </p>
      <pre style={{ background: '#f7f7f7', padding: 8, overflowX: 'auto' }}>
        {JSON.stringify(test.expected_output_data, null, 2)}
      </pre>

      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <strong>Status:</strong> {test.status}
        <button onClick={() => onChangeStatus(test.id, 'passed')}>Pass</button>
        <button onClick={() => onChangeStatus(test.id, 'failed')}>Fail</button>
        <button onClick={() => onChangeStatus(test.id, 'pending')}>Reset</button>
      </div>
    </div>
  )
}
