import type {
  RadarTemplate,
  GapAnalysisData,
  AnalysisHistoryItem,
  LearningResource,
  SideProject,
} from '@/types/analysis';

// TODO: Replace with API call
export const radarTemplates: Record<string, RadarTemplate> = {
  frontend: {
    label: '前端工程師',
    mascot: '/mascots/frontend.png',
    data: [
      { dimension: 'HTML/CSS', user: 90, target: 95 },
      { dimension: 'JavaScript', user: 85, target: 90 },
      { dimension: '框架 (React/Vue)', user: 80, target: 90 },
      { dimension: '效能優化', user: 60, target: 80 },
      { dimension: '測試與品質', user: 55, target: 75 },
      { dimension: 'UI/UX 設計感', user: 70, target: 80 },
    ],
  },
  backend: {
    label: '後端工程師',
    mascot: '/mascots/backend.png',
    data: [
      { dimension: 'API 設計', user: 75, target: 90 },
      { dimension: '資料庫', user: 65, target: 85 },
      { dimension: '系統架構', user: 50, target: 80 },
      { dimension: '安全性', user: 55, target: 75 },
      { dimension: '快取與效能', user: 45, target: 70 },
      { dimension: '運維部署', user: 40, target: 65 },
    ],
  },
  fullstack: {
    label: '全端工程師',
    mascot: '/mascots/fullstack.png',
    data: [
      { dimension: '前端開發', user: 85, target: 90 },
      { dimension: '後端開發', user: 65, target: 80 },
      { dimension: '運維部署', user: 50, target: 70 },
      { dimension: 'AI 與數據', user: 40, target: 60 },
      { dimension: '工程品質', user: 75, target: 85 },
      { dimension: '軟實力', user: 80, target: 75 },
    ],
  },
  data: {
    label: '資料科學家',
    mascot: '/mascots/data.png',
    data: [
      { dimension: '統計學', user: 70, target: 85 },
      { dimension: '機器學習', user: 55, target: 80 },
      { dimension: '資料工程', user: 60, target: 75 },
      { dimension: '視覺化', user: 75, target: 80 },
      { dimension: 'SQL/NoSQL', user: 65, target: 80 },
      { dimension: '商業洞察', user: 50, target: 70 },
    ],
  },
  ai: {
    label: 'AI/演算法工程師',
    mascot: '/mascots/ai.png',
    data: [
      { dimension: '深度學習', user: 60, target: 85 },
      { dimension: 'NLP/CV', user: 50, target: 80 },
      { dimension: '模型部署', user: 40, target: 70 },
      { dimension: '數學基礎', user: 70, target: 85 },
      { dimension: '論文閱讀', user: 55, target: 75 },
      { dimension: '資料處理', user: 65, target: 80 },
    ],
  },
  devops: {
    label: 'DevOps/SRE',
    mascot: '/mascots/devops.png',
    data: [
      { dimension: 'CI/CD', user: 45, target: 80 },
      { dimension: '容器化 (K8s)', user: 50, target: 85 },
      { dimension: '雲端服務', user: 55, target: 80 },
      { dimension: '監控告警', user: 40, target: 75 },
      { dimension: '基礎設施即程式碼', user: 35, target: 70 },
      { dimension: '安全合規', user: 45, target: 65 },
    ],
  },
};

// TODO: Replace with API call
export const gapAnalysis: GapAnalysisData = {
  selfAssessment: '中階工程師',
  aiAssessment: '資深工程師',
  assessmentExplanation: '根據您的履歷經歷、技能自評以及性格測驗結果，系統綜合判斷您在專案管理、跨團隊溝通及核心技術深度方面已達到資深工程師的基準線。然而，在運維部署與系統架構設計方面仍有成長空間，建議持續累積大型專案經驗以鞏固此評級。',
  matchPercentage: 78,
  targetPosition: '全端資深工程師',
  cognitiveBias: '您對運維部署的能力略有高估，建議多參與實際部署專案來累積經驗。',
  summary: '您的後端技術已達標，但在運維部署上仍有 20% 的成長空間，是晉升資深工程師的關鍵。',
  gaps: [
    { skill: '容器化技術', current: 50, target: 70, priority: '高' },
    { skill: 'CI/CD 流程', current: 45, target: 75, priority: '高' },
    { skill: '雲端架構', current: 55, target: 80, priority: '中' },
    { skill: '資料庫優化', current: 60, target: 75, priority: '中' },
  ],
};

