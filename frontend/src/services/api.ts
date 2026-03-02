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



// 取得職缺推薦 (POST 請求) -> 🌟 已經換成 V2 引擎
export const getJobRecommendationsAPI = async (surveyData: any) => {
    try {
        const response = await fetch('/api/jobs/v2/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(surveyData),
        });

        if (!response.ok) {
            throw new Error(`API 請求失敗，狀態碼: ${response.status}`);
        }

        return await response.json();
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


