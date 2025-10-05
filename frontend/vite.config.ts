import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { fileURLToPath } from 'url';

const baseDir = fileURLToPath(new URL('.', import.meta.url));

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
    outDir: resolve(baseDir, '../static/app'),
    emptyOutDir: true,
    manifest: true,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: resolve(baseDir, './vitest.setup.ts'),
    clearMocks: true
  },
});
