import { useEffect, useState } from 'react'
import { getJson } from './api'

type Status = 'checking' | 'ok' | 'down'

function useStatus(path: string): Status {
  const [status, setStatus] = useState<Status>('checking')
  useEffect(() => {
    getJson(path)
      .then(() => setStatus('ok'))
      .catch(() => setStatus('down'))
  }, [path])
  return status
}

const label: Record<Status, string> = {
  checking: 'Checking…',
  ok: 'Connected',
  down: 'Not reachable',
}

function StatusRow({ name, status }: { name: string; status: Status }) {
  const colour =
    status === 'ok' ? 'text-green-700' : status === 'down' ? 'text-red-700' : 'text-slate-500'
  return (
    <div className="flex justify-between border-b border-slate-200 py-2">
      <dt>{name}</dt>
      <dd className={`font-medium ${colour}`}>{label[status]}</dd>
    </div>
  )
}

export default function App() {
  const api = useStatus('/health')
  const database = useStatus('/health/db')

  return (
    <main className="mx-auto max-w-md p-8 font-sans text-slate-900">
      <h1 className="text-2xl font-semibold">Brave Clinical System</h1>
      <p className="mt-1 text-slate-600">Development environment status</p>
      <dl className="mt-6" aria-live="polite">
        <StatusRow name="API" status={api} />
        <StatusRow name="Database" status={database} />
      </dl>
    </main>
  )
}
