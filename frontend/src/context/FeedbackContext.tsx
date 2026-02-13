import { createContext, useCallback, useMemo, useState } from 'react'

export enum Severity {
  Success = 'success',
  Error = 'error',
  Info = 'info',
}

export interface FeedbackMessage {
  id: number
  text: string
  severity: Severity
}

interface FeedbackContextValue {
  addMessage: (text: string, severity: Severity) => void
}

export const FeedbackContext = createContext<FeedbackContextValue>({
  addMessage: () => undefined,
})

export function FeedbackProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<FeedbackMessage[]>([])

  const addMessage = useCallback((text: string, severity: Severity) => {
    setMessages((prev) => [...prev, { id: Date.now(), text, severity }])
    // eslint-disable-next-line no-console
    console.log(`[${severity}] ${text}`)
  }, [])

  const value = useMemo(() => ({ addMessage }), [addMessage])

  return (
    <FeedbackContext.Provider value={value}>
      {children}
      <div style={{ position: 'fixed', right: 16, bottom: 16, display: 'grid', gap: 8, zIndex: 9999 }}>
        {messages.slice(-3).map((message) => (
          <div
            key={message.id}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              color: '#fff',
              background: message.severity === Severity.Error ? '#d32f2f' : message.severity === Severity.Success ? '#2e7d32' : '#1565c0',
            }}
          >
            {message.text}
          </div>
        ))}
      </div>
    </FeedbackContext.Provider>
  )
}
