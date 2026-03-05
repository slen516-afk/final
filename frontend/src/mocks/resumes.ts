import type { OriginalResumeData, ResumeData, Suggestion } from '@/types/resume';
import { supabase } from '@/utils/supabaseClient';

// TODO: Replace with API call



// 1. 介面新增 sourceType，完美對接你後端的路由分流邏輯
export interface ResumeItem {
  id: number | string;
  name: string;
  updatedAt: string;
  content: string;
  sourceType: 'RESUME' | 'OPTIMIZATION'; // 區分資料來源
}

export const MOCK_RESUMES: ResumeItem[] = [
  {
    id: 1,
    name: '軟體工程師履歷_v2',
    updatedAt: '2026-02-12',
    content: `王小明\n前端工程師...`,
    sourceType: 'RESUME'
  },
  {
    id: 2,
    name: '前端工程師履歷',
    updatedAt: '2026-02-10',
    content: `王小明 - 前端工程師履歷...`,
    sourceType: 'RESUME'
  },
  {
    id: 3,
    name: 'AI工程師優化版',
    updatedAt: '2026-02-11',
    content: `王小明 - AI 工程師...`,
    sourceType: 'OPTIMIZATION'
  },
];

export const getResumes = async (): Promise<ResumeItem[]> => {
  try {
    // 2. 使用 Promise.all 同時發送兩個請求
    const [resumeResponse, optimizationResponse] = await Promise.all([
      supabase
        .from('resume')
        .select('resume_id, resume_name, updated_at')
        .eq('resume_id', 1), // 👉 只抓 resume_id = 1 的資料

      supabase
        .from('resume_optimization')
        .select('optimization_id, resume_name, created_at')
        .eq('resume_id', 1) // 👉 只抓 optimization_id = 1 的資料
    ]);

    // 檢查是否有報錯
    if (resumeResponse.error) throw resumeResponse.error;
    if (optimizationResponse.error) throw optimizationResponse.error;

    // ✨ 順手加的小工具：把 2026-03-03T06:42:10+00:00 變成乾淨的 2026-03-03 06:42
    const formatDate = (dateString: string) => {
      if (!dateString) return '';
      return dateString.replace('T', ' ').substring(0, 16);
    };

    // 3. 處理「原始履歷」資料，並對應正確的欄位名稱
    const standardResumes: ResumeItem[] = (resumeResponse.data || []).map((item: any) => ({
      id: item.resume_id,                 // 對應表裡的 resume_id
      name: item.resume_name || '未命名履歷', // 對應表裡的 resume_name (加個防呆，如果沒填字就顯示預設)
      updatedAt: formatDate(item.updated_at), // 使用上面的日期格式化工具
      content: '',                        // ⚠️ 你這次沒有 select 內容，所以先塞空字串給它
      sourceType: 'RESUME'
    }));

    // 4. 處理「優化版履歷」資料，並對應正確的欄位名稱
    const optimizedResumes: ResumeItem[] = (optimizationResponse.data || []).map((item: any) => ({
      id: item.optimization_id,           // 對應表裡的 optimization_id
      name: item.resume_name || '未命名履歷', // 對應表裡的 resume_name
      updatedAt: formatDate(item.created_at), // 注意：這張表你是用 created_at
      content: '',                        // ⚠️ 一樣先塞空字串
      sourceType: 'OPTIMIZATION'
    }));

    // 5. 將兩個陣列合併在一起
    const combinedResumes = [...standardResumes, ...optimizedResumes];

    // 6. 在前端進行排序：依照時間由新到舊
    combinedResumes.sort((a, b) => {
      const timeA = new Date(a.updatedAt).getTime();
      const timeB = new Date(b.updatedAt).getTime();
      return timeB - timeA;
    });

    return combinedResumes;

  } catch (err) {
    console.error('❌ Supabase 雙資料表撈取失敗，切換為假資料:', err);
    return MOCK_RESUMES;
  }
};

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
