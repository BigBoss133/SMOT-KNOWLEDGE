import { writable } from 'svelte/store'

export const view = writable('chat')
export const chatMessages = writable([])
export const isThinking = writable(false)
export const terminalLogs = writable([])
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
  memories: 0,
  curiosityScore: 0,
  activeConnections: 0,
  lastConsolidation: null,
})

export const settings = writable({
  model: 'qwen3:7b',
  contextBudget: { instruction: 10, kb: 20, web: 20, academic: 20, reasoning: 10, output: 20 },
  curiosityEnabled: true,
  terminalVisible: true,
})

export function addTerminalLog(message, type = 'info') {
  terminalLogs.update(logs => [...logs.slice(-200), {
    id: crypto.randomUUID(),
    time: new Date().toLocaleTimeString(),
    message,
    type,
  }])
}
