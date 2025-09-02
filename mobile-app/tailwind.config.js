/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,jsx,ts,tsx}', './components/**/*.{js,jsx,ts,tsx}'],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      colors: {
        // Sri Lankan primary colors
        saffron: {
          50: '#FFF4E6',
          100: '#FFE8CC',
          200: '#FFD199',
          300: '#FFBA66',
          400: '#FFA333',
          500: '#FF6B35', // Primary saffron
          600: '#E55A2B',
          700: '#CC4921',
          800: '#B33817',
          900: '#99270D',
        },
        slGreen: {
          50: '#E8F5E8',
          100: '#C8E6C8',
          200: '#91D291',
          300: '#5ABE5A',
          400: '#23AA23',
          500: '#00A86B', // Sri Lankan flag green
          600: '#008A57',
          700: '#006C43',
          800: '#004E2F',
          900: '#00301B',
        },
        slMaroon: {
          50: '#F5E6E6',
          100: '#E6C7C7',
          200: '#CC8F8F',
          300: '#B35757',
          400: '#991F1F',
          500: '#8B0000', // Sri Lankan maroon
          600: '#700000',
          700: '#560000',
          800: '#3D0000',
          900: '#230000',
        },
        slGold: {
          50: '#FFFEF7',
          100: '#FFFCEB',
          200: '#FFF8D1',
          300: '#FFF3B8',
          400: '#FFEE9E',
          500: '#FFD700', // Sri Lankan gold
          600: '#E6C200',
          700: '#CCAD00',
          800: '#B39900',
          900: '#998400',
        },
        // Traditional colors
        teaGreen: '#87A96B',
        cinnamon: '#D2691E',
        sapphire: '#0F52BA',
        coconut: '#8B4513',
        spice: '#CC5500',
      },
      fontFamily: {
        'sinhala': ['NotoSansSinhala', 'system-ui', 'sans-serif'],
        'tamil': ['NotoSansTamil', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'sri': '0 4px 6px -1px rgba(255, 107, 53, 0.1), 0 2px 4px -1px rgba(255, 107, 53, 0.06)',
      },
    },
  },
  plugins: [],
};
