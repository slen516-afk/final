import type {
  AnalysisResult,
  AnalysisHistoryItem,
  LearningResource,
  SideProject,
} from '@/types/analysis';

// Full mock analysis result matching new backend JSON structure
export const mockAnalysisResult: AnalysisResult = {
  report_metadata: {
    user_id: 'mock-user-001',
    timestamp: new Date().toISOString(),
  },
  preliminary_summary: {
    core_insight:
      '目前，前端開發領域持續受到關注，尤其是 JavaScript 框架如 React 和 Vue.js 的使用日益普及。使用者在前端開發方面具有豐富的經驗，特別是在使用 React 和 Vue.js 上，並且有實際的優化經驗，這是其在市場中的競爭優勢。',
    industry_insight:
      '目前，前端開發領域持續受到關注，尤其是 JavaScript 框架如 React 和 Vue.js 的使用日益普及。企業對具備 TypeScript、效能優化以及跨平台開發能力的工程師需求持續攀升，全端技能組合已成為市場趨勢。',
    personal_summary:
      '您在前端開發方面具有豐富的經驗，特別是在使用 React 和 Vue.js 上，並且有實際的效能優化經驗，這是您在市場中的核心競爭優勢。建議持續深化後端與雲端部署能力，以拓展職涯寬度。',
  },
  radar_chart: {
    dimensions: [
      { axis: '前端開發', score: 4.0 },
      { axis: '後端開發', score: 2.3 },
      { axis: '運維部署', score: 2.0 },
      { axis: 'AI 與數據', score: 0.5 },
      { axis: '工程品質', score: 3.0 },
      { axis: '軟實力', score: 3.0 },
    ],
  },
  target_radar: {
    dimensions: [
      { axis: '前端開發', score: 4.5 },
      { axis: '後端開發', score: 3.5 },
      { axis: '運維部署', score: 3.0 },
      { axis: 'AI 與數據', score: 2.0 },
      { axis: '工程品質', score: 4.0 },
      { axis: '軟實力', score: 3.5 },
    ],
  },
  gap_analysis: {
    current_status: {
      self_assessment: '中階工程師',
      actual_level: '中階工程師',
      cognitive_bias:
        '使用者自評為中階工程師，與實際技術評估結果一致。然而，後端開發經驗不足，建議加強 Node.js 或其他後端框架的學習，以提升全棧開發能力。',
    },
    target_position: {
      role: '前端工程師',
      match_score: 89,
      gap_description:
        '【優勢 (Strengths)】：使用者在前端開發方面具有豐富的經驗，特別是在使用 React 和 Vue.js 上，並且有實際的優化經驗。\n【劣勢 (Weaknesses)】：後端開發經驗不足，對運維和安全性知識的掌握也相對有限。\n【機會 (Opportunities)】：隨著前端技術的快速發展，使用者可以利用其高結構能力和敘事遷移能力，快速適應新的前端技術和框架。\n【威脅 (Threats)】：如果不加強後端技術和運維知識，可能面臨在技術多樣性要求高的職位中競爭力下降的風險。\n【核心落差 (Gap)】：需要加強後端開發的學習，特別是 Node.js 或其他後端框架的應用，並增加對 CI/CD 和雲服務的了解，以補足全棧開發的能力缺口。',
    },
    action_plan: {
      short_term:
        '參加 Node.js 或 Express.js 的線上課程，並開始使用這些技術開發小型後端應用作為實踐。',
      mid_term:
        '加入或創建一個全棧開發專案，將學習到的後端技術應用到實際項目中，並嘗試使用 Docker 和 CI/CD 工具來部署應用。',
      long_term:
        '考取相關的雲服務證照（如 AWS Certified Developer），並持續關注前端技術的最新發展，參加行業會議和技術社群活動以擴展人脈和知識。',
    },
  },
  learningResources: [
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
  ],
  sideProjects: [
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
  ],
};

// Re-export individual pieces for backward compat
export const learningResources = mockAnalysisResult.learningResources;
export const sideProjects = mockAnalysisResult.sideProjects;

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
