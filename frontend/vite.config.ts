import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: true, // 這是關鍵！允許從 Docker 外部 (你的本機瀏覽器) 訪問
    port: 5173,
    // 如果你想設定代理，避免 CORS 問題，也可以在這裡加 proxy (但我們先用 flask-cors 解決了)
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
