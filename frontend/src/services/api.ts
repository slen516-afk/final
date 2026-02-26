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