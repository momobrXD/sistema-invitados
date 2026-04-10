/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        azul: { DEFAULT: '#1a3a5c', med: '#1e4f80', claro: '#2e6faf', hover: '#e8f1fa' },
        dorado: { DEFAULT: '#c9973a', claro: '#f5e6c8', dark: '#a07828' },
        verde: { DEFAULT: '#2a7d55', claro: '#e8f5ee' },
        crema: '#faf8f5',
      },
      fontFamily: {
        serif: ['Lora', 'Georgia', 'serif'],
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '20px',
        btn: '14px',
      },
    },
  },
  plugins: [],
}
