export interface JobData {
  id: number;
  title: string;
  description: string;
  company: string;
  city: string;
  salary: string;
  industry: string;
  externalUrl: string;
}

/** Backend recommendation API response per job */
export interface RecommendedJob {
  id: string;
  title: string;
  company: string;
  industry: string;
  location: string;
  externalUrl: string;
  salary_range: string;
  match_score: string | number;
  recommendation_reason: string;
  strengths: string;
  weaknesses: string;
  interview_tips: string;
  isMock?: boolean;
}

export interface RecommendedJobDetail extends RecommendedJob {
  description: string;
  requirements: string[];
}

export interface JobDetailData {
  id: number;
  title: string;
  company: string;
  industry: string;
  city: string;
  address: string;
  salary: string;
  description: string;
  requirements: string[];
  benefits: string[];
  skills: string[];
  externalUrl: string;
}

export interface SkillCard {
  name: string;
  tags: string[];
  description: string;
}

export interface SubCategory {
  label: string;
  skills: SkillCard[];
}

export interface JobCategory {
  label: string;
  subcategories: SubCategory[];
}
