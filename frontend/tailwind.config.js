/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#060a14',
          surface: '#0d1321',
          card: '#111827',
          border: '#1e2a42',
          hover: '#1a2744',
          cyan: '#00d4ff',
          'cyan-dim': '#0891b2',
          emerald: '#10b981',
          amber: '#f59e0b',
          red: '#ef4444',
          purple: '#a855f7',
          text: '#e2e8f0',
          'text-dim': '#94a3b8',
          'text-muted': '#64748b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
        'typing': 'typing 1.5s ease-in-out infinite',
        'scan-line': 'scanLine 3s linear infinite',
        'count-up': 'countUp 0.6s ease-out',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 212, 255, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.4)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        slideIn: {
          '0%': { transform: 'translateX(-20px)', opacity: 0 },
          '100%': { transform: 'translateX(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        typing: {
          '0%, 100%': { opacity: 0.3 },
          '50%': { opacity: 1 },
        },
        scanLine: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'cyber': '0 0 15px rgba(0, 212, 255, 0.15)',
        'cyber-lg': '0 0 30px rgba(0, 212, 255, 0.2)',
        'glow-red': '0 0 15px rgba(239, 68, 68, 0.3)',
        'glow-amber': '0 0 15px rgba(245, 158, 11, 0.3)',
        'glow-emerald': '0 0 15px rgba(16, 185, 129, 0.3)',
      },
    },
  },
  plugins: [],
}
