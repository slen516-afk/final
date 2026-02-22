// 人格特質問卷計分引擎

export type Dimension = 'structure' | 'ambiguity' | 'decision' | 'learning' | 'transfer';

export const DIMENSIONS: Dimension[] = ['structure', 'ambiguity', 'decision', 'learning', 'transfer'];

export const DIMENSION_LABELS: Record<Dimension, string> = {
  structure: '結構',
  ambiguity: '模糊',
  decision: '決策',
  learning: '學習',
  transfer: '跨域',
};

export const DIMENSION_CONFIG: Record<Dimension, { min: number; max: number }> = {
  structure: { min: 0, max: 10 },
  ambiguity: { min: -2, max: 5 },
  decision: { min: -1, max: 6 },
  learning: { min: -2, max: 8 },
  transfer: { min: -1, max: 6 },
};

type ScoreImpact = Partial<Record<Dimension, number>>;

const SCORING_MAP: Record<string, Record<string, ScoreImpact>> = {
  Q1: {
    A: { structure: 1 },
    B: { ambiguity: 1 },
    C: { structure: 2 },
    D: {},
  },
  Q2: {
    A: { structure: 2 },
    B: { decision: 2 },
    C: { learning: 1 },
    D: {},
  },
  Q3: {
    A: { ambiguity: 2 },
    B: { structure: 1 },
    C: { ambiguity: 1 },
    D: { ambiguity: -1 },
  },
  Q4: {
    A: { ambiguity: 2, learning: 1 },
    B: { decision: 1 },
    C: {},
    D: { ambiguity: -1 },
  },
  Q5: {
    A: { structure: 1, transfer: 1 },
    B: { decision: 1 },
    C: {},
    D: {},
  },
  Q6: {
    A: { decision: 2 },
    B: { decision: 1, structure: 1 },
    C: { decision: -1 },
    D: {},
  },
  Q7: {
    A: { learning: 2 },
    B: { learning: 1, structure: 1 },
    C: {},
    D: { learning: -1 },
  },
  Q8: {
    A: { learning: 2, transfer: 1 },
    B: { learning: 1 },
    C: {},
    D: { learning: -1 },
  },
  Q9: {
    A: { transfer: 2 },
    B: { learning: 1 },
    C: {},
    D: { transfer: -1 },
  },
  Q10: {
    A: { structure: 2, transfer: 1 },
    B: { transfer: 1 },
    C: { transfer: 1 },
    D: { transfer: 2 },
  },
};

export interface Archetype {
  id: string;
  name: string;
}

const ARCHETYPE_RULES: Array<Archetype & { check: (s: Record<Dimension, number>) => boolean }> = [
  { id: 'STRUCTURE_ARCHITECT', name: '結構建模者', check: (s) => s.structure >= 45 && s.transfer >= 50 },
  { id: 'AMBIGUITY_NAVIGATOR', name: '模糊探索者', check: (s) => s.ambiguity >= 78 && s.learning >= 50 },
  { id: 'RAPID_DECISION_MAKER', name: '快速決策者', check: (s) => s.decision >= 78 && s.ambiguity >= 60 },
  { id: 'PRAGMATIC_REFINER', name: '深度精煉者', check: (s) => s.decision >= 70 && s.structure >= 40 },
  { id: 'LEARNING_ACCELERATOR', name: '成長加速者', check: (s) => s.learning >= 54 && s.ambiguity >= 65 },
  { id: 'CROSS_DOMAIN_INTEGRATOR', name: '跨域整合者', check: (s) => s.transfer >= 64 && s.structure >= 40 },
];

// Step A: Raw scores
export function calculateRawScores(answers: Record<string, string>): Record<Dimension, number> {
  const raw: Record<Dimension, number> = { structure: 0, ambiguity: 0, decision: 0, learning: 0, transfer: 0 };

  for (const [qId, ansKey] of Object.entries(answers)) {
    const qConfig = SCORING_MAP[qId];
    if (!qConfig) continue;
    const impact = qConfig[ansKey];
    if (!impact) continue;
    for (const [dim, value] of Object.entries(impact)) {
      raw[dim as Dimension] += value as number;
    }
  }
  return raw;
}

// Step B: Scaled scores (0-100)
export function calculateScaledScores(raw: Record<Dimension, number>): Record<Dimension, number> {
  const scaled = {} as Record<Dimension, number>;
  for (const dim of DIMENSIONS) {
    const { min, max } = DIMENSION_CONFIG[dim];
    scaled[dim] = max === min ? 0 : Math.round(((raw[dim] - min) / (max - min)) * 100);
  }
  return scaled;
}

// Step C: Archetype determination
export function determineArchetypes(scaled: Record<Dimension, number>): Archetype[] {
  const matched = ARCHETYPE_RULES.filter((r) => r.check(scaled)).map(({ id, name }) => ({ id, name }));
  return matched.length > 0 ? matched : [{ id: 'GENERALIST', name: '綜合型' }];
}

export interface PersonalityResult {
  rawScores: Record<Dimension, number>;
  scaledScores: Record<Dimension, number>;
  archetypes: Archetype[];
}

export function computePersonalityResult(answers: Record<string, string>): PersonalityResult {
  const rawScores = calculateRawScores(answers);
  const scaledScores = calculateScaledScores(rawScores);
  const archetypes = determineArchetypes(scaledScores);
  return { rawScores, scaledScores, archetypes };
}
