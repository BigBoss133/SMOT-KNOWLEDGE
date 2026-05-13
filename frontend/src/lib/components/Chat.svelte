<script>
  import { messages, isThinking, streamingContent, sendMessage, clearChat, settings, sources } from '../stores/app.js'
  import Message from './Message.svelte'
  import InputBar from './InputBar.svelte'

  let chatContainer = $state(null)
  let useNewMsg = $state(0)

  $effect(() => {
    const count = useNewMsg
    if (count && chatContainer) {
      requestAnimationFrame(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight
      })
    }
  })

  $effect(() => {
    const val = $messages
    useNewMsg++
  })

  $effect(() => {
    const val = $streamingContent
    if (val && chatContainer) {
      requestAnimationFrame(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight
      })
    }
  })

  function handleSend(text) {
    const userMsg = { role: 'user', content: text, id: crypto.randomUUID() }
    messages.update(m => [...m, userMsg])
    sendMessage(text)
  }
</script>

<div class="flex flex-col h-full">
  <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4" bind:this={chatContainer}>
    {#if $messages.length === 0}
      <div class="flex flex-col items-center justify-center h-full text-center space-y-4">
        <div class="text-5xl animate-pulse-glow">⚡</div>
        <div>
          <p class="text-brain-200 font-semibold text-xl tracking-wide">SMOT-KNOWLEDGE</p>
          <p class="text-sm text-brain-400 mt-1">RAG personale con cervello simulato</p>
        </div>
        <div class="flex items-center gap-2 text-xs text-brain-500">
          <span class="w-2 h-2 rounded-full {$settings.wsConnected ? 'bg-accent-emerald' : 'bg-red-400'}"
                class:animate-pulse-glow={!$settings.wsConnected}></span>
          {$settings.wsConnected ? 'Backend connesso' : 'Backend disconnesso'}
          <span class="text-brain-600">|</span>
          Modello: {$settings.model}
        </div>
        <div class="grid grid-cols-2 gap-2 max-w-sm mt-4 w-full px-4">
          {#each [
            'Spiegami l\'attention nei transformer',
            'Cosa sono i modelli MoE?',
            'Differenza tra RAG e fine-tuning',
            'Come funziona il RLHF?',
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
        <button onclick={clearChat}
          class="text-[11px] text-brain-500 hover:text-brain-300 transition-colors">
          cancella cronologia
        </button>
      </div>
    {:else}
      {#each $messages as msg (msg.id)}
        <div class="message-enter">
          <Message {msg} />
        </div>
      {/each}
    {/if}

    {#if $isThinking}
      <div class="message-enter">
        <div class="flex items-start gap-3 max-w-3xl mx-auto">
          <div class="w-8 h-8 rounded-full bg-accent-cyan/20 flex items-center justify-center text-sm shrink-0 animate-pulse-glow">⚡</div>
          <div class="flex-1 min-w-0">
            <div class="bg-brain-800/80 border border-brain-700/30 rounded-2xl rounded-tl-md px-4 py-2.5">
              {#if $streamingContent}
                <p class="text-sm text-brain-100 leading-relaxed whitespace-pre-wrap">{$streamingContent}<span class="cursor-blink text-accent-cyan">▌</span></p>
              {:else}
                <div class="flex items-center gap-1.5 text-brain-400 text-sm">
                  <span class="w-2 h-2 rounded-full bg-accent-cyan animate-pulse-glow"></span>
                  <span class="w-2 h-2 rounded-full bg-accent-cyan animate-pulse-glow" style="animation-delay: 0.2s"></span>
                  <span class="w-2 h-2 rounded-full bg-accent-cyan animate-pulse-glow" style="animation-delay: 0.4s"></span>
                </div>
              {/if}
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <div class="shrink-0 px-4 py-3 border-t border-brain-700/30">
    <InputBar {handleSend} disabled={$isThinking} />
  </div>
</div>
