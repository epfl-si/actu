import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({

  root: path.resolve(__dirname, './src'),

  // Must match the `STATIC_URL` Django setting. Every asset URL generated
  // in the final HTML will be prefixed with this value.
  base: '/static/',

  build: {
    // Absolute path for compiled assets. This directory is listed in
    // Django's `STATICFILES_DIRS` so that `collectstatic` picks it up.
    outDir: path.resolve(__dirname, './src/static'),

    // Keep existing files in outDir (e.g. Django static files).
    emptyOutDir: false,

    // Required by django-vite. The manifest maps entry names to hashed
    // output filenames so templates can resolve the correct URLs.
    manifest: 'manifest.json',

    rollupOptions: {
      input: {
        homepages: './assets/components/homepages/index.js',
        actu: './assets/entrypoint.scss',
        manage_users: './assets/pages/manage-users-homepages/manage_users.js',
      },
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'css/[name][extname]'
          }
        },
      },
    },
  },

  css: {
    devSourcemap: true,

    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
        loadPaths: [path.resolve(__dirname, './src/assets')],
      },
    },
  },

  server: {
    host: '0.0.0.0',
  },
})
