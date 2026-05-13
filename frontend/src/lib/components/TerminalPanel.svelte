<script>
  import { terminalLogs } from '../stores/app.js'

  let isPaused = $state(false)
  let terminalEl = $state(null)

  $effect(() => {
    if (!isPaused && terminalEl) {
      requestAnimationFrame(() => {
        terminalEl.scrollTop = terminalEl.scrollHeight
      })
    }
  })

  const typeColors = {
    brain: 'text-accent-cyan',
    search: 'text-accent-purple',
    system: 'text-brain-400',
    success: 'text-accent-emerald',
    error: 'text-red-400',
    info: 'text-brain-300',
  }

  const typeIcons = {
    brain: '  ',
    search: '  ',
    system: '  ',
    success: ' ✅',
    error: ' ❌',
    info: ' ℹ️',
  }
</script>

<div class="bg-brain-950 border-t border-brain-700/30">
  <div class="flex items-center justify-between px-4 py-1.5 bg-brain-900/80">
    <div class="flex items-center gap-2">
      <span class="text-xs font-semibold text-brain-300 font-mono">▶ Terminale</span>
      <span class="text-[10px] text-brain-500 font-mono">{$terminalLogs.length} linee</span>
    </div>
    <button
      onclick={() => isPaused = !isPaused}
      class="text-[10px] px-2 py-0.5 rounded font-mono transition-colors
        {isPaused ? 'text-accent-orange bg-accent-orange/10' : 'text-brain-400 hover:text-brain-200'}"
    >
      {isPaused ? '  Riprendi' : '  Pausa'}
    </button>
  </div>

  <div bind:this={terminalEl} class="h-40 overflow-y-auto px-4 py-2 space-y-0.5 font-mono text-[12px] leading-5">
    {#if $terminalLogs.length === 0}
      <div class="text-brain-600 italic">In attesa di attività...</div>
    {:else}
      {#each $terminalLogs as log (log.id)}
        <div class="terminal-line flex items-start gap-2 {typeColors[log.type] || 'text-brain-300'}">
          <span class="text-brain-600 shrink-0 w-14">[{log.time}]</span>
          <span class="shrink-0">{typeIcons[log.type] || ' ℹ️'}</span>
          <span class="break-all">{log.message}</span>
        </div>
      {/each}
    {/if}
  </div>
</div>
