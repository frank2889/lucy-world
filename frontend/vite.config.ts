import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  root: '.',
  base: '/static/app/',
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
      '/search': 'http://localhost:5000',
      '/health': 'http://localhost:5000'
    }
  },
  build: {
    outDir: resolve(__dirname, '../static/app'),
    emptyOutDir: true,
    manifest: true,
  },
});
