import { defineConfig } from 'vite'
import {fileURLToPath, URL} from 'url'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias:[{
      find: '@',
      replacement: fileURLToPath(new URL('./src', import.meta.url))
    }]
  },
  server:{
    host:'0.0.0.0',
    allowedHosts:['all'],
    proxy:{
      '/api':{
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/auth':{
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/socket.io':{
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true,
      },
    }
  }
})