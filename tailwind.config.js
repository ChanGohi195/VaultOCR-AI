/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Obsidian-style dark theme colors
        obsidian: {
          bg: '#1e1e1e',
          sidebar: '#252525',
          border: '#3e3e3e',
          text: '#dcddde',
          accent: '#7f6df2',
          hover: '#2a2a2a'
        }
      }
    },
  },
  plugins: [],
}
