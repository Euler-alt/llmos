/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 自定义颜色
        'kernel-light': '#9cd7d7',
        'kernel-dark': '#3b82f6',
        'heap-light': '#e6f3ff',
        'heap-dark': '#10b981',
        'stack-light': '#fffbe6',
        'stack-dark': '#f59e0b',
        'code-light': '#ccffcc',
        'code-dark': '#ef4444',
      },
      boxShadow: {
        'module': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'module-dark': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.18)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      fontFamily: {
        'mono': ['Menlo', 'Monaco', 'Consolas', '"Liberation Mono"', '"Courier New"', 'monospace'],
      },
    },
  },
  plugins: [],
}