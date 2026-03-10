import type { JobData, JobDetailData, JobCategory } from '@/types/job';

// TODO: Replace with API call
export const generateMockJobs = (page: number): JobData[] => {
  const industries = ['科技業', '金融業', '製造業', '服務業', '零售業', '醫療業', '教育業', '電商業'];
  const cities = ['台北市', '新北市', '桃園市', '台中市', '高雄市', '新竹市', '台南市'];
  const positions = [
    { title: '資深前端工程師', desc: '負責開發與維護企業級 Web 應用程式，追求卓越使用者體驗' },
    { title: '產品經理', desc: '主導產品策略規劃，協調跨部門資源達成商業目標' },
    { title: 'UI/UX 設計師', desc: '打造直覺且美觀的數位產品介面，提升品牌價值' },
    { title: '數據分析師', desc: '運用大數據技術挖掘商業洞察，驅動決策優化' },
    { title: '後端工程師', desc: '設計與開發高效能的伺服器端架構與 API 服務' },
    { title: '專案經理', desc: '統籌專案時程與資源，確保如期交付高品質成果' },
    { title: '行銷企劃', desc: '策劃創新行銷活動，擴大品牌影響力與市場覆蓋' },
    { title: '人資專員', desc: '負責人才招募與培訓發展，打造優質企業文化' },
    { title: 'DevOps 工程師', desc: '建構與維護 CI/CD 流程，確保系統穩定與高可用性' },
    { title: '業務主管', desc: '帶領業務團隊開拓市場，達成營收成長目標' },
  ];
  const companies = ['科技新創', '金融集團', '跨國企業', '本土龍頭', '上市公司', '獨角獸', '百年老店', '新興品牌'];

  return positions.map((pos, idx) => ({
    id: (page - 1) * 10 + idx + 1,
    title: pos.title,
    description: pos.desc,
    company: `${companies[idx % companies.length]}股份有限公司`,
    city: cities[idx % cities.length],
    salary: `${40 + idx * 5}K - ${60 + idx * 8}K`,
    industry: industries[idx % industries.length],
    externalUrl: 'https://www.104.com.tw',
  }));
};

// TODO: Replace with API call
export const getMockJobDetail = (id: string): JobDetailData => ({
  id: parseInt(id) || 1,
  title: '資深前端工程師',
  company: '科技創新股份有限公司',
  industry: '資訊科技業',
  city: '台北市信義區',
  address: '台北市信義區信義路五段7號',
  salary: '60K - 100K',
  description: `我們正在尋找一位熱愛前端開發的資深工程師，加入我們的產品團隊。您將負責開發高品質的使用者介面，與後端工程師及設計師密切合作，打造優秀的使用者體驗。

作為團隊核心成員，您將有機會：
• 主導關鍵產品功能的前端架構設計
• 參與技術選型與最佳實踐的制定
• 指導初級工程師成長
• 與產品經理緊密合作，將產品願景轉化為實際功能`,
  requirements: [
    '5 年以上前端開發經驗，具備大型專案經驗者優先',
    '精通 React/Vue 等現代前端框架，熟悉 TypeScript',
    '熟悉 CSS-in-JS、Tailwind CSS 等樣式解決方案',
    '了解前端效能優化、SEO、無障礙設計',
    '具備良好的溝通能力與團隊合作精神',
    '持續學習新技術的熱情，關注前端生態發展',
  ],
  benefits: [
    '具競爭力的薪資與年終獎金',
    '彈性工時與遠端工作選項',
    '完善的教育訓練與進修補助',
    '健康檢查與團體保險',
    '舒適的辦公環境與免費零食',
    '定期團隊建設活動與員工旅遊',
  ],
  skills: ['React', 'TypeScript', 'Tailwind CSS', 'Git', 'RESTful API', 'GraphQL'],
  externalUrl: 'https://www.104.com.tw',
});

// TODO: Replace with API call
export const mockCoverLetter = (jobTitle?: string, company?: string) => ({
  subject: `應徵 ${jobTitle} 職位 - [您的姓名]`,
  body: `親愛的招聘經理：

您好！我是一位熱愛技術、追求卓越的軟體工程師，對貴公司「${company}」的「${jobTitle}」職位深感興趣。透過深入了解貴公司的企業文化與發展願景，我相信我的技術背景與專業經驗能為團隊帶來價值。

【為什麼選擇我】

在過去的工作經歷中，我累積了豐富的專案經驗：
• 主導開發並維護多個大型企業級應用程式
• 成功優化系統效能，將頁面載入速度提升 40%
• 帶領小型技術團隊完成關鍵專案，如期交付

【我能為貴公司帶來的價值】

• 紮實的技術基礎與持續學習的熱情
• 良好的跨部門溝通與團隊協作能力
• 注重程式碼品質與最佳實踐的工程師文化

我期待有機會與您進一步討論，展示我如何能為「${company}」做出貢獻。感謝您撥冗審閱，靜候佳音。

此致
敬禮

[您的姓名]
[您的聯絡電話]
[您的電子郵件]`,
});

