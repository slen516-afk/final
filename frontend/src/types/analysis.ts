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

/* ── Report Metadata ── */
export interface ReportMetadata {
  user_id: string;
  timestamp: string;
}

export interface PreliminarySummary {
  core_insight: string;
  industry_insight: string;
  personal_summary: string;
}

/** Ideal dimension scores for a target role (used as radar overlay) */
export interface TargetRadarData {
  dimensions: RadarDimension[];
}

/* ── Payload sent to POST /analysis/generate ── */
export interface AnalysisRequest {
  user_id: string;
  resume_id: number;
}

/* ── Full result returned from the analysis API ── */
export interface AnalysisResult {
  report_metadata: ReportMetadata;
  preliminary_summary: PreliminarySummary;
  radar_chart: RadarChartData;
  target_radar?: TargetRadarData;
  gap_analysis: GapAnalysis;
  learningResources: LearningResource[];
  sideProjects: SideProject[];
}

/* ── Legacy types kept for history feature ── */
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

/** Parse SWOT sections from gap_description text */
export function parseSWOT(text: string): { strengths: string; weaknesses: string; opportunities: string; threats: string; gap: string } {
  const extract = (label: string) => {
    const regex = new RegExp(`【${label}[^】]*】[：:]?\\s*(.+?)(?=【|$)`, 's');
    const match = text.match(regex);
    return match ? match[1].trim() : '';
  };
  return {
    strengths: extract('優勢'),
    weaknesses: extract('劣勢'),
    opportunities: extract('機會'),
    threats: extract('威脅'),
    gap: extract('核心落差'),
  };
}
