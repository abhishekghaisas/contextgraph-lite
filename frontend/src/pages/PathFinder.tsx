import { useState } from 'react'
import { api } from '../api'
import EmptyState from '../components/EmptyState'
import ErrorBanner from '../components/ErrorBanner'
import LoadingState from '../components/LoadingState'
import type { PathResult } from '../types'

export default function PathFinder() {
  const [fromId, setFromId] = useState('')
  const [toId, setToId] = useState('')
  const [result, setResult] = useState<PathResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const findPath = async () => {
    if (!fromId || !toId) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      setResult(await api.shortestPath(fromId, toId))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Path Finder</h1>
      <p className="subtitle">
        Find the shortest chain of context connecting two people — the query a chain of
        relational joins would struggle with.
      </p>

      <section className="card">
        <div className="row">
          <input
            className="input"
            placeholder="Person A id…"
            value={fromId}
            onChange={(e) => setFromId(e.target.value)}
          />
          <input
            className="input"
            placeholder="Person B id…"
            value={toId}
            onChange={(e) => setToId(e.target.value)}
          />
          <button className="btn" onClick={findPath}>
            Find path
          </button>
        </div>

        {loading && <LoadingState label="Walking the graph…" />}
        {error && <ErrorBanner message={error} />}
        {!loading && !error && result && (
          <ol className="path">
            {result.path.map((node, i) => (
              <li key={i}>
                {node}
                {i < result.hops.length && <span className="hop">{result.hops[i]}</span>}
              </li>
            ))}
          </ol>
        )}
        {!loading && !error && !result && (
          <EmptyState label="Enter two person ids to see how they're connected." />
        )}
      </section>
    </div>
  )
}
