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
