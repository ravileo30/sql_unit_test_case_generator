import { useContext, useEffect, useMemo, useState } from 'react'
import {
  Box,
  Button,
  CircularProgress,
  DataGrid,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  TextField,
  Typography,
} from '@deloitte-default/gel-react'

import { snackbarMessages } from '../constants/snackbarMessages'
import { FeedbackContext, Severity } from '../context/FeedbackContext'
import {
  acceptBaseline,
  generateSqlTests,
  getSqlProcedures,
  getSqlRuns,
  getSqlTests,
  runSqlTests,
  updateSqlTest,
} from '../services/api'
import type { IProcedure, ITestCase, ITestRun } from '../types'

const defaultTestCase: ITestCase = {
  id: 0,
  proc_full_name: '',
  name: '',
  description: '',
  params_json: '{}',
  setup_sql: '',
  act_sql: '',
  assert_sql: '',
  assertion_type: 'EXCEPT_FULL_COMPARE',
  actual_schema_sql: '',
  expected_schema_sql: '',
  openjson_with_clause: '',
}

export function SqlUnitTestManager() {
  const { addMessage } = useContext(FeedbackContext)
  const [procedures, setProcedures] = useState<IProcedure[]>([])
  const [tests, setTests] = useState<ITestCase[]>([])
  const [runs, setRuns] = useState<ITestRun[]>([])
  const [selectedProc, setSelectedProc] = useState<IProcedure | null>(null)
  const [selectedTestIds, setSelectedTestIds] = useState<number[]>([])
  const [selectedTest, setSelectedTest] = useState<ITestCase>(defaultTestCase)
  const [activeRun, setActiveRun] = useState<ITestRun | null>(null)
  const [searchText, setSearchText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [isGenerateOpen, setIsGenerateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [numberOfTests, setNumberOfTests] = useState(8)
  const [notes, setNotes] = useState('')

  const filteredProcedures = useMemo(
    () => procedures.filter((proc) => `${proc.schema}.${proc.name}`.toLowerCase().includes(searchText.toLowerCase())),
    [procedures, searchText],
  )

  useEffect(() => {
    loadProcedures()
  }, [])

  async function loadProcedures() {
    setIsLoading(true)
    try {
      const nextProcedures = await getSqlProcedures()
      setProcedures(nextProcedures)
      addMessage(snackbarMessages.loadedProcedures, Severity.Success)
    } catch (error) {
      addMessage((error as Error).message, Severity.Error)
    } finally {
      setIsLoading(false)
    }
  }

  async function loadTests(procFullName: string) {
    try {
      const nextTests = await getSqlTests(procFullName)
      setTests(nextTests)
    } catch (error) {
      addMessage((error as Error).message, Severity.Error)
    }
  }

  async function handleGenerateTests() {
    if (!selectedProc) return
    setIsLoading(true)
    try {
      const generated = await generateSqlTests({
        proc_full_name: selectedProc.full_name,
        number_of_tests: numberOfTests,
        notes,
      })
      setTests(generated)
      setIsGenerateOpen(false)
      addMessage(snackbarMessages.generatedTests, Severity.Success)
    } catch (error) {
      addMessage((error as Error).message, Severity.Error)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSaveTestCase() {
    try {
      const updated = await updateSqlTest(selectedTest.id, selectedTest)
      setTests((prev) => prev.map((test) => (test.id === updated.id ? updated : test)))
      addMessage(snackbarMessages.savedTestCase, Severity.Success)
      setIsEditOpen(false)
    } catch (error) {
      addMessage((error as Error).message, Severity.Error)
    }
  }

  async function handleRun(testCaseIds: number[]) {
    if (!testCaseIds.length) return
    setIsRunning(true)
    try {
      const nextRuns = await runSqlTests(testCaseIds)
      setRuns(nextRuns)
      setActiveRun(nextRuns[0] ?? null)
      addMessage(snackbarMessages.ranTests, Severity.Success)
      if (selectedProc) {
        await loadTests(selectedProc.full_name)
      }
    } catch (error) {
      addMessage((error as Error).message, Severity.Error)
    } finally {
      setIsRunning(false)
    }
  }

  async function handleAcceptBaseline() {
    if (!activeRun) return
    try {
      await acceptBaseline(activeRun.test_case_id, activeRun.id)
      addMessage(snackbarMessages.acceptedBaseline, Severity.Success)
      if (selectedProc) {
        await loadTests(selectedProc.full_name)
      }
    } catch (error) {
      addMessage((error as Error).message, Severity.Error)
    }
  }

  async function openTestRuns(testCase: ITestCase) {
    setSelectedTest(testCase)
    setIsEditOpen(true)
    const nextRuns = await getSqlRuns(testCase.id)
    setRuns(nextRuns)
    setActiveRun(nextRuns[0] ?? null)
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4">SQL Unit Test Manager</Typography>
      <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
        <Box sx={{ width: '34%' }}>
          <Typography variant="h6">Stored Procedures</Typography>
          <TextField
            fullWidth
            value={searchText}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) => setSearchText(event.target.value)}
            placeholder="Search procedures"
            sx={{ mb: 1 }}
          />
          <DataGrid
            autoHeight
            rows={filteredProcedures}
            getRowId={(row: IProcedure) => row.full_name}
            columns={[
              { field: 'schema', headerName: 'Schema', flex: 1 },
              { field: 'name', headerName: 'Name', flex: 1 },
              {
                field: 'action',
                headerName: 'Action',
                renderCell: (params: { row: IProcedure }) => (
                  <Button
                    size="small"
                    onClick={() => {
                      setSelectedProc(params.row)
                      loadTests(params.row.full_name)
                    }}
                  >
                    Select
                  </Button>
                ),
              },
            ]}
          />
        </Box>

        <Box sx={{ width: '66%' }}>
          <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
            <Button disabled={!selectedProc || isLoading} onClick={() => setIsGenerateOpen(true)}>
              Generate Test Cases
            </Button>
            <Button disabled={isRunning || selectedTestIds.length === 0} onClick={() => handleRun(selectedTestIds)}>
              Run Selected
            </Button>
            <Button disabled={isRunning || tests.length === 0} onClick={() => handleRun(tests.map((test) => test.id))}>
              Run All
            </Button>
            <Button disabled={!selectedProc} onClick={() => selectedProc && loadTests(selectedProc.full_name)}>
              Refresh
            </Button>
            {(isLoading || isRunning) && <CircularProgress size={22} />}
          </Stack>

          <DataGrid
            autoHeight
            checkboxSelection
            rows={tests}
            getRowId={(row: ITestCase) => row.id}
            onRowSelectionModelChange={(selection: unknown) => setSelectedTestIds(selection as number[])}
            columns={[
              { field: 'name', headerName: 'Name', flex: 1 },
              { field: 'assertion_type', headerName: 'Assertion', flex: 1 },
              { field: 'status', headerName: 'Status', flex: 0.8 },
              { field: 'last_run_at', headerName: 'Last Run', flex: 1 },
              { field: 'last_duration_ms', headerName: 'Duration (ms)', flex: 0.8 },
              {
                field: 'view',
                headerName: 'View/Edit',
                renderCell: (params: { row: ITestCase }) => <Button onClick={() => openTestRuns(params.row)}>View/Edit</Button>,
              },
              {
                field: 'run',
                headerName: 'Run',
                renderCell: (params: { row: ITestCase }) => (
                  <Button disabled={isRunning} onClick={() => handleRun([params.row.id])}>
                    Run
                  </Button>
                ),
              },
            ]}
          />

          <Box sx={{ mt: 2, p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
            <Typography variant="h6">Run Results</Typography>
            {activeRun ? (
              <>
                <Typography>Status: {activeRun.status}</Typography>
                <Typography>Duration: {activeRun.duration_ms}ms</Typography>
                <Typography>Run ID: {activeRun.id}</Typography>
                <Typography sx={{ mt: 1 }}>Diff Preview</Typography>
                <pre style={{ maxHeight: 180, overflow: 'auto' }}>
                  {JSON.stringify((activeRun.diff_preview ?? []).slice(0, 200), null, 2)}
                </pre>
                <Typography>Full Log</Typography>
                <TextField fullWidth multiline minRows={4} value={activeRun.log_text ?? ''} />
                <Button sx={{ mt: 1 }} onClick={handleAcceptBaseline}>
                  Accept Baseline
                </Button>
              </>
            ) : (
              <Typography>No runs selected.</Typography>
            )}
          </Box>
        </Box>
      </Stack>

      <Dialog open={isGenerateOpen} onClose={() => setIsGenerateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate SQL Unit Tests</DialogTitle>
        <DialogContent>
          <TextField
            type="number"
            label="Number of tests"
            value={numberOfTests}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) => setNumberOfTests(Number(event.target.value))}
            fullWidth
            sx={{ mt: 1 }}
          />
          <TextField
            label="Goals / Notes"
            value={notes}
            onChange={(event: React.ChangeEvent<HTMLInputElement>) => setNotes(event.target.value)}
            fullWidth
            multiline
            minRows={3}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsGenerateOpen(false)}>Cancel</Button>
          <Button onClick={handleGenerateTests}>Generate</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={isEditOpen} onClose={() => setIsEditOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Test Case Details</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Name" value={selectedTest.name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, name: e.target.value })} fullWidth />
            <TextField label="Description" value={selectedTest.description} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, description: e.target.value })} multiline minRows={2} fullWidth />
            <TextField label="Params JSON" value={selectedTest.params_json} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, params_json: e.target.value })} multiline minRows={3} fullWidth />
            <TextField label="Setup SQL" value={selectedTest.setup_sql} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, setup_sql: e.target.value })} multiline minRows={3} fullWidth />
            <TextField label="Act SQL" value={selectedTest.act_sql} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, act_sql: e.target.value })} multiline minRows={3} fullWidth />
            <TextField label="Assertion Type" value={selectedTest.assertion_type} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, assertion_type: e.target.value as ITestCase['assertion_type'] })} fullWidth />
            <TextField label="Assert SQL" value={selectedTest.assert_sql} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, assert_sql: e.target.value })} multiline minRows={3} fullWidth />
            <TextField label="Actual Schema SQL" value={selectedTest.actual_schema_sql ?? ''} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, actual_schema_sql: e.target.value })} multiline minRows={3} fullWidth />
            <TextField label="Expected Schema SQL" value={selectedTest.expected_schema_sql ?? ''} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, expected_schema_sql: e.target.value })} multiline minRows={3} fullWidth />
            <TextField label="OPENJSON WITH clause" value={selectedTest.openjson_with_clause ?? ''} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedTest({ ...selectedTest, openjson_with_clause: e.target.value })} multiline minRows={2} fullWidth />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveTestCase}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
