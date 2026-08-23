import type {
  BlockerChain,
  ContextResult,
  ExpertResult,
  PathResult,
  Person,
  Project,
  Task,
} from './types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => request<{ status: string; error?: string }>('/health'),

  people: (q?: string) =>
    request<Person[]>(`/people${q ? `?q=${encodeURIComponent(q)}` : ''}`),

  tasks: (q?: string) =>
    request<Task[]>(`/tasks${q ? `?q=${encodeURIComponent(q)}` : ''}`),

  projects: (q?: string) =>
    request<Project[]>(`/projects${q ? `?q=${encodeURIComponent(q)}` : ''}`),

  contextForTask: (taskId: string, hops = 3) =>
    request<ContextResult[]>(`/context/task/${encodeURIComponent(taskId)}?hops=${hops}`),

  shortestPath: (from: string, to: string) =>
    request<PathResult>(`/path?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`),

  blockersForProject: (projectId: string) =>
    request<BlockerChain[]>(`/blockers/project/${encodeURIComponent(projectId)}`),

  expertsForPerson: (personId: string) =>
    request<ExpertResult[]>(`/experts/${encodeURIComponent(personId)}`),
}