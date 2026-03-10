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
  learningStrategy: {
    overall_strategy:
      '基於目前的媒合度，建議使用者應先鞏固地基，再逐步過渡到高階技術的掌握。首先，確保對微服務架構設計和雲端技術的基礎理解，這是當前後端技術趨勢的核心。參加相關線上課程或獲取認證可以快速提升這兩個領域的知識。接著，在掌握基礎後，通過參加開源項目或在現有工作中主動尋求機會實踐容器化技術和高併發處理方案，將理論知識轉化為實際經驗。最後，向高階技術進發，專注於數據庫性能優化和系統性能調優，這不僅提升技術深度，還能在複雜項目中發揮更大作用。',
    milestones: [
      '完成高併發處理技術的學習，能夠應對大規模用戶請求。',
      '掌握數據庫優化技術，能夠設計高效能的數據庫系統。',
      '熟練運用 Django 及 REST 框架，構建可擴展的後端應用。',
      '理解並應用面向對象設計原則，靈活運用多種編程語言。',
    ],
  },
  learningResources: [
    {
      title: 'High-Performance and Parallel Computing',
      description: '本課程提供高併發處理的基礎知識，為後續進一步優化系統性能打下基礎。',
      tags: ['DevOps', '高併發', '熱門'],
      link: 'https://www.coursera.org/specializations/high-performance-parallel-computing',
      rating: 4.7,
      review_count: 1200,
      level: 'Intermediate',
      course_type: 'Specialization',
      duration: '3 months',
      priority: 1,
      strategy_reason:
        '本課程提供高併發處理的基礎知識，為後續進一步優化系統性能打下基礎。掌握高併發處理能力是後端工程師必須具備的基礎技能，尤其在微服務和容器化技術廣泛應用的環境中。',
    },
    {
      title: 'Advanced Relational Database and SQL',
      description: '在掌握高併發基礎後，進一步提升數據庫設計與優化能力。',
      tags: ['資料庫', 'SQL', '進階'],
      link: 'https://www.coursera.org/projects/advanced-rdb-sql',
      rating: 4.8,
      review_count: 950,
      level: 'Advanced',
      course_type: 'Project',
      duration: '2 months',
      priority: 2,
      strategy_reason:
        '在掌握高併發基礎後，進一步提升數據庫設計與優化能力。強化對 SQL 數據庫的優化技術是提升系統性能的關鍵，尤其在處理大規模數據時。',
    },
    {
      title: 'Advanced Django: Mastering Django and Django Rest Framework',
      description: '在數據庫優化之後，進一步掌握框架技術如 Django，這是構建微服務架構的關鍵。',
      tags: ['Python', 'Django', '後端'],
      link: 'https://www.coursera.org/specializations/codio-advanced-django-and-django-rest-framework',
      rating: 4.6,
      review_count: 800,
      level: 'Advanced',
      course_type: 'Specialization',
      duration: '4 months',
      priority: 3,
      strategy_reason:
        '在數據庫優化之後，進一步掌握框架技術如 Django，這是構建微服務架構的關鍵。Django 框架的深入掌握有助於構建可擴展的應用程式和 RESTful API。',
    },
    {
      title: 'Advanced Ruby Programming and Object-Oriented Design',
      description: '進一步提升對面向對象設計和 Ruby 編程的掌握，增加在異構系統環境中的適應能力。',
      tags: ['Ruby', 'OOP', '設計'],
      link: 'https://www.coursera.org/learn/packt-advanced-ruby-programming-and-object-oriented-design-prbon',
      rating: 4.5,
      review_count: 700,
      level: 'Advanced',
      course_type: 'Course',
      duration: '3 months',
      priority: 4,
      strategy_reason:
        '最後，進一步提升對面向對象設計和 Ruby 編程的掌握。這將有助於理解和應用多樣化的技術方案，增加在異構系統環境中的適應能力。',
    },
  ],
  sideProjects: [
    {
      name: '智慧化物流系統',
      name_en: 'Intelligent Logistics System',
      capability_gaps: ['後端系統設計', '數據處理能力', '數據分析能力', '人工智能應用能力', '系統優化與擴展能力'],
      technologies: ['Python', 'Flask', 'TensorFlow', 'PyTorch', 'PostgreSQL', 'Docker', 'Kubernetes'],
      phases: [
        {
          phase_name: '階段一：物流系統後端',
          goal: '開發一個基本的物流系統後端',
          tasks: ['使用 Flask 建立 API', '處理基本的訂單數據'],
          resume_value: '成功設計並實作一個可擴展的物流系統後端，強調系統架構設計能力。',
        },
        {
          phase_name: '階段二：數據分析模組',
          goal: '展示使用者的數據分析能力。',
          tasks: ['整合 PostgreSQL 資料庫', '實作數據收集與簡單分析功能', '產生報表'],
          resume_value: '實作數據收集與分析模組，提升數據處理能力。',
        },
        {
          phase_name: '階段三：人工智能預測',
          goal: '證明使用者在人工智能技術上的應用能力。',
          tasks: ['使用 TensorFlow 或 PyTorch 開發需求預測模型', '整合機器學習模型', '實作預測功能', '評估模型效能'],
          resume_value: '成功應用人工智能技術於需求預測，增強系統智能化水平。',
        },
        {
          phase_name: '階段四：系統優化與擴展',
          goal: '展示使用者在高壓環境下的系統優化與擴展能力。',
          tasks: ['使用 Docker 和 Kubernetes 進行系統容器化', '自動化部署'],
          resume_value: '實作系統容器化與自動化部署，提升系統在高壓環境下的穩定性與擴展能力。',
        },
      ],
      overall_resume_impact: '此專案計畫不僅符合該職位的技術要求，還能有效地在履歷上展示使用者的多方面能力，並且具備真實世界的商業邏輯，讓面試官能夠深入探討專案細節。',
      difficulty: 3,
      difficulty_label: '中等',
      estimated_duration: '12 週',
      difficulty_note: '主要挑戰在於整合多種技術棧並確保系統的穩定性與擴展性。',
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
