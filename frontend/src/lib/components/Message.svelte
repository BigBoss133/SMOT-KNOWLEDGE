<script>
  let { msg } = $props()
</script>

<div class="flex items-start gap-3 max-w-3xl mx-auto"
  class:flex-row-reverse={msg.role === 'user'}>
  <!-- Avatar -->
  <div
    class="w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0
      {msg.role === 'user'
        ? 'bg-accent-orange/20 text-accent-orange'
        : 'bg-accent-cyan/20 text-accent-cyan'}"
  >
    {msg.role === 'user' ? 'Tu' : '⚡'}
  </div>

  <!-- Content -->
  <div class="flex flex-col gap-2 min-w-0 max-w-[85%]">
    {#if msg.role === 'user'}
      <div class="bg-accent-orange/10 border border-accent-orange/20 rounded-2xl rounded-tr-md px-4 py-2.5">
        <p class="text-sm text-brain-100 leading-relaxed whitespace-pre-wrap">{msg.content}</p>
      </div>
    {:else}
      <div class="bg-brain-800/80 border border-brain-700/30 rounded-2xl rounded-tl-md px-4 py-2.5">
        <p class="text-sm text-brain-100 leading-relaxed whitespace-pre-wrap">{msg.content}</p>
      </div>

      <!-- Sources -->
      {#if msg.sources?.length}
        <div class="flex flex-wrap gap-1.5 px-1">
          {#each msg.sources as source}
            <span class="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full
              bg-accent-cyan/8 text-accent-cyan/70 border border-accent-cyan/15">
              📄 {source.title}
            </span>
          {/each}
        </div>
      {/if}

      <!-- Curiosity -->
      {#if msg.curiosity?.length}
        <div class="px-1 pt-1 border-t border-brain-700/20">
          <p class="text-[11px] text-brain-400 mb-1.5 font-medium">💡 Curiosità</p>
          <div class="flex flex-wrap gap-1.5">
            {#each msg.curiosity as item}
              <span class="inline-flex items-center text-[11px] px-2 py-0.5 rounded-full
                bg-accent-purple/8 text-accent-purple/70 border border-accent-purple/15 cursor-pointer
                hover:bg-accent-purple/15 transition-colors">
                {item}
              </span>
            {/each}
          </div>
        </div>
      {/if}
    {/if}
  </div>
</div>
