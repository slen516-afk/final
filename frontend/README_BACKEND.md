# 🔗 Backend Integration Guide

> 本文件為後端工程師提供前端對接所需的完整資訊。

---

## 📌 環境變數設定

⚠️ **Lovable 不支援 `.env` 檔案。** 部署後請在 Vite build 時透過環境變數指定後端位址：

```bash
VITE_API_BASE_URL=https://api.example.com vite build
```

前端 API Client 位於 `src/services/apiClient.ts`，會讀取 `import.meta.env.VITE_API_BASE_URL`，若未設定則 fallback 至 `/api`。

---

## 🗂️ 需要串接 API 的頁面一覽

| 優先級 | 頁面路由                          | 功能說明                              | 對應 Service          | 預期 API Endpoint                                                                                                        |
| :----: | --------------------------------- | ------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 🔴 P0  | `/member/center`                  | 個人資料讀取與編輯                    | `memberService.ts`    | `GET/PUT /members/me`                                                                                                    |
| 🔴 P0  | `/member/upload-resume`           | 履歷上傳                              | `resumeService.ts`    | `POST /resumes/upload`                                                                                                   |
| 🔴 P0  | `/auth/register-form`             | 會員註冊                              | —                     | `POST /auth/register`                                                                                                    |
| 🟠 P1  | `/resume/optimize`                | 履歷優化（取得原始 → AI 優化 → 建議） | `resumeService.ts`    | `GET /resumes/:id/original`、`POST /resumes/:id/optimize`、`GET /resumes/:id/suggestions`                                |
| 🟠 P1  | `/member/my-resumes`              | 履歷列表                              | `resumeService.ts`    | `GET /resumes`                                                                                                           |
| 🟠 P1  | `/jobs/skill-search`              | 技能搜尋職缺                          | `jobService.ts`       | `GET /jobs?page=&skills=`                                                                                                |
| 🟠 P1  | `/jobs/recommendations`           | AI 推薦職缺                           | `jobService.ts`       | `GET /jobs?page=`                                                                                                        |
| 🟠 P1  | `/jobs/:id`                       | 職缺詳情 + 求職信生成                 | `jobService.ts`       | `GET /jobs/:id`、`POST /jobs/:id/cover-letter`                                                                           |
| 🟡 P2  | `/analysis/skills`                | 技能雷達圖 + 落差分析 + 學習資源      | `analysisService.ts`  | `GET /analysis/radar`、`GET /analysis/gap`、`GET /analysis/resources`、`GET /analysis/projects`、`GET /analysis/history` |
| 🟡 P2  | `/member/survey/personality`      | 職涯偏好問卷提交                      | —                     | `POST /survey/personality`                                                                                               |
| 🟢 P3  | `/` (首頁)                        | 統計數據 + 最新消息                   | `homepageService.ts`  | `GET /homepage/stats`、`GET /homepage/news`                                                                              |
| 🟢 P3  | `/member/career-path`             | 職涯路徑圖                            | —                     | `GET /career/path`                                                                                                       |

> ℹ️ `/member/survey/personality-test`（人格特質問卷）的計分與結果判定完全在前端完成（見 `src/data/personalityScoring.ts`），不需後端 API。

---

## 🏗️ 前端架構概覽

```
src/
├── services/          # API 服務層（目前回傳 mock 資料）
│   ├── apiClient.ts   # 統一 HTTP Client（fetch-based）
│   ├── resumeService.ts
│   ├── jobService.ts
│   ├── memberService.ts
│   ├── analysisService.ts
│   └── homepageService.ts
├── mocks/             # 模擬資料（對接後可移除）
├── types/             # TypeScript 介面定義
│   ├── resume.ts
│   ├── job.ts
│   ├── member.ts
│   ├── analysis.ts
│   └── homepage.ts
├── data/              # 前端靜態資料與計算邏輯
│   ├── personalityScoring.ts    # 人格特質問卷計分引擎（純前端）
│   ├── archetypeDetails.ts      # 人格原型詳細資訊
│   ├── personalityTestQuestions.ts
│   ├── surveyQuestions.ts
│   ├── careerLadderTemplates.ts
│   └── taiwanAddresses.ts
└── contexts/          # React Context（全局狀態）
```

