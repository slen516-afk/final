import { mockDelay } from './apiClient';
import { mockAnalysisResult, analysisHistory } from '@/mocks/analysis';
import type { LearningResource, SideProject, AnalysisHistoryItem, AnalysisRequest, AnalysisResult } from '@/types/analysis';

// TODO: Replace with API call – GET /analysis/resources
export async function getLearningResources(): Promise<LearningResource[]> {
  await mockDelay();
  return mockAnalysisResult.learningResources;
}

// TODO: Replace with API call – GET /analysis/projects
export async function getSideProjects(): Promise<SideProject[]> {
  await mockDelay();
  return mockAnalysisResult.sideProjects;
}

// TODO: Replace with API call – GET /analysis/history
export async function getAnalysisHistory(): Promise<AnalysisHistoryItem[]> {
  await mockDelay();
  return analysisHistory;
}

// TODO: Replace mock with real API call – POST /analysis/generate
export async function generateAnalysis(payload: AnalysisRequest): Promise<AnalysisResult> {
  console.log('[analysisService] generateAnalysis called with:', payload);
  await mockDelay(2000);
  return mockAnalysisResult;
}
