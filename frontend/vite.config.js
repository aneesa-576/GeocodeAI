import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite configuration for GeoCode AI React Application
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
