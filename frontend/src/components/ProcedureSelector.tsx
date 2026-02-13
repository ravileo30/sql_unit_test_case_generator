interface ProcedureSelectorProps {
  procedures: string[]
  selected: string
  onSelect: (value: string) => void
  onGenerate: () => void
  isLoading: boolean
}

export function ProcedureSelector({ procedures, selected, onSelect, onGenerate, isLoading }: ProcedureSelectorProps) {
  return (
    <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
      <select value={selected} onChange={(e) => onSelect(e.target.value)} style={{ minWidth: 260 }}>
        <option value="">Select a procedure</option>
        {procedures.map((procedure) => (
          <option key={procedure} value={procedure}>
            {procedure}
          </option>
        ))}
      </select>
      <button onClick={onGenerate} disabled={!selected || isLoading}>
        {isLoading ? 'Generating...' : 'Generate Unit Tests'}
      </button>
    </div>
  )
}
