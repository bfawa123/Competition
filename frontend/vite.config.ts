import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "127.0.0.1",
    proxy: {
      // 当 VITE_API_BASE_URL 为空时，/api 请求会被代理到后端
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      // 封面图片由后端静态服务提供
      "/covers": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
