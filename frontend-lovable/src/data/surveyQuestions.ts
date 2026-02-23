// 職涯問卷題目資料 (23 題，分 A/B/C/D 四模組)

export interface SkillCategory {
  category: string;
  options: string[];
}

export interface RadioOption {
  label: string;
  value: string | number;
  level?: string;
  tag?: string;
}

export interface CheckboxOption {
  label: string;
  value: string;
}

export interface RankOption {
  label: string;
  value: string;
}

export interface BaseQuestion {
  id: string;
  question: string;
  required: boolean;
}

export interface CategorizedSkillQuestion extends BaseQuestion {
  type: 'categorized_skill_selector';
  options: SkillCategory[];
  validation: { min_selection: number; max_selection: number; scale_min: number; scale_max: number };
  meta: { scale_desc: string };
}

export interface RadioQuestion extends BaseQuestion {
  type: 'radio';
  options: RadioOption[];
}

export interface CheckboxQuestion extends BaseQuestion {
  type: 'checkbox';
  options: CheckboxOption[];
}

export interface RankQuestion extends BaseQuestion {
  type: 'rank';
  options: RankOption[];
  validation: { max_selection: number };
}

export interface TextQuestion extends BaseQuestion {
  type: 'text';
  placeholder: string;
}

export type SurveyQuestion = CategorizedSkillQuestion | RadioQuestion | CheckboxQuestion | RankQuestion | TextQuestion;

export interface SurveyModule {
  id: string;
  title: string;
  description: string;
  questions: SurveyQuestion[];
}

