import type { ResumeItem, OriginalResumeData, ResumeData, Suggestion } from '@/types/resume';

// TODO: Replace with API call
export const MOCK_RESUMES: ResumeItem[] = [
  {
    id: 1,
    name: '軟體工程師履歷_v2',
    updatedAt: '2026-02-12',
    content: `王小明\n前端工程師\n\n聯絡方式\nEmail: xiaoming@example.com\n電話: 0912-345-678\n\n工作經歷\n\n科技公司 A | 前端工程師 | 2022 - 現在\n• 開發維護公司核心產品前端\n• 使用 React + TypeScript 建構現代化 UI\n• 優化效能，提升載入速度 40%\n\n新創公司 B | 初階工程師 | 2020 - 2022\n• 參與多個客戶專案開發\n• 學習並應用前端最佳實踐\n\n技能\nReact, TypeScript, JavaScript, CSS, Git, Node.js`,
  },
  {
    id: 2,
    name: '前端工程師履歷',
    updatedAt: '2026-02-10',
    content: `王小明 - 前端工程師履歷\n\n專精於 React 生態系統的前端開發者，\n具備 3 年以上實戰經驗。\n\n核心技能：\n- React / Next.js\n- TypeScript\n- Tailwind CSS\n- REST API 整合\n\n期望職位：資深前端工程師\n期望薪資：NT$ 70,000 - 90,000`,
  },
  {
    id: 3,
    name: 'AI工程師優化版',
    updatedAt: '2026-02-11',
    content: `王小明 - AI 工程師\n\n專注於機器學習與深度學習應用開發。\n\n核心技能：\n- Python / PyTorch / TensorFlow\n- LLM 應用開發\n- MLOps\n\n期望職位：AI 工程師\n期望薪資：NT$ 80,000 - 120,000`,
  },
];

// TODO: Replace with API call
export const mockOriginalResumeData: OriginalResumeData = {
  name: '王小明',
  phone: '0912-345-678',
  email: 'xiaoming.wang@email.com',
  address: '台北市大安區',
  education: '國立台灣大學 | 資訊工程學系 | 碩士 | 2020 畢業\n國立成功大學 | 資訊工程學系 | 學士 | 2018 畢業',
  experience: `ABC科技公司 | 前端工程師 | 2020 - 至今\n• 負責公司官網與產品頁面開發\n• 使用 React + TypeScript 建構現代化 UI\n• 優化效能，提升載入速度 40%\n\nXYZ新創 | 實習工程師 | 2019 - 2020\n• 參與多個客戶專案開發\n• 使用 Vue.js 開發管理模組`,
  languages: '中文 (母語)、英文 (TOEIC 850)、日文 (N2)',
  skills: 'React, TypeScript, JavaScript, Node.js, Python, Git, SQL, Docker',
  certifications: 'AWS Certified Developer - Associate\nGoogle Cloud Professional Data Engineer',
  portfolio: '個人技術部落格: https://xiaoming.dev\nGitHub: https://github.com/xiaoming',
  autobiography: '我是一名前端工程師，具備 5 年軟體開發經驗。從大學時期便開始接觸程式設計，碩士期間專注於 Web 前端效能優化研究。進入職場後，我持續精進技術能力，從初階工程師成長為能獨立帶領小型團隊的技術骨幹。我熱愛學習新技術，善於團隊合作，期望未來能在技術領導的道路上持續成長。',
  other: '',
};

// TODO: Replace with API call
export const mockResumeData: ResumeData = {
  name: '王小明',
  email: 'xiaoming.wang@email.com',
  phone: '0912-345-678',
  linkedin: 'https://linkedin.com/in/xiaoming',
  github: 'https://github.com/xiaoming',
  professional_summary: '具備 5 年經驗的全端工程師，專注於打造高效能、可擴展的現代 Web 應用。精通 React 生態系統與 Node.js 後端開發，曾帶領 3 人團隊完成多項關鍵專案，優化頁面載入速度達 40%。',
  professional_experience: `ABC科技公司 | 前端工程師 | 2020 - 至今\n• 情境 (S)：公司官網載入速度緩慢，使用者跳出率高達 60%\n• 任務 (T)：負責重構前端架構，提升整體效能\n• 行動 (A)：導入 React 框架，實作程式碼分割與懶載入策略\n• 結果 (R)：頁面載入速度提升 40%，使用者留存率提高 25%\n\nXYZ新創 | 實習工程師 | 2019 - 2020\n• 情境 (S)：後台管理系統功能不足，無法滿足業務需求\n• 任務 (T)：協助開發新功能模組\n• 行動 (A)：使用 Vue.js 開發 3 個管理模組，撰寫單元測試\n• 結果 (R)：系統功能覆蓋率提升 30%，Bug 數量減少 50%`,
  core_skills: 'React, TypeScript, Node.js, Python, Git, SQL',
  projects: `企業級電商平台 | React + Node.js + PostgreSQL\n• 獨立開發完整電商系統，支援 1000+ 日活用戶\n• 實作 CI/CD 流程，部署時間縮短 70%\n\nAI 客服機器人 | Python + FastAPI + OpenAI\n• 整合 GPT API 實現智慧客服，回覆準確率達 92%\n• 日均處理 500+ 筆客戶諮詢`,
  education: '國立台灣大學 | 資訊工程學系 | 碩士 | 2020 畢業\n國立成功大學 | 資訊工程學系 | 學士 | 2018 畢業',
  autobiography: '我是一名前端工程師，具備 5 年軟體開發經驗。從大學時期便開始接觸程式設計，碩士期間專注於 Web 前端效能優化研究。進入職場後，我持續精進技術能力，從初階工程師成長為能獨立帶領小型團隊的技術骨幹。我熱愛學習新技術，善於團隊合作，期望未來能在技術領導的道路上持續成長。',
};

// TODO: Replace with API call
export const mockSuggestions: Suggestion[] = [
  {
    section: '工作經歷',
    original: '負責公司官網與產品頁面開發',
    optimized: '主導 5+ 個企業級 Web 應用開發專案，優化頁面載入速度達 40%，提升使用者留存率 25%',
  },
  {
    section: '技能描述',
    original: 'React, TypeScript, Node.js',
    optimized: '精通 React 生態系統 (Redux, React Query, Next.js)，具備 3 年 TypeScript 實戰經驗，熟悉 Node.js 後端開發',
  },
  {
    section: '專業摘要',
    original: '我是一名前端工程師',
    optimized: '具備 5 年經驗的全端工程師，專注於打造高效能、可擴展的現代 Web 應用，曾帶領 3 人團隊完成多項關鍵專案',
  },
];
