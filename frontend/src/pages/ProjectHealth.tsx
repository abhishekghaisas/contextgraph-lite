import { useState } from 'react'
import { api } from '../api'
import EmptyState from '../components/EmptyState'
import EntityPicker from '../components/EntityPicker'
import ErrorBanner from '../components/ErrorBanner'
import LoadingState from '../components/LoadingState'
import type { BlockerChain } from '../types'

export default function ProjectHealth() {
  const [chains, setChains] = useState<BlockerChain[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadBlockers = async (projectId: string) => {
    setLoading(true)
    setError(null)
    try {
      setChains(await api.blockersForProject(projectId))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Project Health</h1>
      <p className="subtitle">See which root tasks are blocking the most downstream work.</p>

      <section className="card">
        <EntityPicker
          placeholder="Search for a project by name…"
          fetchOptions={async (q) => {
            const projects = await api.projects(q)
            return projects.map((p) => ({ id: p.id, label: p.name, sublabel: p.status }))
          }}
          onSelect={(opt) => loadBlockers(opt.id)}
        />

        {loading && <LoadingState label="Tracing blocker chains…" />}
        {error && <ErrorBanner message={error} />}
        {!loading && !error && chains && chains.length === 0 && (
          <EmptyState label="No blocker chains found for this project — clear runway." />
        )}
        {!loading && !error && chains && chains.length > 0 && (
          <ul className="list">
            {chains.map((c, i) => (
              <li key={i}>
                <strong>{c.rootBlocker}</strong>
                <span>blocks: {c.blockedTasks.join(', ')}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}