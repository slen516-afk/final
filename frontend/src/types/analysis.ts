export interface RadarDataPoint {
  dimension: string;
  user: number;
  target: number;
}

export interface RadarTemplate {
  label: string;
  mascot: string;
  data: RadarDataPoint[];
}

export interface GapItem {
  skill: string;
  current: number;
  target: number;
  priority: string;
}

export interface GapAnalysisData {
  selfAssessment: string;
  aiAssessment: string;
  assessmentExplanation: string;
  matchPercentage: number;
  targetPosition: string;
  cognitiveBias: string;
  summary: string;
  gaps: GapItem[];
}

export interface AnalysisHistoryItem {
  id: number;
  date: string;
  title: string;
  summary: string;
  content: {
    strengths: string[];
    improvements: string[];
    recommendations: string[];
  };
}

export interface LearningResource {
  title: string;
  description: string;
  tags: string[];
  link: string;
}

export interface SideProject {
  name: string;
  technologies: string[];
  highlights: string;
  difficulty: number;
}

/** Payload sent to POST /analysis/generate */
export interface AnalysisRequest {
  user_id: string;
  resume_id: number;
}

/** Full result returned from the analysis API */
export interface AnalysisResult {
  radarTemplates: Record<string, RadarTemplate>;
  gapAnalysis: GapAnalysisData;
  learningResources: LearningResource[];
  sideProjects: SideProject[];
}