export const surveyModules: SurveyModule[] = [
  {
    id: 'module_A',
    title: '模組 A：硬實力盤點',
    description: '使用 1-5 分自評量表，盤點您的技術能力。',
    questions: [
      {
        id: 'Q1',
        type: 'categorized_skill_selector',
        question: '[核心語言] 請填寫您最擅長的 1-3 種程式語言，並標註熟練度 (1-5)：',
        required: true,
        options: [
          { category: '前端語言', options: ['JavaScript', 'TypeScript', 'HTML', 'CSS'] },
          { category: '後端語言', options: ['Java', 'Go', 'Python', 'C#', 'Rust', 'PHP'] },
          { category: '資料科學語言', options: ['R', 'SQL', 'Julia'] },
        ],
        validation: { min_selection: 1, max_selection: 3, scale_min: 1, scale_max: 5 },
        meta: { scale_desc: '1: 不熟悉, 2: 基礎了解, 3: 能獨立開發, 4: 能優化與除錯, 5: 精通/能指導他人' },
      },
      {
        id: 'Q2',
        type: 'radio',
        required: true,
        question: '[前端開發] 針對前端領域，您的掌握程度最接近以下哪項描述？',
        options: [
          { label: 'A. 僅能修改現有 UI，依賴 Bootstrap 等現成套件，不熟悉 JS 底層', value: 1, level: '新手' },
          { label: 'B. 熟悉 HTML/CSS/Vanilla JS，能切版與製作簡單互動', value: 2, level: '初階' },
          { label: 'C. 熟悉 React/Vue/Angular 其中一種框架，能串接 API 開發 SPA', value: 3, level: '中階' },
          { label: 'D. 精通前端效能優化 (Web Vitals)、State Management (Redux/Pinia) 與 SSR (Next.js/Nuxt)', value: 4, level: '高階' },
          { label: 'E. 能設計前端架構 (Micro-frontends)、設計 System Design', value: 5, level: '專家' },
        ],
      },
      {
        id: 'Q3',
        type: 'radio',
        required: true,
        question: '[後端開發] 針對後端領域，您的掌握程度最接近以下哪項描述？',
        options: [
          { label: 'A. 僅能寫簡單的 Script 處理數據，無 Web Server 開發經驗', value: 1, level: '新手' },
          { label: 'B. 基礎應用：能使用框架撰寫基本的 CRUD API，並理解 RESTful 概念', value: 2, level: '初階' },
          { label: 'C. 核心進階：熟悉資料庫設計、Authentication (JWT/OAuth) 與整合單元測試', value: 3, level: '中階' },
          { label: 'D. 架構優化：具備高併發處理經驗，能導入 Redis 快取、消息隊列', value: 4, level: '高階' },
          { label: 'E. 系統工程：能設計大型分散式系統，考量 CAP 定理與高可用性', value: 5, level: '專家' },
        ],
      },
      {
        id: 'Q4',
        type: 'checkbox',
        required: true,
        question: '[資料庫與儲存] 您在資料庫方面的經驗包含 (可複選)：',
        options: [
          { label: 'A. 關聯式資料庫 (MySQL, PostgreSQL, MS SQL)', value: 'relational' },
          { label: 'B. NoSQL 文件型 (MongoDB, Firestore)', value: 'nosql_doc' },
          { label: 'C. Key-Value/Cache (Redis, Memcached)', value: 'key_value' },
          { label: 'D. 搜尋引擎 (Elasticsearch, Meilisearch)', value: 'search_engine' },
          { label: 'E. 向量資料庫 (Pinecone, Milvus, Chroma, Weaviate)', value: 'vector_db' },
          { label: 'F. 圖形資料庫 (Neo4j)', value: 'graph_db' },
          { label: 'G. 資料倉儲/湖 (BigQuery, Snowflake)', value: 'data_warehouse' },
        ],
      },
      {
        id: 'Q5',
        type: 'radio',
        required: true,
        question: '[DevOps 與雲端] 您的部署與維運經驗最接近以下哪項？',
        options: [
          { label: 'A. 僅使用 FTP 上傳程式碼，或直接在 Server 上 git pull', value: 1, level: '新手' },
          { label: 'B. 熟悉 Linux 基本指令，能撰寫 Dockerfile 並在 local 運行容器', value: 2, level: '初階' },
          { label: 'C. 熟悉 AWS/GCP/Azure 核心服務，能手動配置雲端環境', value: 3, level: '中階' },
          { label: 'D. 熟悉 Kubernetes 物件管理，並能建構 CI/CD 流水線', value: 4, level: '高階' },
          { label: 'E. 能使用 Terraform, Ansible 管理大規模資源，並建立監控系統', value: 5, level: '專家' },
        ],
      },
      {
        id: 'Q6',
        type: 'radio',
        required: true,
        question: '[AI 與數據] 您的 AI/Data 技能包含：',
        options: [
          { label: 'A. 僅止於呼叫 OpenAI/Gemini API', value: 1, level: '使用者' },
          { label: 'B. 熟悉 Pandas/NumPy 進行資料清洗與分析', value: 2, level: '整合者' },
          { label: 'C. 熟悉 Scikit-learn/TensorFlow/PyTorch 進行模型訓練', value: 3, level: '工程師' },
          { label: 'D. 熟悉 RAG 應用開發與 LangChain', value: 4, level: '科學家' },
          { label: 'E. 熟悉 MLOps 與模型部署', value: 5, level: '架構師' },
        ],
      },
      {
        id: 'Q7',
        type: 'radio',
        required: true,
        question: '[資安意識] 在開發過程中，您對資訊安全的掌握度為何？',
        options: [
          { label: 'A. 不熟悉，通常依賴框架預設保護', value: 1, level: '無意識' },
          { label: 'B. 知道基本的 OWASP Top 10 並會避免', value: 2, level: '基礎' },
          { label: 'C. 熟悉身分驗證與授權機制 (OAuth2, RBAC, Encryption)', value: 3, level: '進階' },
          { label: 'D. 能進行 Code Audit，並在 CI/CD 中整合資安掃描', value: 4, level: '防禦' },
        ],
      },
      {
        id: 'Q8',
        type: 'text',
        required: false,
        question: '[領域專精] 除了 coding，您在哪個領域有額外 Domain Knowledge？(選填)',
        placeholder: '例如：FinTech, E-commerce, Healthcare...',
      },
    ],
  },
  {
    id: 'module_B',
    title: '模組 B：軟實力與職級評估',
    description: '透過情境題判斷您的職場思維層級。',
    questions: [
      {
        id: 'Q9',
        type: 'radio',
        required: true,
        question: '[問題解決] 當你發現 Production 環境出現一個緊急 Bug，但原因不明時，你的直覺反應是？',
        options: [
          { label: 'A. 立即重啟伺服器，希望能暫時恢復正常', value: 1, tag: 'Junior' },
          { label: 'B. 撈取 Log 檔案，複製錯誤訊息去搜尋', value: 2, tag: 'Junior+' },
          { label: 'C. 先 rollback 到穩定版本，止血後再重現問題', value: 4, tag: 'Senior' },
          { label: 'D. 通知相關人員，啟動 Incident Response 流程', value: 5, tag: 'Lead' },
        ],
      },
      {
        id: 'Q10',
        type: 'radio',
        required: true,
        question: '[技術決策] 團隊要開發一個新功能，在選擇技術框架時，你會優先考慮？',
        options: [
          { label: 'A. 我最近剛學會的新技術，很想試試看', value: 1, tag: 'Junior' },
          { label: 'B. 社群最熱門、星星數最多的技術', value: 2, tag: 'Junior+' },
          { label: 'C. 團隊現有成員最熟悉的技術，降低風險', value: 4, tag: 'Senior' },
          { label: 'D. 基於長期維護性與業務需求的權衡分析', value: 5, tag: 'Architect' },
        ],
      },
      {
        id: 'Q11',
        type: 'radio',
        required: true,
        question: '[溝通協作] 當 PM 提出一個你認為技術上不可行的需求時，你會？',
        options: [
          { label: 'A. 雖然覺得不合理，但還是照著做', value: 1, tag: 'Passive' },
          { label: 'B. 直接告訴他做不到，請他改需求', value: 2, tag: 'Aggressive' },
          { label: 'C. 解釋技術限制，並提出替代方案', value: 4, tag: 'Collaborative' },
          { label: 'D. 評估背後的商業價值，重新調配資源實現', value: 5, tag: 'Strategic' },
        ],
      },
      {
        id: 'Q12',
        type: 'radio',
        required: true,
        question: '[程式碼品質] 你對 Code Review 的態度是？',
        options: [
          { label: 'A. 形式主義，只要功能會動就好', value: 2, tag: 'Junior' },
          { label: 'B. 主要檢查 Coding Style 是否符合規範', value: 3, tag: 'Mid' },
          { label: 'C. 檢查程式邏輯錯誤與邊界情況', value: 4, tag: 'Senior' },
          { label: 'D. 關注架構設計、可維護性與 SOLID 原則', value: 5, tag: 'Lead' },
        ],
      },
      {
        id: 'Q13',
        type: 'radio',
        required: true,
        question: '[學習心態] 面對快速變化的軟體技術，你的學習習慣是？',
        options: [
          { label: 'A. 等到公司專案要用了才學', value: 1 },
          { label: 'B. 買了一堆課程但很少看完', value: 2 },
          { label: 'C. 固定每週撥出時間閱讀技術文章或做 Side Project', value: 3 },
          { label: 'D. 會深入研究底層原理，並在團隊內部分享', value: 5 },
        ],
      },
      {
        id: 'Q14',
        type: 'radio',
        required: true,
        question: '[開發流程] 您熟悉的軟體開發方法論為何？',
        options: [
          { label: 'A. 瀑布式開發或沒特定流程，需求來了就做', value: 1 },
          { label: 'B. 熟悉 Agile/Scrum 儀式 (Daily Standup, Sprint Planning)', value: 2 },
          { label: 'C. 熟悉看板管理 (Kanban) 與 Jira/Trello 工具操作', value: 3 },
          { label: 'D. 能帶領團隊進行 Retrospective 並優化開發流程', value: 5 },
        ],
      },
      {
        id: 'Q15',
        type: 'radio',
        required: true,
        question: '[英語能力] 您的英文技術閱讀與溝通能力？',
        options: [
          { label: 'A. 依賴翻譯工具翻譯技術文件', value: 1 },
          { label: 'B. 能緩慢閱讀英文官方文件，但偏好中文資源', value: 2 },
          { label: 'C. 能流暢閱讀英文文件與 StackOverflow', value: 3 },
          { label: 'D. 能使用英文進行 Code Review 與跨國會議溝通', value: 5 },
        ],
      },
    ],
  },
  {
    id: 'module_C',
    title: '模組 C：職涯定位與期待',
    description: '定義您的職涯目標與產業偏好。',
    questions: [
      {
        id: 'Q16',
        type: 'radio',
        required: true,
        question: '[目前狀態] 您如何定義自己目前的職涯階段？',
        options: [
          { label: 'A. 轉職中/學習中 (Entry Level)', value: 'Entry' },
          { label: 'B. 初階工程師 (Junior, 0-2年)', value: 'Junior' },
          { label: 'C. 中階工程師 (Mid-Level, 2-5年)', value: 'Mid' },
          { label: 'D. 資深工程師 (Senior, 5年以上)', value: 'Senior' },
          { label: 'E. 技術主管/架構師 (Lead/Architect)', value: 'Lead' },
        ],
      },
      {
        id: 'Q17',
        type: 'radio',
        required: true,
        question: '[目標職位] 您在未來 1-3 年內最想擔任的角色是？',
        options: [
          { label: 'A. 前端工程師 (Frontend)', value: 'Frontend' },
          { label: 'B. 後端工程師 (Backend)', value: 'Backend' },
          { label: 'C. 全端工程師 (Full Stack)', value: 'FullStack' },
          { label: 'D. 資料科學家/分析師', value: 'Data' },
          { label: 'E. AI/演算法工程師', value: 'AI' },
          { label: 'F. DevOps/SRE 工程師', value: 'DevOps' },
        ],
      },
      {
        id: 'Q18',
        type: 'radio',
        required: true,
        question: '[產業偏好] 您最希望進入哪種類型的公司？',
        options: [
          { label: 'A. 新創公司：高風險、高成長、彈性大', value: 'Startup' },
          { label: 'B. 科技巨頭：制度完善、薪資高', value: 'BigTech' },
          { label: 'C. 傳統產業數位轉型：穩定、工作生活平衡', value: 'Traditional' },
          { label: 'D. 接案公司：接觸專案多、練功快', value: 'SoftwareHouse' },
          { label: 'E. 自有產品公司：深耕單一產品', value: 'Product' },
        ],
      },
      {
        id: 'Q19',
        type: 'radio',
        required: true,
        question: '[求職狀態] 您目前的求職急迫度與規劃？',
        options: [
          { label: 'A. 積極求職中，希望 1 個月內上工', value: 'Active' },
          { label: 'B. 觀望中，有好的機會才考慮', value: 'Passive' },
          { label: 'C. 純粹了解市場行情，目前無轉職打算', value: 'MarketCheck' },
          { label: 'D. 學生/培訓中，預計畢業後開始求職', value: 'Student' },
        ],
      },
    ],
  },
  {
    id: 'module_D',
    title: '模組 D：職涯錨點與價值觀',
    description: '決定推薦演算法的權重配置。',
    questions: [
      {
        id: 'Q20',
        type: 'rank',
        required: true,
        question: '[排序題] 請將以下工作價值觀依照「重要性」排序 (由高到低選前三名)：',
        options: [
          { label: '高薪資與獎金 (Financial)', value: 'financial' },
          { label: '技術挑戰與成長 (Technical Competence)', value: 'technical' },
          { label: '工作與生活平衡 (WLB)', value: 'wlb' },
          { label: '公司名氣與品牌 (Status)', value: 'status' },
          { label: '團隊氣氛與文化 (Culture)', value: 'culture' },
          { label: '產品的社會影響力 (Service/Cause)', value: 'impact' },
        ],
        validation: { max_selection: 3 },
      },
      {
        id: 'Q21',
        type: 'radio',
        required: true,
        question: '[穩定 vs 挑戰] 如果有一份薪水高出 20% 但需要經常加班且壓力大的工作，你會？',
        options: [
          { label: 'A. 毫不猶豫接受', value: 'accept_immediately' },
          { label: 'B. 考慮接受，短期衝刺存錢', value: 'consider' },
          { label: 'C. 傾向拒絕，健康重要', value: 'reject_likely' },
          { label: 'D. 絕對拒絕', value: 'reject_absolute' },
        ],
      },
      {
        id: 'Q22',
        type: 'radio',
        required: true,
        question: '[專才 vs 通才] 你更傾向成為？',
        options: [
          { label: 'A. 技術專才：在特定技術領域鑽研到極致', value: 'specialist' },
          { label: 'B. 技術通才：什麼都懂一點，能快速解決各種問題', value: 'generalist' },
          { label: 'C. 管理職：帶領團隊達成目標', value: 'manager' },
        ],
      },
      {
        id: 'Q23',
        type: 'checkbox',
        required: true,
        question: '[學習偏好] 當您需要學習新技術時，您最偏好的方式是？(複選)',
        options: [
          { label: 'A. 官方文件與技術手冊', value: 'docs' },
          { label: 'B. 影音課程 (Udemy, YouTube)', value: 'video' },
          { label: 'C. 實作專案做中學', value: 'project' },
          { label: 'D. 閱讀技術書籍或電子書', value: 'book' },
          { label: 'E. 請教導師或參加社群', value: 'community' },
        ],
      },
    ],
  },
];
