/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{svelte,js,ts}'],
  theme: {
    extend: {
      colors: {
        brain: {
          50: '#e8e8f0',
          100: '#c4c4d6',
          200: '#a0a0bc',
          300: '#7c7ca2',
          400: '#585888',
          500: '#3a3a5c',
          600: '#2a2a42',
          700: '#1a1a2e',
          800: '#0f0f1e',
          900: '#0a0a12',
        },
        accent: {
          cyan: '#00d4ff',
          orange: '#ff6b35',
          emerald: '#10b981',
          purple: '#a855f7',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'slide-up': 'slide-up 0.3s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
        'typing': 'typing 1s steps(4) infinite',
        'brain-pulse': 'brain-pulse 3s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'typing': {
          '0%': { content: "''" },
          '25%': { content: "'.'" },
          '50%': { content: "'..'" },
          '75%': { content: "'...'" },
        },
        'brain-pulse': {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(0, 212, 255, 0.4)' },
          '50%': { boxShadow: '0 0 20px 5px rgba(0, 212, 255, 0.1)' },
        },
      },
    },
  },
  plugins: [],
}