### 對接方式

每個 `service` 檔案中的函式目前以 `mockDelay()` + mock data 模擬回傳。只需將其替換為 `apiClient.get/post/put/delete` 即可完成對接，例如：

```ts
// Before (mock)
export async function getResumes(): Promise<ResumeItem[]> {
  await mockDelay();
  return MOCK_RESUMES;
}

// After (real API)
export async function getResumes(): Promise<ResumeItem[]> {
  return apiClient.get<ResumeItem[]>('/resumes');
}
```

---

## 🎨 配色規範（大地色系 Earth Tones）

前端使用 CSS 變數 + Tailwind 語義化 Token，後端回傳的資料**不需包含任何樣式資訊**。

| 用途                   | 色碼      | CSS Token            |
| ---------------------- | --------- | -------------------- |
| 頁面背景（米杏色）     | `#fbf1e8` | `--background`       |
| 主標題                 | `#000000` | `--foreground`       |
| 品牌重點色（紅銅色）   | `#8d4903` | `--primary`          |
| 輔助文字（深棕色）     | `#675143` | `--muted-foreground` |
| 導覽列底色（暖棕色）   | `#966949` | `--header-bg`        |
| 頁尾底色（深褐色）     | `#502D03` | `--footer-bg`        |
| 卡片背景               | `#ffffff` | `--card`             |
| 次級區塊背景（奶油色） | `#FFFBF5` | `--news-bg`          |

### UI 組件邏輯

- **所有彈窗、Modal、Tooltip、輸入框** → 強制純白底 (`#ffffff`) + 暖色調陰影
- **按鈕** → 品牌紅銅色 (`--primary`) 為主色
- **圖標** → 淺色背景用 `#8d4903`，深色背景反轉為 `#dabea8`
- **字型** → `Noto Sans TC` + `Inter`
- **圓角** → 全局 `0.75rem`

---

## 📋 資料結構參考

所有 TypeScript 介面定義於 `src/types/`，後端 API 回傳格式請盡量與這些介面一致，以減少前端轉換成本。

關鍵介面：

- `UserProfile` → `src/types/member.ts`
- `ResumeItem`, `ResumeData`, `Suggestion` → `src/types/resume.ts`
- `JobData`, `JobDetailData`, `JobCategory` → `src/types/job.ts`
- `RadarTemplate`, `GapAnalysisData`, `LearningResource` → `src/types/analysis.ts`
- `HeroStat`, `NewsItem` → `src/types/homepage.ts`

---

## 🔐 門禁系統（Route Protection）

前端使用 `ProtectedRoute` 組件控制頁面存取，依據以下狀態旗標：

- `isLoggedIn` — 登入狀態
- `isResumeUploaded` — 履歷上傳狀態
- `isPersonalityQuizDone` — 職涯偏好問卷狀態
- `isPersonalityTestDone` — 人格特質問卷狀態

各頁面所需旗標：

| 頁面                    | 需要旗標                                                                      |
| ----------------------- | ----------------------------------------------------------------------------- |
| `/member/center`        | `isLoggedIn`                                                                  |
| `/jobs/skill-search`    | `isLoggedIn`                                                                  |
| `/jobs/recommendations` | `isLoggedIn`, `isResumeUploaded`, `isPersonalityQuizDone`, `isPersonalityTestDone` |
| `/resume/optimize`      | `isLoggedIn`, `isResumeUploaded`, `isPersonalityQuizDone`, `isPersonalityTestDone` |
| `/analysis/skills`      | `isLoggedIn`, `isResumeUploaded`, `isPersonalityQuizDone`, `isPersonalityTestDone` |

---

## ✅ 後端對接 Checklist

- [ ] 確認 CORS 允許前端 domain
- [ ] 實作認證機制（JWT / Session），前端 `apiClient` 已預留 headers 注入點
- [ ] 依照 P0 → P3 優先級逐步實作 API
- [ ] API 回傳格式與 `src/types/` 介面一致
- [ ] 錯誤回傳統一為 `{ message: string; code?: string }` 格式
