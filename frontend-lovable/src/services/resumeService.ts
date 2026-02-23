import { mockDelay } from './apiClient';
import { MOCK_RESUMES, mockOriginalResumeData, mockResumeData, mockSuggestions } from '@/mocks/resumes';
import type { ResumeItem, OriginalResumeData, ResumeData, Suggestion } from '@/types/resume';

// TODO: Replace with API call – GET /resumes
export async function getResumes(): Promise<ResumeItem[]> {
  await mockDelay();
  return MOCK_RESUMES;
}

// TODO: Replace with API call – GET /resumes/:id/original
export async function getOriginalResumeData(): Promise<OriginalResumeData> {
  await mockDelay();
  return mockOriginalResumeData;
}

// TODO: Replace with API call – POST /resumes/:id/optimize
export async function getOptimizedResumeData(): Promise<ResumeData> {
  await mockDelay();
  return mockResumeData;
}

// TODO: Replace with API call – GET /resumes/:id/suggestions
export async function getResumeSuggestions(): Promise<Suggestion[]> {
  await mockDelay();
  return mockSuggestions;
}
