<script lang="ts">
  import { brainStats, settings } from '../stores/app.js'

  interface KGNode {
    id: string
    label: string
    category: string
    connections: string[]
  }

  interface KGData {
    nodes: KGNode[]
    curiosities: string[]
  }

  let kg = $state<KGData>({ nodes: [], curiosities: [] })

  const sizeByCategory: Record<string, string> = {
    core: 'lg', architecture: 'lg', training: 'md',
    system: 'md', field: 'md', curiosity: 'sm',
  }

  const sizeClasses: Record<string, string> = {
    sm: 'w-14 h-14', md: 'w-20 h-20', lg: 'w-24 h-24',
  }

  function fetchKG() {
    fetch('/api/knowledge-graph')
      .then(r => r.json())
      .then(d => kg = d)
      .catch(() => {})
  }

  $effect(() => {
    fetchKG()
    const id = setInterval(fetchKG, 15000)
    return () => clearInterval(id)
  })
</script>

<div class="h-full flex flex-col p-4 space-y-4">
  <div class="grid grid-cols-3 gap-3">
    {#each [
      { label: 'Memorie', value: ($brainStats.memories || 0).toString(), icon: '🧠' },
      { label: 'Curiosità', value: $brainStats.curiosityScore ? `${$brainStats.curiosityScore}%` : '—', icon: '💡' },
      { label: 'Connessioni', value: ($brainStats.activeConnections || 0).toString(), icon: '🔗' },
    ] as stat}
      <div class="bg-brain-800/50 border border-brain-700/30 rounded-xl p-3 text-center">
        <span class="text-lg">{stat.icon}</span>
        <p class="text-lg font-bold text-brain-100 mt-0.5">{stat.value}</p>
        <p class="text-[10px] text-brain-400 font-medium">{stat.label}</p>
      </div>
    {/each}
  </div>

  <div class="flex-1 bg-brain-800/30 border border-brain-700/20 rounded-xl relative overflow-hidden">
    <div class="absolute inset-0 bg-grid opacity-30"></div>
    {#if kg.nodes.length === 0}
      <div class="absolute inset-0 flex items-center justify-center text-brain-500 text-sm">
        Chiedi qualcosa per popolare il grafo
      </div>
    {:else}
      <div class="absolute inset-0 flex items-center justify-center">
        {#each kg.nodes as node, i}
          {@const angle = (i / kg.nodes.length) * 2 * Math.PI - Math.PI / 2}
          {@const radius = 25 + (i % 3) * 8}
          {@const x = 50 + radius * Math.cos(angle)}
          {@const y = 50 + radius * Math.sin(angle)}
          <div class="absolute transform -translate-x-1/2 -translate-y-1/2 text-center cursor-pointer transition-all duration-300 hover:scale-110"
            style="left: {x}%; top: {y}%;">
            <div class="mx-auto rounded-full flex items-center justify-center bg-accent-cyan/10 border border-accent-cyan/20 hover:bg-accent-cyan/20 hover:border-accent-cyan/40 transition-all duration-300 animate-brain-pulse {sizeClasses[sizeByCategory[node.category] || 'sm']}">
              <span class="text-[10px] font-medium text-accent-cyan/80 leading-tight px-1">{node.label}</span>
            </div>
          </div>
        {/each}

        <svg class="absolute inset-0 w-full h-full" style="pointer-events: none;">
          {#each kg.nodes as a}
            {#each a.connections as connId}
              {@const b = kg.nodes.find(n => n.id === connId)}
              {#if b}
                {@const ai = kg.nodes.indexOf(a)}
                {@const bi = kg.nodes.indexOf(b)}
                {@const aAngle = (ai / kg.nodes.length) * 2 * Math.PI - Math.PI / 2}
                {@const bAngle = (bi / kg.nodes.length) * 2 * Math.PI - Math.PI / 2}
                {@const aRad = 25 + (ai % 3) * 8}
                {@const bRad = 25 + (bi % 3) * 8}
                {@const ax = 50 + aRad * Math.cos(aAngle)}
                {@const ay = 50 + aRad * Math.sin(aAngle)}
                {@const bx = 50 + bRad * Math.cos(bAngle)}
                {@const by = 50 + bRad * Math.sin(bAngle)}
                <line x1="{ax}%" y1="{ay}%" x2="{bx}%" y2="{by}%"
                  stroke="rgba(0,212,255,0.08)" stroke-width="1" />
              {/if}
            {/each}
          {/each}
        </svg>
      </div>
    {/if}

    <div class="absolute bottom-3 left-3 text-[10px] text-brain-500 font-mono">
      {kg.nodes.length} nodi · {kg.nodes.reduce((s, n) => s + n.connections.length, 0)} connessioni
    </div>
  </div>

  {#if kg.curiosities.length > 0}
    <div class="flex flex-wrap gap-2">
      {#each kg.curiosities as c}
        <span class="text-[11px] px-2 py-1 rounded-full bg-accent-purple/10 text-accent-purple/70 border border-accent-purple/15">💡 {c}</span>
      {/each}
    </div>
  {/if}

  <div class="text-xs text-brain-400 font-mono space-y-0.5">
    <p class="text-brain-500">▸ Modello: {$settings.model}</p>
    <p class="text-brain-500">▸ Consolidazione: {$brainStats.lastConsolidation || '—'}</p>
  </div>
</div>
