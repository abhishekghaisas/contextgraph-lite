export interface Person {
  id: string
  name: string
  title?: string
  team?: string
}

export interface ContextResult {
  person: string
  title?: string
}

export interface PathResult {
  path: string[]
  hops: string[]
}

export interface BlockerChain {
  rootBlocker: string
  blockedTasks: string[]
}

export interface ExpertResult {
  name: string
  title?: string
}

export interface HealthStatus {
  status: 'ok' | 'unreachable'
  error?: string | null
}
