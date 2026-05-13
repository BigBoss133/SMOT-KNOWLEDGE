<script>
  import { settings } from '../stores/app.js'

  let s = $state({})

  $effect(() => {
    s = $settings
  })

  function update(key, value) {
    settings.update(st => ({ ...st, [key]: value }))
  }
</script>

<div class="h-full flex flex-col p-4 space-y-4 overflow-y-auto">
  <h2 class="text-sm font-semibold text-brain-100">⚙️ Impostazioni</h2>

  <!-- Modello -->
  <section class="space-y-2">
    <label class="block">
      <span class="text-xs text-brain-300 font-medium">Modello LLM</span>
      <select
        value={s.model}
        onchange={(e) => update('model', e.target.value)}
        class="w-full mt-1 px-3 py-2 rounded-lg text-sm
          bg-brain-800/80 border border-brain-600/50 text-brain-100
          focus:outline-none focus:border-accent-cyan/40"
      >
        <option value="qwen3:7b">Qwen3 7B (consigliato)</option>
        <option value="gemma4:e2b">Gemma4 e2b</option>
        <option value="deepseek-r1:7b">DeepSeek-R1 7B</option>
        <option value="gemma3:4b">Gemma3 4B</option>
        <option value="qwen2.5-coder:7b">Qwen2.5-Coder 7B</option>
      </select>
    </label>
  </section>

  <!-- Context Budget -->
  <section class="space-y-2">
    <span class="text-xs text-brain-300 font-medium">Budget Contesto (COAST)</span>
    <div class="space-y-1.5">
      {#each [
        { key: 'instruction', label: 'Istruzioni', color: 'bg-accent-cyan' },
        { key: 'kb', label: 'Knowledge Base', color: 'bg-accent-purple' },
        { key: 'web', label: 'Web Search', color: 'bg-accent-orange' },
        { key: 'academic', label: 'Fonti Accademiche', color: 'bg-accent-emerald' },
        { key: 'reasoning', label: 'Ragionamento', color: 'bg-yellow-500' },
        { key: 'output', label: 'Output', color: 'bg-blue-400' },
      ] as item}
        <div class="flex items-center gap-3">
          <span class="text-xs text-brain-400 w-28 shrink-0">{item.label}</span>
          <div class="flex-1 h-2 rounded-full bg-brain-700/50 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-300 {item.color}"
              style="width: {s.contextBudget[item.key]}%"
            ></div>
          </div>
          <span class="text-xs text-brain-400 font-mono w-8 text-right">{s.contextBudget[item.key]}%</span>
        </div>
      {/each}
    </div>
  </section>

  <!-- Opzioni -->
  <section class="space-y-3">
    <label class="flex items-center justify-between py-2 px-3 rounded-lg bg-brain-800/30 border border-brain-700/20">
      <div>
        <span class="text-sm text-brain-100">🧠 Curiosità</span>
        <p class="text-[11px] text-brain-400">Ricerca autonoma di nuovi pattern</p>
      </div>
      <button
        aria-label="Attiva curiosità"
        onclick={() => update('curiosityEnabled', !s.curiosityEnabled)}
        class="relative w-10 h-5 rounded-full transition-colors duration-200
          {s.curiosityEnabled ? 'bg-accent-cyan' : 'bg-brain-600'}"
      >
        <span
          class="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform duration-200
            {s.curiosityEnabled ? 'translate-x-5' : 'translate-x-0.5'}"
        ></span>
      </button>
    </label>

    <label class="flex items-center justify-between py-2 px-3 rounded-lg bg-brain-800/30 border border-brain-700/20">
      <div>
        <span class="text-sm text-brain-100">⊞ Terminale</span>
        <p class="text-[11px] text-brain-400">Mostra log in tempo reale</p>
      </div>
      <button
        aria-label="Mostra terminale"
        onclick={() => update('terminalVisible', !s.terminalVisible)}
        class="relative w-10 h-5 rounded-full transition-colors duration-200
          {s.terminalVisible ? 'bg-accent-cyan' : 'bg-brain-600'}"
      >
        <span
          class="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform duration-200
            {s.terminalVisible ? 'translate-x-5' : 'translate-x-0.5'}"
        ></span>
      </button>
    </label>
  </section>

  <!-- Info sistema -->
  <section class="border-t border-brain-700/20 pt-3 space-y-1 text-[11px] text-brain-500 font-mono">
    <p>GPU: NVIDIA RTX 4060 Ti (8GB)</p>
    <p>Modello attivo: {s.model}</p>
    <p>SMOT-KNOWLEDGE v0.1.0</p>
  </section>
</div>
