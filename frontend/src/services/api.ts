import axios from 'axios';
import apiClient from './apiClient'; // 🌟 統一從這裡引入 apiClient

// --- 常數定義 ---
const RESUME_PREFIX = '/resume_process';
const API_BASE_URL = 'http://127.0.0.1:8000/api/resume_process';

// --- 履歷相關 API (使用 fetch 寫法保留) ---
export const uploadResumeAPI = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
        const response = await fetch("/api/resume_process/upload", {
            method: "POST",
            body: formData,
        });
        if (!response.ok) throw new Error(`伺服器回應錯誤狀態碼: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("上傳履歷時發生錯誤:", error);
        throw error;
    }
};

// 🌟 修正 saveResumeAPI 的 axios 呼叫 (使用底下的 api 實例)
export const saveResumeAPI = async (payload: any) => {
    // 🌟 網址改成 /resume_process/save，跟你的 Flask 完全對齊！
    const response = await apiClient.post<any>('/resume_process/save', payload, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
    return response;
};

// 🌟 獲取特定使用者的履歷清單 (解決陳浩宇問題的核心)
export const fetchUserResumesAPI = async (userId: number | string) => {
    try {
        console.log(`🚀 [API] 正在請求使用者 ${userId} 的履歷清單...`);
        const response = await apiClient.get<any>(`${RESUME_PREFIX}/list/${userId}`);
        console.log("📦 [API] 原始回應內容:", response);

        // 🌟 超級容錯解析
        if (!response) return [];

        // 格式 A: { status: 'success', data: [...] } - 您分享的格式
        if (response.status === "success" && Array.isArray(response.data)) {
            return response.data;
        }

        // 格式 B: 直接是陣列 [...]
        if (Array.isArray(response)) return response;

        // 格式 C: Axios 風格 { data: { status: 'success', data: [...] } }
        if (response.data && response.data.status === "success" && Array.isArray(response.data.data)) {
            return response.data.data;
        }

        // 格式 D: { data: [...] } 但沒有 status
        if (Array.isArray(response.data)) return response.data;

        console.warn("⚠️ [API] 無法辨識的履歷資料格式:", response);
        return [];
    } catch (error) {
        console.error("❌ [API] fetchUserResumesAPI 失敗:", error);
        return [];
    }
};

// --- 職缺與推薦相關 API (保留原本 fetch 寫法) ---
export const getJobRecommendationsAPI = async (surveyData: any) => {
    const response = await fetch('/api/jobs/v2/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(surveyData),
    });
    if (!response.ok) throw new Error(`API 請求失敗: ${response.status}`);
    return await response.json();
};

export const getProjectSuggestionsAPI = async (userData: any = {}) => {
    const response = await fetch(`/api/projects/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
    });
    if (!response.ok) throw new Error(`伺服器回應錯誤: ${response.status}`);
    return await response.json();
};

export const getLearningRecommendationsAPI = async (userData: any = {}) => {
    const response = await fetch(`/api/learning/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
    });
    if (!response.ok) throw new Error(`伺服器回應錯誤: ${response.status}`);
    return await response.json();
};

export const getJobDetailAPI = async (jobId: string) => {
    const response = await fetch(`/api/jobs/${jobId}`);
    if (!response.ok) throw new Error('取得職缺詳細資料失敗');
    return await response.json();
};

// --- Cover Letter 相關 API ---
export const generateCoverLetterAPI = async (payload: { job_id: string; resume_id?: string; optimization_id?: string }) => {
    try {
        // 使用 apiClient 自動帶入 /api 前綴與 Token
        const response = await apiClient.post<any>('/cover_letter/generate', payload);
        return response;
    } catch (error) {
        console.error("generateCoverLetterAPI 發生錯誤:", error);
        throw error;
    }
};

// --- 問卷與人格特質相關 API ---
export const saveQuestionnaireAPI = async (payload: any) => {
    const response = await apiClient.post('/questionnaire-response', payload);
    return response;
};

export const savePersonalityAPI = async (payload: any) => {
    const response = await apiClient.post('/personality', payload);
    return response;
};

// --- Axios 實例與攔截器設定 (合併重複定義) ---
const api = axios.create({
    baseURL: '/api',
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// --- 介面定義 ---
export interface TaskStatusResponse<T = any> {
    task_id: string;
    state: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED';
    result: T | null;
    message?: string;
}

// --- 服務物件導出 (保留原本邏輯) ---
export const taskService = {
    submit: (taskType: string, payload: any) => {
        return apiClient.post<{ task_id: string }>('/tasks/submit', {
            task_type: taskType,
            payload: payload
        });
    },
    // 修正了泛型 T 的使用方式
    getStatus: <T = any>(taskId: string) => {
        return apiClient.get<TaskStatusResponse<T>>(`/tasks/status/${taskId}`);
    }
};

export const resumeService = {
    getAll: () => apiClient.get('/resumes'),
    process: (id: string) => apiClient.post(`/resume_process/${id}`, {}),
};

// 🌟 預設導出 apiClient
export default apiClient;