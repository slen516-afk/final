import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
// 1. 引入 React Query 的核心工具
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// 2. 建立一個 QueryClient 實例 (這就像是掌管所有 API 快取的總管)
const queryClient = new QueryClient();

// 3. 用 QueryClientProvider 把 <App /> 包起來，並把總管交給它
createRoot(document.getElementById("root")!).render(
    <QueryClientProvider client={queryClient}>
        <App />
    </QueryClientProvider>
);