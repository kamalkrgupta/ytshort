import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// base './' so the built video can be served from any folder by tools/record.mjs
export default defineConfig({
  base: './',
  plugins: [react()],
  build: { chunkSizeWarningLimit: 4000 },
});
