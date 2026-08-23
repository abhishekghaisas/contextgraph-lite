import { useEffect, useState } from 'react'
import { api } from '../api'
import EmptyState from '../components/EmptyState'
import ErrorBanner from '../components/ErrorBanner'
import LoadingState from '../components/LoadingState'
import type { ContextResult, Person } from '../types'

export default function Dashboard() {
  const [query, setQuery] = useState('')
  const [people, setPeople] = useState<Person[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [taskId, setTaskId] = useState('')
  const [context, setContext] = useState<ContextResult[] | null>(null)
  const [contextLoading, setContextLoading] = useState(false)
  const [contextError, setContextError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    api
      .people(query || undefined)
      .then(setPeople)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [query])

  const loadContext = async () => {
    if (!taskId) return
    setContextLoading(true)
    setContextError(null)
    try {
      setContext(await api.contextForTask(taskId))
    } catch (e) {
      setContextError((e as Error).message)
    } finally {
      setContextLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p className="subtitle">Search the org, or pull up everyone with context on a task.</p>

      <section className="card">
        <h2>People</h2>
        <input
          className="input"
          placeholder="Search by name…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {loading && <LoadingState label="Searching people…" />}
        {error && <ErrorBanner message={error} />}
        {!loading && !error && people.length === 0 && <EmptyState label="No people found." />}
        {!loading && !error && people.length > 0 && (
          <ul className="list">
            {people.map((p) => (
              <li key={p.id}>
                <strong>{p.name}</strong>
                <span>
                  {p.title}
                  {p.team ? ` · ${p.team}` : ''}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Who has context on a task?</h2>
        <div className="row">
          <input
            className="input"
            placeholder="Paste a task id (e.g. task_a1b2c3d4)…"
            value={taskId}
            onChange={(e) => setTaskId(e.target.value)}
          />
          <button className="btn" onClick={loadContext}>
            Find context
          </button>
        </div>
        {contextLoading && <LoadingState label="Traversing the graph…" />}
        {contextError && <ErrorBanner message={contextError} />}
        {!contextLoading && !contextError && context && context.length === 0 && (
          <EmptyState label="No one found within 3 hops of this task." />
        )}
        {!contextLoading && !contextError && context && context.length > 0 && (
          <ul className="list">
            {context.map((c, i) => (
              <li key={i}>
                <strong>{c.person}</strong>
                <span>{c.title}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
