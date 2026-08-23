import { useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import { api } from './api'
import ErrorBanner from './components/ErrorBanner'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import PathFinder from './pages/PathFinder'
import ProjectHealth from './pages/ProjectHealth'

export default function App() {
  const [dbDown, setDbDown] = useState(false)

  useEffect(() => {
    api
      .health()
      .then((h) => setDbDown(h.status !== 'ok'))
      .catch(() => setDbDown(true))
  }, [])

  return (
    <>
      {dbDown && (
        <ErrorBanner message="Can't reach CognoDB right now. Some views may be empty until the connection recovers." />
      )}
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="path" element={<PathFinder />} />
          <Route path="projects" element={<ProjectHealth />} />
        </Route>
      </Routes>
    </>
  )
}