// TODO: Replace with API call
export const JOB_CATEGORIES: JobCategory[] = [
  {
    label: '軟體工程師',
    subcategories: [
      {
        label: '前端工程師',
        skills: [
          { name: 'React', tags: ['框架', '前端'], description: '構建互動式使用者介面的主流 JavaScript 函式庫' },
          { name: 'TypeScript', tags: ['語言', '型別安全'], description: 'JavaScript 的超集，提供靜態型別檢查' },
          { name: 'Vue.js', tags: ['框架', '前端'], description: '漸進式 JavaScript 框架，易於上手' },
          { name: 'CSS/Tailwind', tags: ['樣式', '工具'], description: '現代 CSS 框架與工具鏈' },
          { name: 'Next.js', tags: ['框架', 'SSR'], description: 'React 全端框架，支援伺服器端渲染' },
          { name: 'Webpack/Vite', tags: ['建構工具'], description: '前端模組打包與建構工具' },
        ],
      },
      {
        label: '後端工程師',
        skills: [
          { name: 'Node.js', tags: ['執行環境', '後端'], description: '高效能 JavaScript 伺服器端執行環境' },
          { name: 'Python', tags: ['語言', '通用'], description: '廣泛用於後端、資料科學的通用語言' },
          { name: 'Java/Spring', tags: ['語言', '框架'], description: '企業級後端開發的首選技術棧' },
          { name: 'PostgreSQL', tags: ['資料庫', 'SQL'], description: '功能強大的開源關聯式資料庫' },
          { name: 'Redis', tags: ['快取', 'NoSQL'], description: '高效能鍵值存儲與快取系統' },
          { name: 'GraphQL', tags: ['API', '查詢語言'], description: '靈活的 API 查詢語言與規範' },
        ],
      },
      {
        label: '全端工程師',
        skills: [
          { name: 'React + Node.js', tags: ['全端', 'JS'], description: '最熱門的 JavaScript 全端技術組合' },
          { name: 'Docker', tags: ['容器化', 'DevOps'], description: '容器化部署與環境一致性管理' },
          { name: 'REST API 設計', tags: ['API', '架構'], description: '設計可擴展的 RESTful 服務介面' },
          { name: 'CI/CD', tags: ['自動化', 'DevOps'], description: '持續整合與持續部署流程' },
          { name: 'MongoDB', tags: ['資料庫', 'NoSQL'], description: '文件導向的 NoSQL 資料庫' },
          { name: 'AWS/GCP', tags: ['雲端', '基礎設施'], description: '主流雲端平台服務與架構' },
        ],
      },
      {
        label: '資料科學家',
        skills: [
          { name: 'Python/Pandas', tags: ['語言', '資料處理'], description: '資料科學領域最主流的分析工具' },
          { name: 'SQL 進階', tags: ['資料庫', '分析'], description: '複雜查詢、窗函式與效能調校' },
          { name: 'Tableau/Power BI', tags: ['視覺化', '工具'], description: '商業智慧資料視覺化平台' },
          { name: '統計與機率', tags: ['數學', '基礎'], description: '假說檢定、回歸分析等統計方法' },
          { name: 'Spark', tags: ['大數據', '分散式'], description: '大規模資料分散式運算框架' },
          { name: 'ETL Pipeline', tags: ['資料工程'], description: '資料擷取、轉換與載入流程設計' },
        ],
      },
      {
        label: 'AI / 演算法工程師',
        skills: [
          { name: 'TensorFlow/PyTorch', tags: ['深度學習', '框架'], description: '主流深度學習模型訓練框架' },
          { name: 'NLP', tags: ['AI', '自然語言'], description: '自然語言處理與文本分析技術' },
          { name: 'Computer Vision', tags: ['AI', '影像'], description: '影像辨識、物件偵測等電腦視覺應用' },
          { name: 'MLOps', tags: ['部署', '維運'], description: '機器學習模型的部署與監控流程' },
          { name: 'LLM/RAG', tags: ['生成式AI'], description: '大型語言模型與檢索增強生成技術' },
          { name: '演算法與資料結構', tags: ['基礎', '面試'], description: '核心演算法設計與最佳化能力' },
        ],
      },
      {
        label: 'DevOps / SRE',
        skills: [
          { name: 'Kubernetes', tags: ['容器編排', '雲原生'], description: '容器化應用的自動部署與管理平台' },
          { name: 'Terraform', tags: ['IaC', '自動化'], description: '基礎設施即程式碼工具' },
          { name: '監控/Grafana', tags: ['可觀測性'], description: '系統監控、告警與儀表板建置' },
          { name: 'Linux 系統管理', tags: ['作業系統'], description: '伺服器環境管理與疑難排解' },
          { name: 'CI/CD Pipeline', tags: ['自動化', '部署'], description: 'Jenkins、GitHub Actions 等流程設計' },
          { name: '資安基礎', tags: ['安全', '合規'], description: '網路安全、權限管理與合規實踐' },
        ],
      },
    ],
  },
];

