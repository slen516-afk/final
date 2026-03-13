import { describe, it, expect, beforeEach, vi } from 'vitest';
import { startGapAnalysis, pollGapAnalysisStatus, generateAnalysis } from '../services/analysisService';

/**
 * 職能圖譜服務測試腳本
 * 測試項包含：啟動落差分析、輪詢分析狀態、完整分析流程
 * 
 * 執行指令: npm test src/test/competency_map.test.ts
 * 
 * 注意：
 * 完整分析流程 (generateAnalysis) 可能會耗時較長，取決於後端處理速度。
 */

describe('Competency Map (職能圖譜) Service Test', () => {
    const TEST_TOKEN = 'mock_token_for_competency_map_test';

    beforeEach(() => {
        vi.stubEnv('VITE_API_BASE_URL', 'http://127.0.0.1:8000/api');
        window.localStorage.setItem('accessToken', TEST_TOKEN);
    });

    it('應該能成功發起職能落差分析任務 (startGapAnalysis)', async () => {
        const response = await startGapAnalysis();
        console.log('✅ startGapAnalysis 成功回應:', response);

        expect(response).toHaveProperty('job_id');
        expect(['queued', 'processing', 'done']).toContain(response.status);
    });

    it('應該能成功查詢分析狀態 (pollGapAnalysisStatus)', async () => {
        const testJobId = 'test_job_id_123';
        const response = await pollGapAnalysisStatus(testJobId);
        console.log('✅ pollGapAnalysisStatus 成功回應:', response);
        expect(response).toHaveProperty('status');
    });

    it('應該能執行完整分析流程 (generateAnalysis)', async () => {
        console.log('🚀 開始執行完整分析流程 (包含輪詢)...');
        const result = await generateAnalysis();
        console.log('✅ generateAnalysis 完整結果:', result);

        expect(result).toHaveProperty('radar_chart');
        expect(result).toHaveProperty('gap_analysis');
    }, 60000); // 設定 60 秒超時
});
