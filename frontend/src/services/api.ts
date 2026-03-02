// src/services/api.ts

/**
 * 上傳履歷給後端 OCR 處理的 API
 * @param {File} file - 使用者選擇的履歷檔案 (PDF/Word/圖片等)
 */
export const uploadResumeAPI = async (file: File) => {
    // 1. 把檔案包裝成可以透過網路傳輸的表單格式
    const formData = new FormData();

    // 注意！這裡的 "file" 必須跟你 Flask 後端 request.files['file'] 的名字一模一樣
    formData.append("file", file);

    try {
        // 2. 透過我們剛剛在 vite.config.ts 設定好的 Proxy 傳達室，送往後端
        const response = await fetch("/api/resume_process/upload", {
            method: "POST",
            body: formData, // 瀏覽器會自動幫我們設定好 multipart/form-data 標頭，不用自己寫！
        });

        if (!response.ok) {
            throw new Error(`伺服器回應錯誤狀態碼: ${response.status}`);
        }

        // 3. 拿到後端分析完的結果並回傳
        const data = await response.json();
        return data;

    } catch (error) {
        console.error("上傳履歷時發生錯誤:", error);
        throw error;
    }
};

// 根據問卷結果獲取推薦職缺 (POST 請求)
export const getJobRecommendationsAPI = async (questionnaireData: any, page: number = 1) => {
    try {
        const response = await fetch(`/api/jobs/recommendations?page=${page}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(questionnaireData),
        });

        if (!response.ok) {
            throw new Error(`伺服器回應錯誤: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("取得職缺推薦失敗:", error);
        throw error;
    }
};

// 取得專屬 Side Project 推薦 (POST 請求)
export const getProjectSuggestionsAPI = async (userData: any = {}) => {
    try {
        // 假設你的 Flask 藍圖有加 /api 前綴
        const response = await fetch(`/api/projects/suggestions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // 這裡可以把使用者填過的問卷資料傳過去，讓 AI 參考
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            throw new Error(`伺服器回應錯誤: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("取得 Side Project 推薦失敗:", error);
        throw error;
    }
};

// 取得學習資源推薦 (POST 請求)
export const getLearningRecommendationsAPI = async (userData: any = {}) => {
    try {
        const response = await fetch(`/api/learning/recommendations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            throw new Error(`伺服器回應錯誤: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("取得學習資源推薦失敗:", error);
        throw error;
    }
};

// 取得單筆職缺詳細資料
export const getJobDetailAPI = async (jobId: string) => {
    // 記得把 URL 換成你實際的後端位址 (例如 http://localhost:8000 或是 /api )
    const response = await fetch(`/api/jobs/${jobId}`);
    if (!response.ok) {
        throw new Error('取得職缺詳細資料失敗');
    }
    return response.json();
};


// 非同步任務處理
import axios from 'axios';
import { apiClient } from './apiClient';

// 建立 axios 實例
const api = axios.create({
    baseURL: '/api',
});

// 攔截器 : 統一處理JWT token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// 定義 Response 介面
export interface TaskStatusResponse<T = any> {
    task_id: string;
    state: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE' | 'REVOKED';
    result: T | null;
    message?: string; // 對應 tasks.py 中的 meta msg
}
// 針對不同模組導出 Service
export const taskService = {
    /**
     * 提交非同步任務
     * @param {string} taskType - 任務類型 (e.g., 'career_analysis', 'resume_ocr')
     * @param {object} payload - 任務所需的參數內容
     */
    submit: (taskType: string, payload: any) => {
        return apiClient.post<{ task_id: string }>('/tasks/submit', {
            task_type: taskType,
            payload: payload
        });
    },
    /**
         * 取得任務狀態
         * @param taskId 任務 ID
         */
    getStatus: (taskId) => {
        return apiClient.get<TaskStatusResponse<T>>(`/tasks/status/${taskId}`);
    }
};
export const resumeService = {
    getAll: () => apiClient.get('/resumes'), // /api/resumes
    process: (id: string) => apiClient.post(`/resume_process/${id}`), // /api/resume_process/{id}
};

export default apiClient;