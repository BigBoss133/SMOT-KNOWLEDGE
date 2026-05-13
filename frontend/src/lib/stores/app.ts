import { writable } from 'svelte/store'

export type MessageRole = 'user' | 'assistant'

export interface Message {
  id: string
  role: MessageRole
  content: string
  sources?: { title: string; relevance: number }[]
  curiosity?: string[]
}

export interface Source {
  id: string
  name: string
  active: boolean
  type: string
}

export interface BrainStats {
  memories: number
  curiosityScore: number
  activeConnections: number
  lastConsolidation: string | null
}

export interface Settings {
  model: string
  curiosityEnabled: boolean
  terminalVisible: boolean
  wsConnected: boolean
}

export interface TerminalEntry {
  id: string
  time: string
  message: string
  type: string
}

export const view = writable<string>('chat')
export const messages = writable<Message[]>([])
export const isThinking = writable<boolean>(false)
export const terminalLogs = writable<TerminalEntry[]>([])
export const streamingContent = writable<string>('')

export const sources = writable<Source[]>([
  { id: 'scihub', name: 'Sci-Hub', active: true, type: 'paper' },
  { id: 'semantic', name: 'Semantic Scholar', active: true, type: 'academic' },
  { id: 'arxiv', name: 'arXiv', active: true, type: 'preprint' },
  { id: 'pubmed', name: 'PubMed', active: true, type: 'biomedical' },
  { id: 'openalex', name: 'OpenAlex', active: true, type: 'catalog' },
  { id: 'core', name: 'CORE', active: true, type: 'open-access' },
  { id: 'unpaywall', name: 'Unpaywall', active: true, type: 'resolver' },
  { id: 'crossref', name: 'CrossRef', active: true, type: 'metadata' },
  { id: 'dblp', name: 'DBLP', active: true, type: 'cs-biblio' },
])

export const brainStats = writable<BrainStats>({
  memories: 0, curiosityScore: 0, activeConnections: 0, lastConsolidation: null,
})

export const settings = writable<Settings>({
  model: 'gemma3:4b',
  curiosityEnabled: true,
  terminalVisible: true,
  wsConnected: false,
})

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let reconnectAttempts = 0

function getWsUrl(): string {
  const loc = window.location
  const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${loc.host}/ws`
}

export function connectWebSocket(): void {
  if (ws && ws.readyState === WebSocket.OPEN) return
  try {
    ws = new WebSocket(getWsUrl())
  } catch {
    scheduleReconnect()
    return
  }
  ws.onopen = () => {
    settings.update(s => ({ ...s, wsConnected: true }))
    reconnectAttempts = 0
  }
  ws.onmessage = (event: MessageEvent) => {
    try {
      handleMessage(JSON.parse(event.data))
    } catch { /* ignore */ }
  }
  ws.onclose = () => {
    settings.update(s => ({ ...s, wsConnected: false }))
    scheduleReconnect()
  }
  ws.onerror = () => ws?.close()
}

function scheduleReconnect(): void {
  if (reconnectTimer) return
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000)
  reconnectAttempts++
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    connectWebSocket()
  }, delay)
}

export function sendMessage(text: string): void {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    messages.update(m => [...m, {
      role: 'assistant', content: 'Backend non connesso. Avvia: `cd backend && uvicorn main:app --reload`',
      id: crypto.randomUUID(),
    }])
    return
  }
  ws.send(JSON.stringify({ type: 'chat', text }))
}

interface WSMessage {
  type: string
  content?: string
  message?: string
  log_type?: string
  time?: string
  sources?: { title: string; relevance: number }[]
  curiosity?: string[]
  done?: boolean
}

function handleMessage(data: WSMessage): void {
  switch (data.type) {
    case 'terminal':
      terminalLogs.update(l => [...l.slice(-200), {
        id: crypto.randomUUID(),
        time: data.time || new Date().toLocaleTimeString(),
        message: data.message || '',
        type: data.log_type || 'info',
      }])
      break
    case 'token':
      streamingContent.update(c => c + (data.content || ''))
      isThinking.set(true)
      break
    case 'response':
      streamingContent.set('')
      isThinking.set(false)
      messages.update(m => [...m, {
        role: 'assistant',
        content: data.content || '',
        sources: data.sources || [],
        curiosity: data.curiosity || [],
        id: crypto.randomUUID(),
      }])
      break
  }
}

export function loadChatHistory(): void {
  try {
    const saved = localStorage.getItem('smot-chat')
    if (saved) messages.set(JSON.parse(saved))
  } catch { /* ignore */ }
}

export function saveChatHistory(): () => void {
  return messages.subscribe(m => {
    try { localStorage.setItem('smot-chat', JSON.stringify(m.slice(-100))) } catch { /* ignore */ }
  })
}

export function clearChat(): void {
  messages.set([])
  localStorage.removeItem('smot-chat')
}
