import { useState } from 'react'
import { api } from '../api'
import EmptyState from '../components/EmptyState'
import EntityPicker from '../components/EntityPicker'
import ErrorBanner from '../components/ErrorBanner'
import LoadingState from '../components/LoadingState'
import type { PathResult } from '../types'

export default function PathFinder() {
  const [fromId, setFromId] = useState('')
  const [toId, setToId] = useState('')
  const [result, setResult] = useState<PathResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const findPath = async (from: string, to: string) => {
    if (!from || !to) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      setResult(await api.shortestPath(from, to))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const fetchPeople = async (q: string) => {
    const people = await api.people(q)
    return people.map((p) => ({ id: p.id, label: p.name, sublabel: p.title }))
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
          <EntityPicker
            placeholder="Search person A by name…"
            fetchOptions={fetchPeople}
            onSelect={(opt) => {
              setFromId(opt.id)
              if (toId) findPath(opt.id, toId)
            }}
          />
          <EntityPicker
            placeholder="Search person B by name…"
            fetchOptions={fetchPeople}
            onSelect={(opt) => {
              setToId(opt.id)
              if (fromId) findPath(fromId, opt.id)
            }}
          />
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
          <EmptyState label="Pick two people to see how they're connected." />
        )}
      </section>
    </div>
  )
}