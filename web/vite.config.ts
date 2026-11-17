import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

// Relative base works on a GitHub project page and locally. Set VITE_BASE to
// override (for example /edge-vision-lab/).
export default defineConfig({
  base: process.env.VITE_BASE ?? './',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
});
