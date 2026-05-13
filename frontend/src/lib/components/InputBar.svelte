<script lang="ts">
  let { handleSend, disabled = false }: { handleSend: (t: string) => void; disabled?: boolean } = $props()
  let input = $state('')
  let inputEl: HTMLTextAreaElement | undefined = $state()

  function submit() {
    const text = input.trim()
    if (!text || disabled) return
    handleSend(text)
    input = ''
    inputEl?.focus()
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() }
  }
</script>

<div class="flex items-end gap-2">
  <textarea bind:this={inputEl} bind:value={input} onkeydown={onKeydown} disabled={disabled}
    placeholder="Chiedi qualcosa..." rows="1"
    class="flex-1 resize-none rounded-xl px-4 py-3 text-sm bg-brain-800/80 border border-brain-600/50 placeholder:text-brain-500 text-brain-100 focus:outline-none focus:border-accent-cyan/40 focus:ring-1 focus:ring-accent-cyan/20 disabled:opacity-50 transition-all duration-200"
    oninput={() => { inputEl!.style.height = 'auto'; inputEl!.style.height = Math.min(inputEl!.scrollHeight, 120) + 'px' }}
  ></textarea>
  <button aria-label="Invia messaggio" onclick={submit} disabled={disabled || !input.trim()}
    class="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/25 hover:bg-accent-cyan/25 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200"
  >
    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7" />
    </svg>
  </button>
</div>
