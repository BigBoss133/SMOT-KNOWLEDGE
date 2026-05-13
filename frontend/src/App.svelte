<script>
  import { view, isThinking, terminalLogs, settings, brainStats } from './lib/stores/app.js'
  import Chat from './lib/components/Chat.svelte'
  import BrainView from './lib/components/BrainView.svelte'
  import SourcesPanel from './lib/components/SourcesPanel.svelte'
  import SettingsPanel from './lib/components/SettingsPanel.svelte'
  import TerminalPanel from './lib/components/TerminalPanel.svelte'

  let showTerminal = $state(false)

  function toggleTerminal() {
    showTerminal = !showTerminal
  }
</script>

<div class="h-screen flex flex-col bg-brain-900 bg-grid overflow-hidden">
  <!-- Header -->
  <header class="flex items-center justify-between px-5 py-3 border-b border-brain-700/50 shrink-0">
    <div class="flex items-center gap-3">
      <span class="text-xl">⚡</span>
      <h1 class="text-sm font-semibold tracking-wide text-brain-100">
        SMOT-KNOWLEDGE
      </h1>
      {#if $isThinking}
        <span class="flex items-center gap-1.5 text-xs text-accent-cyan">
          <span class="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse-glow"></span>
          elaborazione...
        </span>
      {/if}
    </div>
    <button
      onclick={toggleTerminal}
      class="text-xs text-brain-400 hover:text-brain-200 transition-colors px-2 py-1 rounded hover:bg-brain-700/50"
    >
      {showTerminal ? '⊟ Terminale' : '⊞ Terminale'}
    </button>
  </header>

  <!-- Main content -->
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

  <!-- Terminal panel (collapsible) -->
  {#if showTerminal || $settings.terminalVisible}
    <div class="transition-all duration-300 ease-in-out" class:max-h-48={showTerminal} class:max-h-0={!showTerminal}>
      {#if showTerminal}
        <TerminalPanel />
      {/if}
    </div>
  {/if}

  <!-- Bottom navigation -->
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
