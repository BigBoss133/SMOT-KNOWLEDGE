<script lang="ts">
  import { brainStats, settings } from '../stores/app.js'

  const nodes = [
    { id: 1, label: 'Transformer\nAttention', x: 50, y: 30, size: 'lg' as const },
    { id: 2, label: 'RLHF', x: 75, y: 45, size: 'md' as const },
    { id: 3, label: 'Computer\nVision', x: 35, y: 55, size: 'md' as const },
    { id: 4, label: 'LLM\nArchitectures', x: 60, y: 65, size: 'lg' as const },
    { id: 5, label: 'Embeddings', x: 25, y: 40, size: 'sm' as const },
    { id: 6, label: 'RAG\nSystems', x: 45, y: 75, size: 'sm' as const },
    { id: 7, label: 'Mixture\nof Experts', x: 80, y: 30, size: 'sm' as const },
    { id: 8, label: 'Tokenization', x: 20, y: 65, size: 'sm' as const },
    { id: 9, label: 'Attention\nMechanism', x: 50, y: 50, size: 'md' as const },
  ]

  const sizeClasses: Record<string, string> = {
    sm: 'w-14 h-14',
    md: 'w-20 h-20',
    lg: 'w-24 h-24',
  }
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
    <div class="absolute inset-0 flex items-center justify-center">
      {#each nodes as node}
        <div class="absolute transform -translate-x-1/2 -translate-y-1/2 text-center cursor-pointer transition-all duration-300 hover:scale-110"
          style="left: {node.x}%; top: {node.y}%;">
          <div class="mx-auto rounded-full flex items-center justify-center bg-accent-cyan/10 border border-accent-cyan/20 hover:bg-accent-cyan/20 hover:border-accent-cyan/40 transition-all duration-300 animate-brain-pulse {sizeClasses[node.size]}">
            <span class="text-[10px] font-medium text-accent-cyan/80 leading-tight px-1">{node.label}</span>
          </div>
        </div>
      {/each}
      <svg class="absolute inset-0 w-full h-full" style="pointer-events: none;">
        {#each nodes as a}
          {#each nodes.filter((_, i) => i > nodes.indexOf(a) && Math.random() > 0.7) as b}
            <line x1="{a.x}%" y1="{a.y}%" x2="{b.x}%" y2="{b.y}%" stroke="rgba(0,212,255,0.08)" stroke-width="1" />
          {/each}
        {/each}
      </svg>
    </div>
    <div class="absolute bottom-3 left-3 text-[10px] text-brain-500 font-mono">
      {nodes.length} nodi · {$brainStats.activeConnections || 0} connessioni
    </div>
  </div>

  <div class="text-xs text-brain-400 font-mono space-y-0.5">
    <p class="text-brain-500">▸ Modello: {$settings.model}</p>
    <p class="text-brain-500">▸ Consolidazione: {$brainStats.lastConsolidation || '—'}</p>
  </div>
</div>
