import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api/sim": {
        target: "http://localhost:9004",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/sim/, ""),
      },
      "/api/agent": {
        target: "http://localhost:9005",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/agent/, ""),
      },
    },
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
  },
});
