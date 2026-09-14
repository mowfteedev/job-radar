import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://mowfteedev.github.io',
  base: process.env.GITHUB_ACTIONS ? '/job-radar' : '/',
  vite: {
    plugins: [tailwindcss()],
  },
});
