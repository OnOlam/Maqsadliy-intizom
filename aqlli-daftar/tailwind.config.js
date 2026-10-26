/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: '#FAF3E3',
        card: '#FFFCF6',
        ink: '#4A4032',
        'ink-soft': '#93876F',
        sage: '#8FA37E',
        'sage-bg': '#E9EFE1',
        gold: '#C9A55A',
        'gold-bg': '#F3E9D2',
        lavender: '#A597C4',
        'lavender-bg': '#EBE5F5',
        rose: '#C97F6C',
        'rose-bg': '#F5E3DC',
        line: '#EADFC4',
      },
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
        serif: ['Fraunces', 'serif'],
      },
    },
  },
  plugins: [],
}
