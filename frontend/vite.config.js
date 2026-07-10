import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  define: {
    __GOOGLE_MAPS_API_KEY__: JSON.stringify(process.env.VITE_GOOGLE_MAPS_API_KEY || ''),
  },
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        login: resolve(__dirname, 'pages/login.html'),
        signup: resolve(__dirname, 'pages/signup.html'),
        forgotPassword: resolve(__dirname, 'pages/forgot-password.html'),
        dashboard: resolve(__dirname, 'pages/dashboard.html'),
        map: resolve(__dirname, 'pages/map.html'),
        volunteer: resolve(__dirname, 'pages/volunteer.html'),
        sustainability: resolve(__dirname, 'pages/sustainability.html'),
        adminAnnouncements: resolve(__dirname, 'pages/admin-announcements.html'),
        adminGates: resolve(__dirname, 'pages/admin-gates.html'),
        adminSecurity: resolve(__dirname, 'pages/admin-security.html')
      }
    }
  }
});
