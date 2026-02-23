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