export const ICON_NAME_MAP: Record<string, string> = {
  'React': 'React',
  'TypeScript': 'TypeScript',
  'Vue.js': 'Vue',
  'CSS/Tailwind': 'css_tailwind',
  'Next.js': 'Nextjs',
  'Webpack/Vite': 'webpack_vite',
  'Node.js': 'Nodejs',
  'Python': 'Python',
  'Java/Spring': 'SpringBoot',
  'PostgreSQL': 'PostgreSQL',
  'Redis': 'Redis',
  'GraphQL': 'graphql',
  'React + Node.js': 'Nodejs',
  'Docker': 'docker',
  'REST API 設計': 'rest_api',
  'CI/CD': 'Jenkins',
  'MongoDB': 'MongoDB',
  'AWS/GCP': 'AWS',
  'Python/Pandas': 'Python',
  'SQL 進階': 'MySQL',
  'Tableau/Power BI': 'tableau_powerbi',
  '統計與機率': 'statistics',
  'Spark': 'spark',
  'ETL Pipeline': 'etl_pipeline',
  'TensorFlow/PyTorch': 'tensorflow_pytorch',
  'NLP': 'nlp',
  'Computer Vision': 'computer_vision',
  'MLOps': 'mlops',
  'LLM/RAG': 'llm_rag',
  '演算法與資料結構': 'algorithm',
  'Kubernetes': 'Kubernetes',
  'Terraform': 'Terraform',
  '監控/Grafana': 'grafana',
  'Linux 系統管理': 'linux',
  'CI/CD Pipeline': 'Jenkins',
  '資安基礎': 'security',
};

