// postcss.config.mjs
import tailwindcssPostcss from '@tailwindcss/postcss';
import autoprefixer from 'autoprefixer';

export default {
  plugins: {
    '@tailwindcss/postcss': {}, // Or simply tailwindcssPostcss: {}
    autoprefixer: {},
  },
};