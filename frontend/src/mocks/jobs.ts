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
  subject: `${jobTitle ?? '應用軟體工程師'}職位申請 - 擁有微服務架構經驗的系統架構師`,
  content:
    `親愛的招聘團隊，您好，我是王俊傑，一名專注於構建可擴展系統的系統架構師，擁有八年的行業經驗。我對貴公司應用軟體工程師的職位非常感興趣，特別是貴公司在技術創新和工業

應用方面的卓越表現深深吸引了我。在LINE

Taiwan擔任系統架構師期間，我設計並實施了支持超過一千萬用戶的微服務架構，並成功將基礎設施成本降低了25%。這與貴公司對Windows程式開發及現場問題分析的需求高度契合。我相

信，我在分布式系統和微服務方面的專業知識將為貴公司帶來實質的價值。此外，我在趨勢科技領導了由五人組成的團隊，專注於分布式系統的構建、Kafka事件流處理以及Kubernetes部

署。這些經驗使我能夠快速適應並解決機台程式的除錯問題，並提出有效的解決方案。我非常期待有機會進一步討論我如何能夠為貴公司帶來貢獻。感謝您考慮我的申請，期待您的回覆。

此致，王俊傑 tech_guru@outlook.com https://github.com/wang-tech-pro`
});

// TODO: Replace with API call
export const JOB_CATEGORIES: JobCategory[] = [
  {
    label: '軟體工程師',
    subcategories: [
      {
        label: '前端工程師',
        skills: [
          { name: 'JavaScript', tags: ['語言', '前端'], description: '網頁開發最核心的程式語言，幾乎所有前端互動皆仰賴它' },
          { name: 'CSS', tags: ['樣式', '前端'], description: '負責網頁視覺呈現的樣式語言' },
          { name: 'Git', tags: ['版本控制', '工具'], description: '分散式版本控制系統，團隊協作必備' },
          { name: 'HTML', tags: ['標記語言', '前端'], description: '網頁結構的基礎標記語言' },
          { name: 'React', tags: ['框架', '前端'], description: '由 Meta 開發的主流使用者介面函式庫' },
          { name: 'Vue', tags: ['框架', '前端'], description: '漸進式 JavaScript 框架，易學易用' },
          { name: 'Communication', tags: ['軟實力'], description: '有效表達與傾聽的溝通協作能力' },
          { name: 'TypeScript', tags: ['語言', '型別安全'], description: 'JavaScript 的超集，提供靜態型別檢查' },
          { name: 'Problem Solving', tags: ['軟實力'], description: '分析問題並提出解決方案的能力' },
          { name: 'jQuery', tags: ['函式庫', '前端'], description: '簡化 DOM 操作的經典 JavaScript 函式庫' },
        ],
      },
      {
        label: '後端工程師',
        skills: [
          { name: 'Git', tags: ['版本控制', '工具'], description: '分散式版本控制系統，團隊協作必備' },
          { name: 'Linux', tags: ['作業系統', '伺服器'], description: '伺服器環境管理與命令列操作' },
          { name: 'Python', tags: ['語言', '通用'], description: '廣泛用於後端、資料科學的通用語言' },
          { name: 'C#', tags: ['語言', '.NET'], description: '微軟開發的物件導向語言，常用於企業應用' },
          { name: 'C++', tags: ['語言', '系統'], description: '高效能系統與底層開發語言' },
          { name: 'Communication', tags: ['軟實力'], description: '有效表達與傾聽的溝通協作能力' },
          { name: 'JavaScript', tags: ['語言', '全端'], description: '可用於前後端的通用腳本語言' },
          { name: 'Java', tags: ['語言', '企業級'], description: '企業級後端開發的主流語言' },
          { name: 'MySQL', tags: ['資料庫', 'SQL'], description: '最受歡迎的開源關聯式資料庫' },
          { name: 'Problem Solving', tags: ['軟實力'], description: '分析問題並提出解決方案的能力' },
        ],
      },
      {
        label: '全端工程師',
        skills: [
          { name: 'JavaScript', tags: ['語言', '全端'], description: '前後端皆通用的核心程式語言' },
          { name: 'HTML', tags: ['標記語言', '前端'], description: '網頁結構的基礎標記語言' },
          { name: 'C#', tags: ['語言', '.NET'], description: '微軟開發的物件導向語言，常用於企業應用' },
          { name: 'CSS', tags: ['樣式', '前端'], description: '負責網頁視覺呈現的樣式語言' },
          { name: 'Git', tags: ['版本控制', '工具'], description: '分散式版本控制系統，團隊協作必備' },
          { name: 'Python', tags: ['語言', '通用'], description: '廣泛用於後端與自動化的通用語言' },
          { name: 'Vue', tags: ['框架', '前端'], description: '漸進式 JavaScript 框架，易學易用' },
          { name: 'Java', tags: ['語言', '企業級'], description: '企業級後端開發的主流語言' },
          { name: 'Communication', tags: ['軟實力'], description: '有效表達與傾聽的溝通協作能力' },
          { name: 'jQuery', tags: ['函式庫', '前端'], description: '簡化 DOM 操作的經典 JavaScript 函式庫' },
        ],
      },
      {
        label: '資料科學家/數據分析師',
        skills: [
          { name: 'Python', tags: ['語言', '資料'], description: '資料科學領域最主流的分析語言' },
          { name: 'Excel', tags: ['工具', '分析'], description: '數據整理與基礎分析的必備工具' },
          { name: 'Communication', tags: ['軟實力'], description: '將分析結果轉化為商業洞察的溝通力' },
          { name: 'Tableau', tags: ['視覺化', '工具'], description: '互動式商業智慧資料視覺化平台' },
          { name: 'Power BI', tags: ['視覺化', '工具'], description: '微軟推出的商業分析與報表工具' },
          { name: 'Problem Solving', tags: ['軟實力'], description: '分析問題並提出解決方案的能力' },
          { name: 'ETL', tags: ['資料工程', '流程'], description: '資料擷取、轉換與載入流程' },
          { name: 'Project Management', tags: ['軟實力', '管理'], description: '專案規劃、執行與進度管理能力' },
          { name: 'MySQL', tags: ['資料庫', 'SQL'], description: '最受歡迎的開源關聯式資料庫' },
          { name: 'Git', tags: ['版本控制', '工具'], description: '分散式版本控制系統，團隊協作必備' },
        ],
      },
      {
        label: 'AI/演算法工程師',
        skills: [
          { name: 'Python', tags: ['語言', 'AI'], description: 'AI 與機器學習開發的首選語言' },
          { name: 'C++', tags: ['語言', '效能'], description: '高效能運算與底層演算法實作' },
          { name: 'PyTorch', tags: ['深度學習', '框架'], description: '靈活的深度學習研究與生產框架' },
          { name: 'TensorFlow', tags: ['深度學習', '框架'], description: 'Google 開源的端到端機器學習平台' },
          { name: 'LLM', tags: ['生成式AI', '模型'], description: '大型語言模型的訓練與應用' },
          { name: 'Git', tags: ['版本控制', '工具'], description: '分散式版本控制系統，團隊協作必備' },
          { name: 'Communication', tags: ['軟實力'], description: '有效表達與傾聽的溝通協作能力' },
          { name: 'Linux', tags: ['作業系統', '伺服器'], description: '伺服器環境與 GPU 運算環境管理' },
          { name: 'NLP', tags: ['AI', '自然語言'], description: '自然語言處理與文本分析技術' },
          { name: 'C#', tags: ['語言', '.NET'], description: '微軟開發的物件導向語言' },
        ],
      },
      {
        label: 'DevOps/SRE工程師',
        skills: [
          { name: 'Linux', tags: ['作業系統', '伺服器'], description: '伺服器環境管理與命令列操作' },
          { name: 'Communication', tags: ['軟實力'], description: '跨團隊協調與事件溝通能力' },
          { name: 'Excel', tags: ['工具', '報表'], description: '數據整理與營運報表工具' },
          { name: 'Problem Solving', tags: ['軟實力'], description: '快速排除故障與解決問題的能力' },
          { name: 'Python', tags: ['語言', '自動化'], description: '自動化腳本與工具開發' },
          { name: 'AWS', tags: ['雲端', '基礎設施'], description: 'Amazon 雲端平台服務' },
          { name: 'Shell', tags: ['腳本', '系統'], description: 'Shell 腳本撰寫與系統自動化' },
          { name: 'Kubernetes', tags: ['容器編排', '雲原生'], description: '容器化應用的自動部署與管理平台' },
          { name: 'Azure', tags: ['雲端', '基礎設施'], description: '微軟雲端平台服務' },
          { name: 'Git', tags: ['版本控制', '工具'], description: '分散式版本控制系統，團隊協作必備' },
        ],
      },
    ],
  },
];

export const ICON_NAME_MAP: Record<string, string> = {
  'JavaScript': 'javascript',
  'CSS': 'CSS',
  'Git': 'Git',
  'HTML': 'HTML',
  'React': 'React',
  'Vue': 'Vue',
  'Communication': 'Communication',
  'TypeScript': 'TypeScript',
  'Problem Solving': 'Problem_Solving',
  'jQuery': 'jQuery',
  'Linux': 'Linux',
  'Python': 'Python',
  'C#': 'CSharp',
  'C++': 'Cpp',
  'Java': 'java',
  'MySQL': 'MySQL',
  'Excel': 'Excel',
  'Tableau': 'Tableau',
  'Power BI': 'PowerBI',
  'ETL': 'ETL',
  'Project Management': 'JIRA',
  'PyTorch': 'PyTorch',
  'TensorFlow': 'tensorflow',
  'LLM': 'LLM',
  'NLP': 'NLP',
  'AWS': 'AWS',
  'Shell': 'Shell',
  'Kubernetes': 'Kubernetes',
  'Azure': 'Azure',
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