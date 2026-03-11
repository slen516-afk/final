import { describe, it, expect, beforeEach, vi } from 'vitest';
import { startGapAnalysis, pollGapAnalysisStatus } from '../services/analysisService';

/**
 * 前後端串接測試 (Gap Analysis)
 * 
 * 執行指令: npm test src/test/gap_analysis_connection.test.ts
 * 
 * 注意: 
 * 1. 確保後端 Flask Server 已啟動 (預設 http://localhost:8000/api)
 * 2. 確保資料庫中有測試使用者，且已完成問卷與人格測驗。
 * 3. 測試前需於 localStorage 設置有效的 accessToken。
 */

describe('Gap Analysis API Connection Integration Test', () => {
    // 模擬 Token (請在實際測試時替換為有效 Token)
    const TEST_TOKEN = 'mock_token_for_connection_test';

    beforeEach(() => {
        // 強制將 API Base URL 指向後端實際位址 (解決 Vitest/jsdom 預設連到 3000 的問題)
        vi.stubEnv('VITE_API_BASE_URL', 'http://127.0.0.1:8000/api');

        // 在 jsdom 模擬環境中設置 localStorage
        window.localStorage.setItem('accessToken', TEST_TOKEN);
    });

    it('應該能成功發送 POST /gap-analysis 請求', async () => {
        try {
            const response = await startGapAnalysis();
            console.log('✅ startGapAnalysis 成功回應:', response);

            expect(response).toHaveProperty('job_id');
            expect(response.status).toBe('queued');
        } catch (error: any) {
            // 如果回傳 401/403，代表串接成功但權限不足
            if (error.message.includes('401') || error.message.includes('403')) {
                console.warn('⚠️ 串接成功，但權限驗證失敗 (可能是 Token 過期或無效):', error.message);
            } else if (error.message.includes('404')) {
                console.warn('⚠️ 串接成功，但後端找不到相關問卷資料 (需先填寫問卷):', error.message);
            } else {
                console.error('❌ startGapAnalysis 串接失敗:', error.message);
                throw error;
            }
        }
    });

    it('應該能成功發送 GET /gap-analysis/:job_id 請求', async () => {
        const fakeJobId = 'job_test_12345';
        try {
            const response = await pollGapAnalysisStatus(fakeJobId);
            console.log('✅ pollGapAnalysisStatus 成功回應:', response);
            expect(response).toBeDefined();
        } catch (error: any) {
            if (error.message.includes('404')) {
                console.log('✅ 串接成功: 後端正確回傳 404 Job Not Found (表示 API 路徑正確)');
            } else if (error.message.includes('401') || error.message.includes('403')) {
                console.warn('⚠️ 串接成功: 但權限驗證失敗:', error.message);
            } else {
                console.error('❌ pollGapAnalysisStatus 串接失敗:', error.message);
                throw error;
            }
        }
    });
});
