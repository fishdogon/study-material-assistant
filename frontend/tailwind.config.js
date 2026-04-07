/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#111827',
        line: '#E5E7EB',
        panel: '#FFFFFF',
        canvas: '#F5F7FA',
        accent: '#0F766E',
        accentSoft: '#ECFDF5',
      },
      boxShadow: {
        panel: '0 8px 24px rgba(15, 23, 42, 0.06)',
      },
      borderRadius: {
        xl2: '1.25rem',
      },
      fontFamily: {
        sans: ['"Noto Sans SC"', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
