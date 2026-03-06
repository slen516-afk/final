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
    const response = await apiClient.post('/resume_process/save', payload, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
    return response.data;
};

// 🌟 獲取特定使用者的履歷清單 (解決陳浩宇問題的核心)
export const fetchUserResumesAPI = async (userId: number) => {
    try {
        // 使用 apiClient 確保帶上攔截器
        const response = await apiClient.get(`${RESUME_PREFIX}/list/${userId}`);
        if (response.data && response.data.status === "success") {
            return response.data.data;
        }
        return [];
    } catch (error) {
        console.error("fetchUserResumesAPI 發生錯誤:", error);
        throw error;
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
    process: (id: string) => apiClient.post(`/resume_process/${id}`),
};

// 🌟 預設導出 apiClient
export default apiClient;