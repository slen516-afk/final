// Six career path templates based on Gemini career ladder data
// Each has 5 levels with title & responsibilities

export interface CareerLevel {
  level: number;
  title: string;
  duties: string[];
}

export interface CareerTemplate {
  id: string;
  name: string;
  mascot: string;
  levels: CareerLevel[];
}

export const careerTemplates: Record<string, CareerTemplate> = {
  frontend: {
    id: 'frontend',
    name: '前端工程師',
    mascot: '/mascots/frontend.png',
    levels: [
      { level: 1, title: '初級前端工程師', duties: ['UI 元件開發', '修復 Bug', '基礎 HTML/CSS/JS'] },
      { level: 2, title: '中級前端工程師', duties: ['熟悉框架 (React/Vue)', '效能優化', '模組化開發'] },
      { level: 3, title: '資深前端工程師', duties: ['大型專案前端架構', '制定開發規範', '前端自動化工作流'] },
      { level: 4, title: '前端架構師', duties: ['跨端技術選型', '微前端架構', 'BFF/Node.js 優化'] },
      { level: 5, title: '前端技術總監', duties: ['技術版圖規劃', '使用者體驗策略', '研發團隊效能提升'] },
    ],
  },
  backend: {
    id: 'backend',
    name: '後端工程師',
    mascot: '/mascots/backend.png',
    levels: [
      { level: 1, title: '初級後端工程師', duties: ['API 開發', 'CRUD 實作', '基礎資料庫查詢'] },
      { level: 2, title: '中級後端工程師', duties: ['系統模組化設計', '資料庫優化', '快取機制應用'] },
      { level: 3, title: '資深後端工程師', duties: ['分散式系統設計', '微服務架構', '訊息佇列處理'] },
      { level: 4, title: '系統架構師', duties: ['高併發系統規劃', '資料治理', '安全性架構設計'] },
      { level: 5, title: '技術長 (CTO)', duties: ['技術棧決策', '資安風險管理', '產品技術轉型'] },
    ],
  },
  fullstack: {
    id: 'fullstack',
    name: '全端工程師',
    mascot: '/mascots/fullstack.png',
    levels: [
      { level: 1, title: '初級全端工程師', duties: ['獨立完成 Web 功能', '前端頁面 + API', '基礎資料庫'] },
      { level: 2, title: '中級全端工程師', duties: ['掌握主流框架', '獨立維運小型專案', '前後端整合'] },
      { level: 3, title: '資深全端工程師', duties: ['全棧效能優化', '設計通用 API 規範', '跨層架構設計'] },
      { level: 4, title: '產品工程師', duties: ['結合技術與商務邏輯', '快速原型開發 (MVP)', '產品視角出發'] },
      { level: 5, title: '技術負責人', duties: ['帶領全棧團隊', '平衡速度與品質', '技術路線規劃'] },
    ],
  },
  data: {
    id: 'data',
    name: '資料科學家',
    mascot: '/mascots/data.png',
    levels: [
      { level: 1, title: '資料分析師', duties: ['數據清洗 (ETL)', '視覺化報表', '基礎 SQL 提取'] },
      { level: 2, title: '資深資料分析師', duties: ['定義 KPIs', 'A/B Testing 分析', '解釋業務問題'] },
      { level: 3, title: '資料科學家', duties: ['特徵工程', '機器學習模型開發', '預測模型建模'] },
      { level: 4, title: '資深資料科學家', duties: ['複雜演算法設計', '推薦系統架構', '解決業務難點'] },
      { level: 5, title: '資料長 (CDO)', duties: ['數據戰略制定', '數據驅動文化', '隱私合規管理'] },
    ],
  },
  ai: {
    id: 'ai',
    name: 'AI/演算法工程師',
    mascot: '/mascots/ai.png',
    levels: [
      { level: 1, title: '助理演算法工程師', duties: ['資料預處理', '模型訓練與調整', '文獻閱讀'] },
      { level: 2, title: 'AI/演算法工程師', duties: ['模型優化', '領域演算法開發', 'CV/NLP/Speech'] },
      { level: 3, title: '資深演算法工程師', duties: ['大規模推論效率', '自研核心算法', '解決落地痛點'] },
      { level: 4, title: '首席 AI 工程師', duties: ['前瞻技術研究', '引領技術突破', 'SOTA 研究'] },
      { level: 5, title: 'AI 技術科學家', duties: ['AI 轉化產品力', '決定技術天花板', '跨領域創新'] },
    ],
  },
  devops: {
    id: 'devops',
    name: 'DevOps/SRE 工程師',
    mascot: '/mascots/devops.png',
    levels: [
      { level: 1, title: '初級 DevOps 工程師', duties: ['伺服器環境配置', 'CI/CD 流水線維護', '基礎監控報警'] },
      { level: 2, title: 'DevOps/SRE 工程師', duties: ['容器化佈署 (K8s)', '基礎設施即程式碼', '災難復原演練'] },
      { level: 3, title: '資深 SRE 工程師', duties: ['穩定性工程', '大規模雲端優化', '自動化故障自癒'] },
      { level: 4, title: '雲端架構師', duties: ['多雲架構策略', '雲端成本控制', '安全性架構'] },
      { level: 5, title: '基礎建設負責人', duties: ['雲端戰略規劃', '研發效率工具化', '組織基礎設施'] },
    ],
  },
};

// Mock: 3 resume experiences (including career changer scenario)
export const mockResumeExperiences = [
  {
    title: '行政人員',
    company: '大同企業',
    period: '2018-2020',
    duties: ['文書處理與歸檔', '會議安排與紀錄', '行政流程優化'],
  },
  {
    title: '專案助理',
    company: 'ABC 科技',
    period: '2020-2022',
    duties: ['專案進度追蹤', '跨部門溝通協調', '需求文件整理'],
  },
  {
    title: '轉職學習中',
    company: '自學 / 培訓班',
    period: '2022-2024',
    duties: ['線上課程學習', '個人作品集開發', '參加技術社群'],
  },
];

// Mock: user's target career type
export const mockTargetCareer = 'frontend';
