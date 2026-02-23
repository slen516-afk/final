// 人格特質問卷題目資料 (10 題，分 5 模組，每模組 2 題)

export interface PTOption {
  key: string;
  text: string;
}

export interface PTQuestion {
  id: string;
  type: 'single';
  construct: string;
  question: string;
  options: PTOption[];
}

export interface PTModule {
  module_id: string;
  module_name: string;
  theory: string;
  questions: PTQuestion[];
}

export const personalityTestModules: PTModule[] = [
  {
    module_id: 'A',
    module_name: 'Cognitive Trigger',
    theory: 'Cognitive Load Theory',
    questions: [
      {
        id: 'Q1',
        type: 'single',
        construct: 'Task Initiation Style',
        question: '你接到一個全新任務時，最常見的第一步是？',
        options: [
          { key: 'A', text: '先確認目標與評估標準是否明確' },
          { key: 'B', text: '直接動手做一版雛形，再邊做邊修' },
          { key: 'C', text: '先拆解任務結構，釐清各子問題' },
          { key: 'D', text: '觀察別人怎麼做，尋求既有範例' },
        ],
      },
      {
        id: 'Q2',
        type: 'single',
        construct: 'Low Cognitive Load Context',
        question: '哪種情境下，你最不容易感到疲累？',
        options: [
          { key: 'A', text: '將雜亂無章的資訊整理成清晰的架構' },
          { key: 'B', text: '在時間壓力下快速做出判斷與決策' },
          { key: 'C', text: '鑽研新技術或深究錯誤產生的根源' },
          { key: 'D', text: '與人反覆討論直到共識形成' },
        ],
      },
    ],
  },
  {
    module_id: 'B',
    module_name: 'Ambiguity Tolerance',
    theory: 'Tolerance for Ambiguity (Budner / McLain)',
    questions: [
      {
        id: 'Q3',
        type: 'single',
        construct: 'Reaction to Incomplete Information',
        question: '當資訊明顯不足時，你通常會？',
        options: [
          { key: 'A', text: '先提出假設並行動' },
          { key: 'B', text: '嘗試蒐集更多資訊' },
          { key: 'C', text: '拆成多個可處理的小問題' },
          { key: 'D', text: '覺得卡住，難以開始' },
        ],
      },
      {
        id: 'Q4',
        type: 'single',
        construct: 'Decision Attitude Under Uncertainty',
        question: '你對「不完全正確但可用的決定」的看法是？',
        options: [
          { key: 'A', text: '可以接受，認為先求有再求好是必要的' },
          { key: 'B', text: '視風險大小而定，不排斥嘗試' },
          { key: 'C', text: '不太安心，傾向等更完整資訊再行動' },
          { key: 'D', text: '認為這是不負責任的行為' },
        ],
      },
    ],
  },
  {
    module_id: 'C',
    module_name: 'Decision Cost Awareness',
    theory: 'Bounded Rationality / Naturalistic Decision Making',
    questions: [
      {
        id: 'Q5',
        type: 'single',
        construct: 'Primary Decision Consideration',
        question: '需要做重要決策時，你最先想到的是？',
        options: [
          { key: 'A', text: '對整體系統或長期架構的連鎖影響' },
          { key: 'B', text: '對當下的目標是否有直接效果' },
          { key: 'C', text: '是否能獲得周圍夥伴的認同與支持' },
          { key: 'D', text: '是否符合公司既有的流程與規章' },
        ],
      },
      {
        id: 'Q6',
        type: 'single',
        construct: 'Decision Under Time Pressure',
        question: '時間非常有限時，你通常？',
        options: [
          { key: 'A', text: '使用直覺快速判斷' },
          { key: 'B', text: '找最關鍵的1-2個指標' },
          { key: 'C', text: '延後決策以降低風險' },
          { key: 'D', text: '尋求主管或同事的共識' },
        ],
      },
    ],
  },
  {
    module_id: 'D',
    module_name: 'Self-Regulated Learning',
    theory: 'Zimmerman / Dweck',
    questions: [
      {
        id: 'Q7',
        type: 'single',
        construct: 'Error Correction Style',
        question: '當你發現方向錯誤時，你通常會？',
        options: [
          { key: 'A', text: '立即調整方向' },
          { key: 'B', text: '先分析錯誤原因' },
          { key: 'C', text: '嘗試修補原方案' },
          { key: 'D', text: '感到挫折，暫停行動' },
        ],
      },
      {
        id: 'Q8',
        type: 'single',
        construct: 'Feedback Attitude',
        question: '面對他人給予的回饋，你通常的態度是？',
        options: [
          { key: 'A', text: '視為優化認知或邏輯的資訊' },
          { key: 'B', text: '視情況採納' },
          { key: 'C', text: '容易質疑自己的能力' },
          { key: 'D', text: '傾向防衛或忽略' },
        ],
      },
    ],
  },
  {
    module_id: 'E',
    module_name: 'Transfer of Learning',
    theory: 'Gentner / Mental Model Theory',
    questions: [
      {
        id: 'Q9',
        type: 'single',
        construct: 'Concept Transfer',
        question: '當你學到一個新概念時，你通常會？',
        options: [
          { key: 'A', text: '立刻聯想到能如何應用在其他情境' },
          { key: 'B', text: '先專注當下應用，不做額外聯想' },
          { key: 'C', text: '需要透過大量實作練習來理解' },
          { key: 'D', text: '覺得概念太過抽象，難以對應到現實' },
        ],
      },
      {
        id: 'Q10',
        type: 'single',
        construct: 'Narrative Framing Style',
        question: '當你解釋一個複雜問題時，你通常會？',
        options: [
          { key: 'A', text: '先講核心結構，再補細節' },
          { key: 'B', text: '依時間順序或執行步驟說明' },
          { key: 'C', text: '用具體例子，由案例延伸' },
          { key: 'D', text: '根據對方背景動態調整說明方式' },
        ],
      },
    ],
  },
];
