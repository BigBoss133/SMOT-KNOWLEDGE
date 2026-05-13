<script lang="ts">
  import { brainStats, settings } from '../stores/app.js'

  interface KGNode { id: string; label: string; category: string; connections: string[] }
  interface KGData { nodes: KGNode[]; curiosities: string[] }

  let kg = $state<KGData>({ nodes: [], curiosities: [] })
  let kbCount = $state(0)
  let kbSearch = $state('')
  let kbResults = $state<string[]>([])

  const sizeClasses: Record<string, string> = {
    sm: 'w-14 h-14', md: 'w-20 h-20', lg: 'w-24 h-24',
  }

  const catSize: Record<string, string> = {
    core: 'lg', architecture: 'lg', training: 'md', system: 'md', field: 'md', curiosity: 'sm',
  }

  function fetchKG() {
    fetch('/api/knowledge-graph').then(r => r.json()).then(d => kg = d).catch(() => {})
    fetch('/api/kb/count').then(r => r.json()).then(d => kbCount = d.count).catch(() => {})
  }

  function searchKB() {
    if (!kbSearch.trim()) { kbResults = []; return }
    fetch(`/api/kb/search?q=${encodeURIComponent(kbSearch)}&top_k=3`)
      .then(r => r.json())
      .then(d => kbResults = d.map((r: any) => r.text.slice(0, 120)))
      .catch(() => kbResults = [])
  }

  $effect(() => {
    fetchKG()
    const id = setInterval(fetchKG, 15000)
    return () => clearInterval(id)
  })
</script>

<div class="h-full flex flex-col p-4 space-y-3">
  <div class="grid grid-cols-4 gap-2">
    {#each [
      { label: 'Memorie', value: ($brainStats.memories || 0).toString(), icon: '🧠' },
      { label: 'Curiosità', value: $brainStats.curiosityScore ? `${$brainStats.curiosityScore}%` : '—', icon: '💡' },
      { label: 'Documenti KB', value: kbCount.toString(), icon: '📚' },
      { label: 'Connessioni', value: ($brainStats.activeConnections || 0).toString(), icon: '🔗' },
    ] as stat}
      <div class="bg-brain-800/50 border border-brain-700/30 rounded-xl p-2 text-center">
        <p class="text-sm font-bold text-brain-100">{stat.value}</p>
        <p class="text-[9px] text-brain-400 font-medium">{stat.label}</p>
      </div>
    {/each}
  </div>

  <div class="flex-1 bg-brain-800/30 border border-brain-700/20 rounded-xl relative overflow-hidden min-h-0">
    <div class="absolute inset-0 bg-grid opacity-30"></div>
    {#if kg.nodes.length === 0}
      <div class="absolute inset-0 flex items-center justify-center text-brain-500 text-sm">Chiedi qualcosa per popolare il grafo</div>
    {:else}
      <div class="absolute inset-0 flex items-center justify-center">
        {#each kg.nodes as node, i}
          {@const angle = (i / kg.nodes.length) * 2 * Math.PI - Math.PI / 2}
          {@const radius = 25 + (i % 3) * 8}
          {@const x = 50 + radius * Math.cos(angle)}
          {@const y = 50 + radius * Math.sin(angle)}
          <div class="absolute transform -translate-x-1/2 -translate-y-1/2 text-center transition-all duration-300 hover:scale-110"
            style="left: {x}%; top: {y}%;">
            <div class="mx-auto rounded-full flex items-center justify-center bg-accent-cyan/10 border border-accent-cyan/20 hover:bg-accent-cyan/20 hover:border-accent-cyan/40 transition-all duration-300 animate-brain-pulse {sizeClasses[catSize[node.category] || 'sm']}">
              <span class="text-[9px] font-medium text-accent-cyan/80 leading-tight px-1">{node.label}</span>
            </div>
          </div>
        {/each}
        <svg class="absolute inset-0 w-full h-full" style="pointer-events: none;">
          {#each kg.nodes as a}
            {#each a.connections as connId}
              {@const b = kg.nodes.find((n: KGNode) => n.id === connId)}
              {#if b}
                {@const ai = kg.nodes.indexOf(a)}
                {@const bi = kg.nodes.indexOf(b)}
                {@const aAngle = (ai / kg.nodes.length) * 2 * Math.PI - Math.PI / 2}
                {@const bAngle = (bi / kg.nodes.length) * 2 * Math.PI - Math.PI / 2}
                {@const aRad = 25 + (ai % 3) * 8}
                {@const bRad = 25 + (bi % 3) * 8}
                <line x1="{50 + aRad * Math.cos(aAngle)}%" y1="{50 + aRad * Math.sin(aAngle)}%"
                  x2="{50 + bRad * Math.cos(bAngle)}%" y2="{50 + bRad * Math.sin(bAngle)}%"
                  stroke="rgba(0,212,255,0.08)" stroke-width="1" />
              {/if}
            {/each}
          {/each}
        </svg>
      </div>
    {/if}
    <div class="absolute bottom-2 left-2 text-[9px] text-brain-500 font-mono">
      {kg.nodes.length} nodi · {kg.nodes.reduce((s: number, n: KGNode) => s + n.connections.length, 0)} connessioni
    </div>
  </div>

  {#if kg.curiosities.length > 0}
    <div class="flex flex-wrap gap-1.5">
      {#each kg.curiosities as c}
        <span class="text-[10px] px-2 py-0.5 rounded-full bg-accent-purple/10 text-accent-purple/70 border border-accent-purple/15">💡 {c}</span>
      {/each}
    </div>
  {/if}

  <div class="flex gap-2 text-xs">
    <input bind:value={kbSearch} oninput={searchKB} placeholder="Cerca nella KB..."
      class="flex-1 px-2 py-1 rounded bg-brain-800/80 border border-brain-600/50 text-brain-100 text-[11px] placeholder:text-brain-500 focus:outline-none focus:border-accent-cyan/40" />
    <span class="text-brain-500 font-mono text-[10px] self-center">{kbCount} doc</span>
  </div>
  {#if kbResults.length > 0}
    <div class="space-y-1 max-h-20 overflow-y-auto">
      {#each kbResults as r}
        <p class="text-[10px] text-brain-400 font-mono leading-tight">📄 {r}...</p>
      {/each}
    </div>
  {/if}

  <div class="text-[10px] text-brain-500 font-mono">
    <p>▸ {$settings.model} · KB: qwen2.5-coder:7b</p>
    <p>▸ Consolidazione: {$brainStats.lastConsolidation || '—'}</p>
  </div>
</div>
