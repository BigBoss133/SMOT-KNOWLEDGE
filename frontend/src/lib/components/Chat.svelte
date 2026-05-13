<script>
  import { chatMessages, isThinking, addTerminalLog } from '../stores/app.js'
  import Message from './Message.svelte'
  import InputBar from './InputBar.svelte'

  let messages = $state([])
  let chatContainer = $state(null)

  $effect(() => {
    messages = $chatMessages
  })

  $effect(() => {
    if (messages.length && chatContainer) {
      requestAnimationFrame(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight
      })
    }
  })

  function handleSend(text) {
    const userMsg = { role: 'user', content: text, id: crypto.randomUUID() }
    chatMessages.update(m => [...m, userMsg])
    isThinking.set(true)
    addTerminalLog('🧠 Sequential Thinking: decomposizione richiesta...', 'brain')
    addTerminalLog('📡 Ricerca parallela su 9 fonti...', 'search')
    addTerminalLog('🧮 HCE: calcolo contest budget...', 'system')

    setTimeout(() => {
      const brainMsg = {
        role: 'assistant',
        content: `Ecco cosa ho trovato su "${text}".\n\nQuesta è una risposta simulata per la UI. Il backend COAST elaborerà realmente ogni richiesta con sequential thinking, RAG, web search e curiosity engine.`,
        sources: [
          { title: 'Sample Paper (2024)', url: '#', relevance: 0.94 },
          { title: 'arXiv Preprint', url: '#', relevance: 0.87 },
        ],
        curiosity: [
          'Approfondire i meccanismi di attention?',
          'Confronto con architetture alternative?',
        ],
        id: crypto.randomUUID(),
      }
      chatMessages.update(m => [...m, brainMsg])
      isThinking.set(false)
      addTerminalLog('✅ Risposta generata in 2.3s', 'success')
    }, 1500)
  }
</script>

<div class="flex flex-col h-full">
  <!-- Messages -->
  <div bind:this={chatContainer} class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
    {#if messages.length === 0}
      <div class="flex flex-col items-center justify-center h-full text-center text-brain-400 space-y-4">
        <div class="text-4xl animate-brain-pulse">⚡</div>
        <div>
          <p class="text-brain-200 font-medium text-lg">SMOT-KNOWLEDGE</p>
          <p class="text-sm mt-1">Il tuo assistente di ricerca personale</p>
        </div>
        <div class="grid grid-cols-2 gap-2 max-w-sm mt-4">
          {#each [
            'Spiegami l\'attention nei transformer',
            'Cosa dice l\'ultimo paper su RLHF?',
            'Confronta modelli linguistici 2026',
            'Novità nel campo della computer vision',
          ] as suggestion}
            <button
              onclick={() => handleSend(suggestion)}
              class="text-xs text-left px-3 py-2 rounded-lg border border-brain-600/50
                hover:border-accent-cyan/30 hover:text-accent-cyan
                transition-all duration-200 bg-brain-800/50"
            >
              {suggestion}
            </button>
          {/each}
        </div>
      </div>
    {:else}
      {#each messages as msg (msg.id)}
        <div class="message-enter">
          <Message {msg} />
        </div>
      {/each}
    {/if}

    {#if $isThinking}
      <div class="flex items-start gap-3 animate-fade-in">
        <div class="w-8 h-8 rounded-full bg-accent-cyan/20 flex items-center justify-center text-sm shrink-0 animate-pulse-glow">⚡</div>
        <div class="flex items-center gap-1.5 text-brain-400 text-sm">
          <span class="w-2 h-2 rounded-full bg-accent-cyan animate-pulse-glow"></span>
          <span class="w-2 h-2 rounded-full bg-accent-cyan animate-pulse-glow" style="animation-delay: 0.2s"></span>
          <span class="w-2 h-2 rounded-full bg-accent-cyan animate-pulse-glow" style="animation-delay: 0.4s"></span>
        </div>
      </div>
    {/if}
  </div>

  <!-- Input -->
  <div class="shrink-0 px-4 py-3 border-t border-brain-700/30">
    <InputBar {handleSend} disabled={$isThinking} />
  </div>
</div>
