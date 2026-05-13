<script>
  import { view, isThinking, settings, brainStats } from './lib/stores/app.js'
  import Chat from './lib/components/Chat.svelte'
  import BrainView from './lib/components/BrainView.svelte'
  import SourcesPanel from './lib/components/SourcesPanel.svelte'
  import SettingsPanel from './lib/components/SettingsPanel.svelte'
  import TerminalPanel from './lib/components/TerminalPanel.svelte'

  let showTerminal = $state(false)
  let clock = $state(new Date().toLocaleTimeString())

  function toggleTerminal() {
    showTerminal = !showTerminal
  }

  function fetchStats() {
    fetch('http://localhost:8000/api/stats')
      .then(r => r.json())
      .then(d => brainStats.set(d))
      .catch(() => {})
  }

  $effect(() => {
    const timer = setInterval(() => {
      clock = new Date().toLocaleTimeString()
    }, 1000)
    fetchStats()
    const statsTimer = setInterval(fetchStats, 10000)
    return () => { clearInterval(timer); clearInterval(statsTimer) }
  })
</script>

<div class="h-screen flex flex-col bg-brain-900 bg-grid overflow-hidden">
  <header class="flex items-center justify-between px-5 py-3 border-b border-brain-700/50 shrink-0">
    <div class="flex items-center gap-3">
      <span class="text-xl">⚡</span>
      <h1 class="text-sm font-semibold tracking-wide text-brain-100">SMOT-KNOWLEDGE</h1>
      <span class="flex items-center gap-1.5 text-[11px] text-brain-500">
        <span class="w-1.5 h-1.5 rounded-full {$settings.wsConnected ? 'bg-accent-emerald' : 'bg-red-400'}"
              class:animate-pulse-glow={!$settings.wsConnected}></span>
        {$settings.wsConnected ? 'connesso' : 'offline'}
      </span>
      {#if $isThinking}
        <span class="flex items-center gap-1.5 text-xs text-accent-cyan">
          <span class="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse-glow"></span>
          elaborazione...
        </span>
      {/if}
    </div>
    <div class="flex items-center gap-3">
      <span class="text-[10px] text-brain-500 font-mono">{clock}</span>
      <button
        onclick={toggleTerminal}
        class="text-xs text-brain-400 hover:text-brain-200 transition-colors px-2 py-1 rounded hover:bg-brain-700/50"
      >
        {showTerminal ? '⊟ Terminale' : '⊞ Terminale'}
      </button>
    </div>
  </header>

  <main class="flex-1 overflow-hidden relative">
    {#if $view === 'chat'}
      <Chat />
    {:else if $view === 'brain'}
      <BrainView />
    {:else if $view === 'sources'}
      <SourcesPanel />
    {:else if $view === 'settings'}
      <SettingsPanel />
    {/if}
  </main>

  {#if showTerminal}
    <TerminalPanel />
  {/if}

  <nav class="flex items-center justify-around px-4 py-2 border-t border-brain-700/50 bg-brain-800/50 shrink-0">
    {#each [
      { id: 'chat', icon: '💬', label: 'Chat' },
      { id: 'brain', icon: '🧠', label: 'Cervello' },
      { id: 'sources', icon: '📚', label: 'Fonti' },
      { id: 'settings', icon: '⚙️', label: 'Impostazioni' },
    ] as tab}
      <button
        onclick={() => view.set(tab.id)}
        class="flex flex-col items-center gap-0.5 px-4 py-1 rounded-lg transition-all duration-200
          {$view === tab.id
            ? 'text-accent-cyan bg-accent-cyan/10'
            : 'text-brain-400 hover:text-brain-200 hover:bg-brain-700/30'}"
      >
        <span class="text-lg leading-none">{tab.icon}</span>
        <span class="text-[10px] font-medium">{tab.label}</span>
      </button>
    {/each}
  </nav>
</div>