// TODO: Replace with API call
export const learningResources: LearningResource[] = [
  {
    title: 'Docker & Kubernetes 實戰課程',
    description: '從零開始學習容器化技術，涵蓋 Docker 基礎到 K8s 集群管理',
    tags: ['DevOps', '容器化', '熱門'],
    link: '#',
  },
  {
    title: 'AWS 雲端架構師認證指南',
    description: '系統性學習雲端服務，準備 AWS SAA 認證考試',
    tags: ['雲端', 'AWS', '認證'],
    link: '#',
  },
  {
    title: '高效能 PostgreSQL 優化技巧',
    description: '深入了解資料庫索引設計與查詢優化策略',
    tags: ['資料庫', 'SQL', '進階'],
    link: '#',
  },
  {
    title: 'GitHub Actions CI/CD 完整教學',
    description: '建立自動化測試與部署流程，提升開發效率',
    tags: ['CI/CD', 'DevOps', '實用'],
    link: '#',
  },
];

// TODO: Replace with API call
export const sideProjects: SideProject[] = [
  {
    name: '個人 DevOps 實驗室',
    technologies: ['Docker', 'K8s', 'GitHub Actions'],
    highlights: '建立完整的 CI/CD 流程，從程式碼提交到自動部署',
    difficulty: 4,
  },
  {
    name: '微服務電商平台',
    technologies: ['Node.js', 'PostgreSQL', 'Redis'],
    highlights: '實作分散式系統架構，練習服務間通訊與資料一致性',
    difficulty: 5,
  },
  {
    name: '即時數據儀表板',
    technologies: ['React', 'WebSocket', 'Chart.js'],
    highlights: '結合前端視覺化與即時數據串流，強化全端技能',
    difficulty: 3,
  },
  {
    name: '智慧日誌分析系統',
    technologies: ['Python', 'Elasticsearch', 'Kibana'],
    highlights: '學習日誌收集與分析，提升運維能力',
    difficulty: 4,
  },
];

// TODO: Replace with API call
export const analysisHistory: AnalysisHistoryItem[] = [
  {
    id: 1,
    date: '2024-01-15',
    title: '職能分析報告',
    summary: '根據您的履歷與職涯問卷，系統為您進行了全面的職能評估。',
    content: {
      strengths: ['前端開發能力優秀', 'React 框架熟練度高', '具備良好溝通能力'],
      improvements: ['可加強後端技術學習', '建議考取雲端相關證照'],
      recommendations: ['建議朝資深工程師發展', '可考慮擴展技術棧至 Node.js'],
    },
  },
  {
    id: 2,
    date: '2024-01-10',
    title: '履歷優化建議',
    summary: '針對您上傳的履歷進行深度分析，提供具體優化方向。',
    content: {
      strengths: ['工作經驗描述完整', '技能展示清晰'],
      improvements: ['建議增加量化成果', '可補充專案影響力說明'],
      recommendations: ['調整履歷格式以突出重點', '增加關鍵字密度'],
    },
  },
  {
    id: 3,
    date: '2024-01-05',
    title: '職涯發展評估',
    summary: '綜合分析您的職涯現況，規劃未來發展方向。',
    content: {
      strengths: ['目標明確', '持續學習態度佳'],
      improvements: ['需建立更廣泛的人脈網絡', '建議參與開源專案'],
      recommendations: ['3年內晉升資深工程師', '開始培養團隊管理能力'],
    },
  },
];
