import { mockDelay } from './apiClient';
import { radarTemplates, gapAnalysis, learningResources, sideProjects, analysisHistory } from '@/mocks/analysis';
import type { RadarTemplate, GapAnalysisData, LearningResource, SideProject, AnalysisHistoryItem } from '@/types/analysis';

// TODO: Replace with API call – GET /analysis/radar
export async function getRadarTemplates(): Promise<Record<string, RadarTemplate>> {
  await mockDelay();
  return radarTemplates;
}

// TODO: Replace with API call – GET /analysis/gap
export async function getGapAnalysis(): Promise<GapAnalysisData> {
  await mockDelay();
  return gapAnalysis;
}

// TODO: Replace with API call – GET /analysis/resources
export async function getLearningResources(): Promise<LearningResource[]> {
  await mockDelay();
  return learningResources;
}

// TODO: Replace with API call – GET /analysis/projects
export async function getSideProjects(): Promise<SideProject[]> {
  await mockDelay();
  return sideProjects;
}

// TODO: Replace with API call – GET /analysis/history
export async function getAnalysisHistory(): Promise<AnalysisHistoryItem[]> {
  await mockDelay();
  return analysisHistory;
}