/** Mock recommended jobs matching backend API shape */
export const generateMockRecommendedJobs = (page: number): RecommendedJob[] => {
  const base: RecommendedJob[] = [
    {
      id: 'rec-1',
      title: 'Senior Backend Engineer - Python',
      company: '塔台智能網絡股份有限公司',
      industry: '資訊科技',
      location: '台北市南港區園區街3之2號9樓',
      externalUrl: 'https://www.104.com.tw/job/8n0gu?jobsource=joblist_list',
      salary_range: '60k - 100k',
      match_score: "79.8%",
      recommendation_reason: '此職缺強調 Python 後端開發能力，並需要在 AWS 和 Docker 上有豐富經驗。候選人在 D3 (DevOps) 和 D5 (Quality) 上的高分顯示其具備相關經驗，契合度高。',
      strengths: '候選人在 D3 (DevOps) 和 D6 (Soft Skills) 上的高分顯示了他在系統部署和團隊合作方面的強項，這對於優化現有架構和團隊溝通至關重要。',
      weaknesses: '候選人在 D1 (Frontend) 和 D4 (AI/Data) 的分數較低，可能在前端技術和數據處理上缺乏經驗。',
      interview_tips: '建議候選人在面試前深入了解 AWS 和 Docker 的最新技術趨勢，並準備一些實際應用案例。',
    },
    {
      id: 'rec-2',
      title: '全端工程師',
      company: '數位創新科技有限公司',
      industry: '軟體服務',
      location: '新北市板橋區中山路一段100號',
      externalUrl: 'https://www.104.com.tw/job/example2',
      salary_range: '50k - 80k',
      match_score: "85.2%",
      recommendation_reason: '該職位需要前後端開發能力（D1）及後端開發能力（D2），候選人的全端經驗完美匹配。D5 (Quality) 分數也顯示其具備優良的工程品質意識。',
      strengths: '候選人在 D2 (Backend) 與 D5 (Quality) 表現突出，展現了紮實的後端架構能力與對程式碼品質的高標準。',
      weaknesses: '候選人在 D4 (AI/Data) 方面得分偏低，在資料處理與AI應用上可能需要額外學習。',
      interview_tips: '建議準備全端架構設計案例，展示前後端整合經驗。',
    },
    {
      id: 'rec-3',
      title: 'DevOps Engineer',
      company: '雲端架構顧問公司',
      industry: '雲端服務',
      location: '台中市西屯區台灣大道三段99號',
      externalUrl: 'https://www.104.com.tw/job/example3',
      salary_range: '70k - 90k',
      match_score: "72.5%",
      recommendation_reason: '此職位專注於 D3 (DevOps) 領域，需要 Kubernetes 和 Terraform 經驗。候選人在運維部署（D3）方面有較強背景。',
      strengths: '候選人在 D3 (DevOps) 上的表現出色，具備 CI/CD 與容器化部署的豐富經驗。',
      weaknesses: '候選人的 D1 (Frontend) 和 D6 (Soft Skills) 分數有提升空間。',
      interview_tips: '建議深入了解 Kubernetes 集群管理和 Terraform IaC 最佳實踐。',
    },
    {
      id: 'rec-4',
      title: '資深前端工程師',
      company: '互動體驗設計公司',
      industry: '數位媒體',
      location: '高雄市前鎮區成功二路88號',
      externalUrl: 'https://www.104.com.tw/job/example4',
      salary_range: '60k - 95k',
      match_score: "68.3%",
      recommendation_reason: '職缺要求精通 React 與 TypeScript，屬於 D1 (Frontend) 核心領域。候選人雖在前端開發（D1）得分中等，但 D6 (Soft Skills) 和 D5 (Quality) 高分彌補了差距。',
      strengths: '候選人在 D6 (Soft Skills) 表現卓越，具備良好的溝通與協作能力，適合跨團隊合作。',
      weaknesses: '候選人在前端開發（D1）的專精度不如後端開發（D2），可能需要更多前端框架的深度學習。',
      interview_tips: '建議展示 React 效能優化與使用者體驗設計的實務案例。',
    },
    {
      id: 'rec-5',
      title: 'AI 應用工程師',
      company: '智慧數據分析股份有限公司',
      industry: '人工智慧',
      location: '新竹市東區光復路二段101號',
      externalUrl: 'https://www.104.com.tw/job/example5',
      salary_range: '80k - 120k',
      match_score: "61.7%",
      recommendation_reason: '此職位聚焦 D4 (AI/Data) 領域，要求 LLM 與 NLP 經驗。候選人在 D4 (AI/Data) 分數偏低，但 D2 (Backend) 的強項可支撐 model 部署工作。',
      strengths: '候選人的 D2 (Backend) 和 D3 (DevOps) 能力可協助 AI 模型的工程化部署與 MLOps 流程建設。',
      weaknesses: '候選人在 D4 (AI/Data) 的核心 AI 技能不足，需補強機器學習與深度學習基礎。',
      interview_tips: '建議了解 LLM 與 RAG 架構的基本原理，並準備後端系統支撐 AI 應用的案例。',
    },
  ];

  // For pagination simulation: shift scores slightly per page
  return base.map((job, idx) => {
    const scoreVal = parseFloat((job.match_score as string).replace('%', ''));
    const newScore = Math.max(50, Math.min(99, scoreVal - (page - 1) * 3 + idx));
    return {
      ...job,
      match_score: `${newScore.toFixed(1)}%`,
    };
  });
};

/** Mock detail data for a recommended job */
export const getMockRecommendedJobDetail = (id: string): RecommendedJobDetail => {
  const allJobs = generateMockRecommendedJobs(1);
  const found = allJobs.find(j => j.id === id);

  const base = found ?? allJobs[0];

  return {
    ...base,
    description: `加入我們，參與和改進以下領域的應用開發：

SaaS 平台：
打造一個高度可靠的雲端平台，具有強大的服務水準協議 (SLA)。優化現有架構，實現自動化部署，以確保系統性能的最佳表現。

AWS 雲端和本地基礎架構：
我們的系統主要部署在 AWS Lightsail 上，我們正在尋求您的專業知識，以利用微服務架構，使其能夠兼容將軟體部署到客戶的本地伺服器上。

產品擴展專案和內部工具：
參與客戶管理系統、郵件傳送系統、系統穩定性監控工具和客服回報系統的開發。這些改進旨在提升我們客戶的整體產品體驗。`,
    requirements: [
      '三年以上後端開發經驗，精通 Python',
      '精通 Python 後端框架，如 Flask、FastAPI 或 Django。熟悉 Gunicorn/Uvicorn 程序管理',
      '熟悉 AWS Lightsail、VPC 架構，以及各種 AWS 服務，包括 EC2、S3、KMS 等',
      '精通 Docker，包括使用 Docker-Compose 進行環境開發和部署的經驗',
      '具備配置 Nginx 作為代理伺服器和負載平衡器的能力',
      '專業的 Postgres 資料庫知識，能夠使用 Python SQLAlchemy 進行 ORM 操作',
      '熟練運用 MemCache 資料庫 Redis，能夠緩存高負載計算的結果',
      '具備使用 Celery 執行非同步任務和設計任務工作流程的實務經驗',
    ],
  };
};