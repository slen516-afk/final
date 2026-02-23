import { mockDelay } from './apiClient';
import { generateMockJobs, getMockJobDetail, mockCoverLetter, JOB_CATEGORIES } from '@/mocks/jobs';
import type { JobData, JobDetailData, JobCategory } from '@/types/job';

// TODO: Replace with API call – GET /jobs?page=
export async function getJobs(page = 1): Promise<JobData[]> {
  await mockDelay();
  return generateMockJobs(page);
}

// TODO: Replace with API call – GET /jobs/:id
export async function getJobDetail(id: string): Promise<JobDetailData> {
  await mockDelay();
  return getMockJobDetail(id);
}

// TODO: Replace with API call – POST /jobs/:id/cover-letter
export async function generateCoverLetter(jobTitle?: string, company?: string): Promise<{ subject: string; body: string }> {
  await mockDelay(2000);
  return mockCoverLetter(jobTitle, company);
}

// TODO: Replace with API call – GET /jobs/categories
export async function getJobCategories(): Promise<JobCategory[]> {
  await mockDelay();
  return JOB_CATEGORIES;
}
