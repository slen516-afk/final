import type { AnalysisResult } from '@/types/analysis';

/**
 * 呼叫後端 Flask + CrewAI 進行職涯與履歷分析
 */
export const generateAnalysis = async (params: { user_id: string, resume_id: number | string }): Promise<AnalysisResult> => {
  console.log("🚀 [步驟 1] 準備呼叫後端 API，參數:", params);

  try {
    console.log("⏳ [步驟 2] 發送 POST 請求中... (CrewAI 運算可能需要 1~3 分鐘，請耐心等候)");

    // ⚠️ 呼叫你後端的 Flask 路由
    // ... 其他代碼 ...

    // 🌟 修正點：請對齊你 Flask Blueprint 的前綴 (假設是 /api/resume_processing) 
    // 以及我們剛剛改的路徑 /career-analyze
    // ... 其他代碼 ...

    // 🌟 請將網址改為：/api/resume_processing/career-analyze
    // 這對應了 Flask 的 Blueprint 前綴 與 我們的路由名稱
    const response = await fetch('/api/resume_process/career-analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: String(params.user_id),
        resume_id: Number(params.resume_id)
      })
    });

    // ... 其他代碼 ...

    // ... 其他代碼 ...

    console.log("📥 [步驟 3] 收到後端回應，狀態碼 HTTP:", response.status);

    const text = await response.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (err) {
      throw new Error(`後端沒有回傳正確的 JSON 格式！原始內容為: ${text.substring(0, 50)}`);
    }

    if (!response.ok) {
      throw new Error(data.error || data.message || `API 請求失敗 (狀態碼: ${response.status})`);
    }

    console.log("✅ [步驟 5] 成功解析 CrewAI 真實分析報告:", data);
    return data as AnalysisResult;

  } catch (error) {
    console.error("🚨 [步驟 6] 呼叫分析 API 發生錯誤:", error);
    throw error;
  }
};