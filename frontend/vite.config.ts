import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "0.0.0.0", // 允許外部連線 (跟 host: true 意思一樣，但寫 IP 更明確)
    port: 5173,
    allowedHosts: true, // 👈【關鍵修改】這行就是解決 "Blocked request" 的解藥！
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));