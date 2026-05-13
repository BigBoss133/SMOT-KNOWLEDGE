<script lang="ts">
  import { sources } from '../stores/app.js'

  const typeLabels: Record<string, string> = {
    paper: 'Paper', academic: 'Accademico', preprint: 'Preprint', biomedical: 'Biomedicale',
    catalog: 'Catalogo', 'open-access': 'OA', resolver: 'Resolver', metadata: 'Metadati', 'cs-biblio': 'CS Biblio',
  }
  const typeStyles: Record<string, string> = {
    paper: 'text-accent-orange bg-accent-orange/10 border-accent-orange/20',
    academic: 'text-accent-cyan bg-accent-cyan/10 border-accent-cyan/20',
    preprint: 'text-accent-purple bg-accent-purple/10 border-accent-purple/20',
    biomedical: 'text-accent-emerald bg-accent-emerald/10 border-accent-emerald/20',
    catalog: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    'open-access': 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
    resolver: 'text-pink-400 bg-pink-400/10 border-pink-400/20',
    metadata: 'text-brain-300 bg-brain-700/30 border-brain-600/30',
    'cs-biblio': 'text-green-400 bg-green-400/10 border-green-400/20',
  }

  function toggle(id: string) {
    sources.update(s => s.map(src => src.id === id ? { ...src, active: !src.active } : src))
  }
</script>

<div class="h-full flex flex-col p-4 space-y-3">
  <div class="flex items-center justify-between">
    <h2 class="text-sm font-semibold text-brain-100">📚 Fonti di Ricerca</h2>
    <span class="text-[10px] text-brain-400 font-mono">{($sources).filter(s => s.active).length}/9 attive</span>
  </div>
  <div class="flex-1 overflow-y-auto space-y-1.5">
    {#each $sources as source (source.id)}
      <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 border
        {source.active ? 'bg-brain-800/50 border-brain-600/40 hover:border-accent-cyan/30' : 'bg-brain-800/20 border-brain-700/20 opacity-50 hover:opacity-80'}">
        <input type="checkbox" checked={source.active} onchange={() => toggle(source.id)}
          class="w-4 h-4 rounded border-brain-500 bg-brain-800 text-accent-cyan focus:ring-accent-cyan/30 focus:ring-offset-0 accent-accent-cyan" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-brain-100">{source.name}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded-full border {typeStyles[source.type] || typeStyles.metadata}">
              {typeLabels[source.type] || source.type}
            </span>
          </div>
        </div>
        <span class="text-[11px] font-mono {source.active ? 'text-accent-cyan' : 'text-brain-500'}">{source.active ? '● attivo' : '○ spento'}</span>
      </label>
    {/each}
  </div>
</div>
