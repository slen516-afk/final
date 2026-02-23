// 人格原型詳細資訊配置

export interface ArchetypeDetail {
  id: string;
  name: string;
  englishName: string;
  image: string;
  bgColor: string;
  accentColor: string;
  accentColorLight: string; // 10% opacity variant for backgrounds
  cardShadow: string;
  strength: string;
  energyCost: string;
  scenarios: string[];
}

export const ARCHETYPE_DETAILS: Record<string, ArchetypeDetail> = {
  STRUCTURE_ARCHITECT: {
    id: 'STRUCTURE_ARCHITECT',
    name: '結構建模者',
    englishName: 'Structure Architect',
    image: '/mascots/Structure_Architect.png',
    bgColor: '#f2f4f7',
    accentColor: '#475569',
    accentColorLight: 'rgba(71,85,105,0.1)',
    cardShadow: '0 4px 20px rgba(71,85,105,0.08)',
    strength: '擅長將複雜、混亂的問題轉化為清楚的結構與框架。',
    energyCost: '在允許先分析、建模、再執行的環境中，能以較低心理耗能產出高品質成果。',
    scenarios: ['問題複雜但可拆解', '需要建立流程、系統或方法論'],
  },
  AMBIGUITY_NAVIGATOR: {
    id: 'AMBIGUITY_NAVIGATOR',
    name: '模糊探索者',
    englishName: 'Ambiguity Navigator',
    image: '/mascots/Ambiguity_Navigator.png',
    bgColor: '#fff9eb',
    accentColor: '#d97706',
    accentColorLight: 'rgba(217,119,6,0.1)',
    cardShadow: '0 4px 20px rgba(217,119,6,0.08)',
    strength: '對不確定性的耐受度高，能在資訊不足時先行動，再根據回饋調整方向。',
    energyCost: '不需要等到「完全確定」，就能保持行動力與判斷品質。',
    scenarios: ['問題未定義', '高變動、試錯成本可控的環境'],
  },
  RAPID_DECISION_MAKER: {
    id: 'RAPID_DECISION_MAKER',
    name: '快速決策者',
    englishName: 'Rapid Decision Maker',
    image: '/mascots/Rapid_Decision_Maker.png',
    bgColor: '#fdf2f2',
    accentColor: '#8d4903',
    accentColorLight: 'rgba(141,73,3,0.1)',
    cardShadow: '0 4px 20px rgba(141,73,3,0.08)',
    strength: '能在時間壓力下快速抓住關鍵變數，做出可承擔後果的決策。',
    energyCost: '對你而言，「可行的下一步」往往比「完美方案」更重要。',
    scenarios: ['高時間壓力', '決策回饋快速、責任明確'],
  },
  PRAGMATIC_REFINER: {
    id: 'PRAGMATIC_REFINER',
    name: '深度精煉者',
    englishName: 'Depth Specialist',
    image: '/mascots/Depth_Specialist.png',
    bgColor: '#f8fafc',
    accentColor: '#675143',
    accentColorLight: 'rgba(103,81,67,0.1)',
    cardShadow: '0 4px 20px rgba(103,81,67,0.08)',
    strength: '當問題被清楚定義後，能長時間專注並持續提升精準度與品質。',
    energyCost: '在專業深度與可靠性累積上，具有高度穩定性。',
    scenarios: ['規格明確', '專業或技術導向的任務'],
  },
  LEARNING_ACCELERATOR: {
    id: 'LEARNING_ACCELERATOR',
    name: '成長加速者',
    englishName: 'Learning Accelerator',
    image: '/mascots/Learning_Accelerator.png',
    bgColor: '#f0fdf4',
    accentColor: '#16a34a',
    accentColorLight: 'rgba(22,163,74,0.1)',
    cardShadow: '0 4px 20px rgba(22,163,74,0.08)',
    strength: '優勢不在於「一開始就會」，而在於能快速吸收回饋並調整策略。',
    energyCost: '在學習密度高、允許試錯的環境中，成長速度往往超過平均。',
    scenarios: ['技能快速演進', '角色仍在發展中的階段'],
  },
  CROSS_DOMAIN_INTEGRATOR: {
    id: 'CROSS_DOMAIN_INTEGRATOR',
    name: '跨域整合者',
    englishName: 'Cross-domain Integrator',
    image: '/mascots/Cross-domain_Integrator.png',
    bgColor: '#f5f3ff',
    accentColor: '#7c3aed',
    accentColorLight: 'rgba(124,58,237,0.1)',
    cardShadow: '0 4px 20px rgba(124,58,237,0.08)',
    strength: '擅長辨識不同領域中的結構相似性，並用同一套思考方式反覆成功。',
    energyCost: '常在跨部門或跨專業合作中成為關鍵連結點。',
    scenarios: ['跨職能合作', '需要溝通、轉譯與整合的角色'],
  },
  GENERALIST: {
    id: 'GENERALIST',
    name: '綜合型',
    englishName: 'Generalist',
    image: '/mascots/fullstack.png',
    bgColor: '#fbf1e8',
    accentColor: '#8d4903',
    accentColorLight: 'rgba(141,73,3,0.1)',
    cardShadow: '0 4px 20px rgba(150,105,73,0.08)',
    strength: '各維度能力均衡發展，能在多元情境中靈活適應。',
    energyCost: '沒有明顯的單一耗能短板，但也需留意是否缺乏深度聚焦。',
    scenarios: ['多元任務並行', '需要廣泛技能的通才型角色'],
  },
};

export function getArchetypeDetail(id: string): ArchetypeDetail {
  return ARCHETYPE_DETAILS[id] || ARCHETYPE_DETAILS.GENERALIST;
}
