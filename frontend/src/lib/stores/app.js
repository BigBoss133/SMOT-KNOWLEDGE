import { writable } from 'svelte/store'

export const view = writable('chat')
export const messages = writable([])
export const isThinking = writable(false)
export const terminalLogs = writable([])
export const streamingContent = writable('')

export const sources = writable([
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

export const brainStats = writable({
  memories: 0, curiosityScore: 0, activeConnections: 0, lastConsolidation: null,
})

export const settings = writable({
  model: 'gemma3:4b',
  curiosityEnabled: true,
  terminalVisible: true,
  wsConnected: false,
})

let ws = null
let reconnectTimer = null
let reconnectAttempts = 0

function getWsUrl() {
  const loc = window.location
  const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${loc.host}/ws`
}

export function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return
  try {
    ws = new WebSocket(getWsUrl())
  } catch (e) {
    scheduleReconnect()
    return
  }

  ws.onopen = () => {
    settings.update(s => ({ ...s, wsConnected: true }))
    reconnectAttempts = 0
  }

  ws.onmessage = (event) => {
    try {
      handleMessage(JSON.parse(event.data))
    } catch (e) { /* ignore */ }
  }

  ws.onclose = () => {
    settings.update(s => ({ ...s, wsConnected: false }))
    scheduleReconnect()
  }

  ws.onerror = () => ws?.close()
}

function scheduleReconnect() {
  if (reconnectTimer) return
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000)
  reconnectAttempts++
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    connectWebSocket()
  }, delay)
}

export function sendMessage(text) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    messages.update(m => [...m, {
      role: 'assistant', content: 'Backend non connesso. Avvia: `cd backend && uvicorn main:app --reload`',
      id: crypto.randomUUID(),
    }])
    return
  }
  ws.send(JSON.stringify({ type: 'chat', text }))
}

function handleMessage(data) {
  switch (data.type) {
    case 'terminal':
      terminalLogs.update(l => [...l.slice(-200), {
        id: crypto.randomUUID(), time: data.time || new Date().toLocaleTimeString(),
        message: data.message, type: data.log_type || 'info',
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
        role: 'assistant', content: data.content || '',
        sources: data.sources || [],
        curiosity: data.curiosity || [],
        id: crypto.randomUUID(),
      }])
      break
    case 'pong':
      break
  }
}

export function loadChatHistory() {
  try {
    const saved = localStorage.getItem('smot-chat')
    if (saved) messages.set(JSON.parse(saved))
  } catch { /* ignore */ }
}

export function saveChatHistory() {
  const unsub = messages.subscribe(m => {
    try { localStorage.setItem('smot-chat', JSON.stringify(m.slice(-100))) } catch { /* ignore */ }
  })
  return unsub
}

export function clearChat() {
  messages.set([])
  localStorage.removeItem('smot-chat')
}
