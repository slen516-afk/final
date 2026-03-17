# <img src="frontend/public/logo.png" width="40" height="40" valign="middle"> CareerPilot 【職星領航員】
> **您的智慧職涯決策助手 —— 提供從能力評估到職務媒合的一站式智慧支持系統。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![Built with CrewAI](https://img.shields.io/badge/Built%20with-CrewAI-red.svg)](https://www.crewai.com/)

---

## 📖 專案簡介
CareerPilot 旨在解決求職過程中因缺乏量化依據而產生的認知偏差。
透過 AI 驅動的決策體系，本專案建構了完整的職涯支援閉環，涵蓋「能力評估、缺口分析、技能補強、職缺媒合、履歷優化」，預計將申請準備時間大幅縮短 **50%**。

---

## 🏗️ 系統架構
本專案採用分層架構設計，結合 **CrewAI 多代理人系統** 與 **Celery 非同步任務管線**，確保 LLM 分析任務的高效執行。


### 技術棧 (Tech Stack)
* **前端**: React 18 + Vite 5 + TypeScript + Tailwind CSS
* **後端**: Flask API + **CrewAI (Multi-Agent System)**
* **非同步管線**: **Redis** (Broker/Backend)
* **AI 引擎**: 外部AI引擎
* **資料庫**: **Supabase (PostgreSQL)** + **Qdrant (Vector DB)**
* **基礎設施**: Docker + VS Code Dev Containers

---

## ✨ 技術亮點

### ⚙️ 後端與 AI 決策引擎 (CrewAI & MAS)
* **多代理人協作架構 (Multi-Agent System)**：正式版採用 **CrewAI** 框架，透過「任務 Agent」與「品質審核 Agent」雙重檢核機制，確保履歷優化建議具備高度專業性，降低單一 Agent 的邏輯幻覺。
* **六維能力向量模型 (6-D Competency Vector)**：參考 IEEE SWEBOK、SFIA 與 Dreyfus 模型，將軟體工程能力量化為：前端、後端、雲端維運、AI 數據、品質架構、商業思維等六大維度。
* **智慧課程推薦演算法**：
    * **難度對齊**：將用戶匹配度 (0-100) 映射至課程等級 (Beginner/Intermediate/Advanced)。
    * **權重增益**：針對能力缺口進行動態權重補償，確保最迫切需要的技能優先排序。

### 💾 資料流水線與檢索 (Data Pipeline & Vector DB)
* **自動化 E.T.L. 流水線**：
    * **爬蟲引擎**：整合 **Requests / Selenium**，支持 104、Cake 等平台之動態渲染頁面抓取。
    * **資料清整**：利用 **Pandas** 進行多階段清洗，包含文本去噪、薪資標準化及正則表達式 (Regex) 萃取技能元數據。
* **語意相似度檢索 (RAG-based)**：
    * 利用 **Qdrant** 向量資料庫進行語意檢索，採用歐幾里得距離與餘弦相似度 (Cosine Similarity) 混合算法，精準消除求職者與企業間的語意落差。
* **高韌性非同步管線**：透過 **Redis** 實作長時任務解耦。前台提交後 `< 300ms` 即可回傳 Job ID，並具備自動重試 (Backoff) 與死信佇列 (DLQ) 機制。

### 🎨 前端交互體驗
* **數據可視化**：利用 **Recharts** 繪製六維技能雷達圖，直觀呈現能力落點與目標角色的匹配差距。
* **高品質產出**：利用 **html2pdf.js** 提供一鍵匯出客製化優化履歷，解決使用者手動調整格式的痛點。
* **效能優化**：使用 **TanStack Query (v5)** 管理非同步狀態與快取，大幅提升資料載入流暢度。

---

## 🚀 快速開始

### 1. 環境配置
複製 `.env_example` 並重新命名為 `.env`，填入以下必要資訊：
* `SUPABASE_URL` / `SERVICE_ROLE_KEY`
* `QDRANT_HOST` / `API_KEY`
* `OPENAI_API_KEY` (用於 Embedding)
* `REDIS_URL` (Broker 連結路徑)

### 2. 啟動開發環境
1.  啟動 **Docker Desktop**。
2.  使用 VS Code **Dev Containers** 擴充套件，選擇 `Reopen in Container`。
3.  **後端與 Worker 啟動**：
    ```bash
    python main.py             # 啟動 API 入口
    celery -A tasks worker     # 啟動非同步任務處理器
    ```
4.  **前端啟動**：`npm run dev`

---

## 🤝 貢獻指南
1.  Fork 本專案並建立功能分支 (`git checkout -b feature/AmazingFeature`)。
2.  **套件維護**：若有新增套件請同步更新 `requirements.txt` (後端) 或 `package.json` (前端)。
3.  **文件同步**：若涉及資料庫變動，請同步更新資料夾內的 **ERD 說明文件**。

---
Made with ❤️ by CareerPilot Team
