import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // This forces network exposure
    port: 5173,      // This locks the port so it doesn't switch to 5174
    strictPort: true, // This makes it crash if 5173 is busy (good for debugging)
    hmr: {
        clientPort: 5173 // Helps preventing WebSocket disconnects
    }
  }
})