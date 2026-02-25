import { apiClient, mockDelay } from './apiClient';
import { MOCK_RESUMES, mockOriginalResumeData, mockResumeData, mockSuggestions } from '@/mocks/resumes';
import type { ResumeItem, OriginalResumeData, ResumeData, Suggestion } from '@/types/resume';

/**
 * 上傳 PDF 履歷並啟動 OCR 處理
 */
export async function uploadResume(file: File): Promise<{ resume_id: string; message: string }> {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post<{ resume_id: string; message: string }>('/resumes/upload', formData);
}

/**
 * 檢查 OCR 處理狀態與結果
 */
export async function getResumeOcrStatus(resumeId: string): Promise<{
  status: 'processing' | 'completed' | 'failed';
  progress: number;
  ocr_result?: any;
}> {
  return apiClient.get(`/resumes/${resumeId}/status`);
}

// TODO: Replace with API call – GET /resumes
export async function getResumes(): Promise<ResumeItem[]> {
  // 這裡仍保留 Mock，但結構上已準備好對接
  return apiClient.get<ResumeItem[]>('/resumes').catch(() => {
    console.warn('Backend /resumes not found, using mock data');
    return MOCK_RESUMES;
  });
}

// TODO: Replace with API call – GET /resumes/:id/original
export async function getOriginalResumeData(id: number): Promise<OriginalResumeData> {
  return apiClient.get<OriginalResumeData>(`/resumes/${id}/original`).catch(() => {
    return mockOriginalResumeData;
  });
}

// TODO: Replace with API call – POST /resumes/:id/optimize
export async function getOptimizedResumeData(id: number): Promise<ResumeData> {
  return apiClient.post<ResumeData>(`/resumes/${id}/optimize`, {}).catch(() => {
    return mockResumeData;
  });
}

// TODO: Replace with API call – GET /resumes/:id/suggestions
export async function getResumeSuggestions(id: number): Promise<Suggestion[]> {
  return apiClient.get<Suggestion[]>(`/resumes/${id}/suggestions`).catch(() => {
    return mockSuggestions;
  });
}

/**
 * 建立履歷 (手動填寫表單)
 */
export async function createResumeFromForm(data: any): Promise<{ resume_id: number; status: string }> {
  // 目前後端 API 是 /api/resumes/form (POST)
  // 根據 backend/flask/api/resume.py
  return apiClient.post<{ resume_id: number; status: string }>('/resumes/form', {
    survey_id: 1, // Mocked survey_id
    structured_data: data
  });
}
