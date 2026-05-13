<script>
  import { settings, clearChat } from '../stores/app.js'

  function update(key, value) {
    settings.update(s => ({ ...s, [key]: value }))
  }
</script>

<div class="h-full flex flex-col p-4 space-y-4 overflow-y-auto">
  <h2 class="text-sm font-semibold text-brain-100">⚙️ Impostazioni</h2>

  <section class="space-y-2">
    <label class="block">
      <span class="text-xs text-brain-300 font-medium">Modello LLM</span>
      <select
        value={$settings.model}
        onchange={(e) => update('model', e.target.value)}
        class="w-full mt-1 px-3 py-2 rounded-lg text-sm
          bg-brain-800/80 border border-brain-600/50 text-brain-100
          focus:outline-none focus:border-accent-cyan/40"
      >
        <option value="gemma3:4b">Gemma3 4B (default)</option>
        <option value="gemma4:e2b">Gemma4 e2b (MoE)</option>
        <option value="qwen2.5-coder:7b">Qwen2.5-Coder 7B</option>
        <option value="llama3.1:8b">Llama 3.1 8B</option>
        <option value="deepseek-coder:6.7b">DeepSeek Coder 6.7B</option>
      </select>
    </label>
  </section>

  <section class="space-y-3">
    <label class="flex items-center justify-between py-2 px-3 rounded-lg bg-brain-800/30 border border-brain-700/20">
      <div>
        <span class="text-sm text-brain-100">🧠 Curiosità</span>
        <p class="text-[11px] text-brain-400">Ricerca autonoma di nuovi pattern</p>
      </div>
      <button
        aria-label="Attiva curiosità"
        onclick={() => update('curiosityEnabled', !$settings.curiosityEnabled)}
        class="relative w-10 h-5 rounded-full transition-colors duration-200
          {$settings.curiosityEnabled ? 'bg-accent-cyan' : 'bg-brain-600'}"
      >
        <span class="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform duration-200
          {$settings.curiosityEnabled ? 'translate-x-5' : 'translate-x-0.5'}"></span>
      </button>
    </label>

    <label class="flex items-center justify-between py-2 px-3 rounded-lg bg-brain-800/30 border border-brain-700/20">
      <div>
        <span class="text-sm text-brain-100">⊞ Terminale</span>
        <p class="text-[11px] text-brain-400">Mostra log in tempo reale</p>
      </div>
      <button
        aria-label="Mostra terminale"
        onclick={() => update('terminalVisible', !$settings.terminalVisible)}
        class="relative w-10 h-5 rounded-full transition-colors duration-200
          {$settings.terminalVisible ? 'bg-accent-cyan' : 'bg-brain-600'}"
      >
        <span class="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform duration-200
          {$settings.terminalVisible ? 'translate-x-5' : 'translate-x-0.5'}"></span>
      </button>
    </label>

    <button onclick={clearChat}
      class="w-full text-xs text-center py-2 rounded-lg text-red-400 hover:bg-red-400/10 border border-red-400/20 transition-colors">
      Cancella cronologia chat
    </button>
  </section>

  <section class="border-t border-brain-700/20 pt-3 space-y-1 text-[11px] text-brain-500 font-mono">
    <p>GPU: NVIDIA RTX 4060 Ti (8GB)</p>
    <p>Modello: {$settings.model}</p>
    <p>Stato WS: {$settings.wsConnected ? 'connesso' : 'disconnesso'}</p>
    <p>SMOT-KNOWLEDGE v0.1.0</p>
  </section>
</div>
