// 開發用：各原型的模擬分數與預設結果
import type { PersonalityResult } from '@/data/personalityScoring';

export const MOCK_RESULTS: Record<string, PersonalityResult> = {
  STRUCTURE_ARCHITECT: {
    rawScores: { structure: 9, ambiguity: 2, decision: 3, learning: 3, transfer: 4 },
    scaledScores: { structure: 90, ambiguity: 57, decision: 57, learning: 50, transfer: 71 },
    archetypes: [{ id: 'STRUCTURE_ARCHITECT', name: '結構建模者' }],
  },
  AMBIGUITY_NAVIGATOR: {
    rawScores: { structure: 3, ambiguity: 5, decision: 2, learning: 6, transfer: 2 },
    scaledScores: { structure: 30, ambiguity: 100, decision: 43, learning: 80, transfer: 43 },
    archetypes: [{ id: 'AMBIGUITY_NAVIGATOR', name: '模糊探索者' }],
  },
  RAPID_DECISION_MAKER: {
    rawScores: { structure: 4, ambiguity: 4, decision: 6, learning: 2, transfer: 1 },
    scaledScores: { structure: 40, ambiguity: 86, decision: 100, learning: 40, transfer: 29 },
    archetypes: [{ id: 'RAPID_DECISION_MAKER', name: '快速決策者' }],
  },
  PRAGMATIC_REFINER: {
    rawScores: { structure: 6, ambiguity: 1, decision: 5, learning: 4, transfer: 2 },
    scaledScores: { structure: 60, ambiguity: 43, decision: 86, learning: 60, transfer: 43 },
    archetypes: [{ id: 'PRAGMATIC_REFINER', name: '深度精煉者' }],
  },
  LEARNING_ACCELERATOR: {
    rawScores: { structure: 3, ambiguity: 4, decision: 2, learning: 8, transfer: 2 },
    scaledScores: { structure: 30, ambiguity: 86, decision: 43, learning: 100, transfer: 43 },
    archetypes: [{ id: 'LEARNING_ACCELERATOR', name: '成長加速者' }],
  },
  CROSS_DOMAIN_INTEGRATOR: {
    rawScores: { structure: 5, ambiguity: 2, decision: 2, learning: 3, transfer: 6 },
    scaledScores: { structure: 50, ambiguity: 57, decision: 43, learning: 50, transfer: 100 },
    archetypes: [{ id: 'CROSS_DOMAIN_INTEGRATOR', name: '跨域整合者' }],
  },
};
