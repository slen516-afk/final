import apiClient, { mockDelay } from './apiClient';
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

// TODO: Replace with real API call – POST /analysis/generate
export async function generateAnalysis(payload: AnalysisRequest): Promise<AnalysisResult> {
  console.log('[analysisService] generateAnalysis called with:', payload);
  try {
    // 1. Submit the gap analysis task to backend API
    const submitResponse = await apiClient.post<{ job_id: string; status: string }>('/gap-analysis', payload);
    const jobId = submitResponse.job_id;
    console.log('[analysisService] Task submitted, ID:', jobId);

    // 2. Poll the status every 3 seconds
    while (true) {
      await new Promise(resolve => setTimeout(resolve, 3000));

      const statusResponse = await apiClient.get<{
        job_id: string;
        status: string;
        result?: AnalysisResult;
        error?: string;
      }>(`/gap-analysis/${jobId}`);

      console.log(`[analysisService] Job ${jobId} status:`, statusResponse.status);

      if (statusResponse.status === 'done' || statusResponse.status === 'SUCCESS') {
        if (statusResponse.result) {
          return statusResponse.result;
        } else {
          throw new Error("Analysis completed but no result returned.");
        }
      } else if (statusResponse.status === 'failed' || statusResponse.status === 'dlq' || statusResponse.status === 'FAILURE') {
        throw new Error(`Analysis failed: ${statusResponse.error || 'Unknown error'}`);
      }
    }
  } catch (error) {
    console.error('[analysisService] Failed to generate analysis:', error);
    throw error;
  }
}
