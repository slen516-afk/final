export interface ResumeItem {
  id: number;
  name: string;
  updatedAt: string;
  content: string;
}

export interface OriginalResumeData {
  name: string;
  phone: string;
  email: string;
  address: string;
  education: string;
  experience: string;
  languages: string;
  skills: string;
  certifications: string;
  portfolio: string;
  autobiography: string;
  other: string;
}

export interface ResumeData {
  name: string;
  email: string;
  phone: string;
  linkedin: string;
  github: string;
  professional_summary: string;
  professional_experience: string;
  core_skills: string;
  projects: string;
  education: string;
  autobiography: string;
}

export interface Suggestion {
  section: string;
  original: string;
  optimized: string;
}

/* ── Resume Diagnostic Result (from backend analysis) ── */

export type ATSRiskLevel = '低' | '中' | '高';

export interface CriticalIssue {
  section: string;
  severity: string;
  original_text: string;
  issue_reason: string;
  improvement_direction: string;
}

export interface ResumeDiagnosticResult {
  candidate_positioning: string;
  target_role_gap_summary: string;
  ats_risk_level: ATSRiskLevel;
  screening_outcome_prediction: string;
  overall_strengths: string[];
  overall_weaknesses: string[];
  critical_issues: CriticalIssue[];
  recommended_next_actions: string[];
  suggestions: Suggestion[];
}