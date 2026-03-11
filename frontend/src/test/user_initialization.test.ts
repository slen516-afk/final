import { describe, it, expect, beforeEach, vi } from 'vitest';
import { uploadResumeAPI, saveQuestionnaireResponseAPI, savePersonalityAPI } from '../services/api';

/**
 * 用戶資料初始化測試腳本
 * 包含：上傳履歷、填寫職涯偏好問卷、填寫人格特質問卷
 * 
 * 執行指令: npm test src/test/user_initialization.test.ts
 */

describe('User Initialization Integration Test', () => {
    const TEST_TOKEN = 'mock_token_for_user_init_test';

    beforeEach(() => {
        // 設置 API 基礎路徑
        vi.stubEnv('VITE_API_BASE_URL', 'http://127.0.0.1:8000/api');

        // 模擬 localStorage 中的 Token
        window.localStorage.setItem('accessToken', TEST_TOKEN);
        window.localStorage.setItem('token', TEST_TOKEN);
    });

    describe('1. 履歷上傳測試', () => {
        it('1. 履歷上傳測試 > 應該能成功發起履歷上傳請求', async () => {
            const blob = new Blob(['mock content'], { type: 'application/pdf' });
            const file = new File([blob], 'test-resume.pdf', { type: 'application/pdf' });
            const result = await uploadResumeAPI(file);
            console.log('✅ uploadResumeAPI 回應:', result);

            expect(result.status).toBe('success');
            expect(result).toHaveProperty('resume_id');
        });
    });

    describe('2. 職涯偏好問卷測試', () => {
        it('應該能成功提交職涯偏好問卷', async () => {
            const mockSurveyData = {
                module_a: { goal: '前端開發工程師' },
                module_b: { industry: '科技業' },
                module_c: { skills: ['React', 'TypeScript'] },
                module_d: { experience: 'Junior' }
            };

            const response = await saveQuestionnaireResponseAPI(mockSurveyData);
            console.log('✅ saveQuestionnaireResponseAPI 回應:', response);
            expect(response).toBeDefined();
        });
    });

    describe('3. 人格特質問卷測試', () => {
        it('應該能成功提交人格特質問卷', async () => {
            const mockPersonalityData = {
                trait_calculation_debug: {},
                trait_normalized_scores: { openness: 90 },
                primary_archetype: 'Architect',
                secondary_archetypes: ['Thinker'],
                trait_created_at: new Date().toISOString()
            };

            const response = await savePersonalityAPI(mockPersonalityData);
            console.log('✅ savePersonalityAPI 回應:', response);
            expect(response).toBeDefined();
        });
    });

});
