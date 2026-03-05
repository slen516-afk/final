import { useState, useCallback, useRef, useEffect } from 'react';
import { taskService } from '../services/api';

export const useAsyncTask = (pollingInterval = 2000) => {
    const [status, setStatus] = useState('IDLE'); // IDLE, PENDING, SUCCESS, FAILURE
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [progressMessage, setProgressMessage] = useState('');
    const timerRef = useRef(null);

    const stopPolling = useCallback(() => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
    }, []);

    useEffect(() => {
        return () => {
            stopPolling();
        };
    }, [stopPolling]);

    /**
     * 執行任務
     * @param {string} taskType - 任務類型
     * @param {object} payload - 任務參數 ( survey_json: '...' )
     */

    const runTask = useCallback(async (taskType, payload) => {
        // 重置狀態
        setStatus('PENDING');
        setError(null);
        setResult(null);
        setProgressMessage('啟動任務中...');
        stopPolling();

        try {
            // 1. 觸發非同步任務
            const res = await taskService.submit(taskType, payload);
            const { task_id } = res.data;

            // 2. 開始輪詢
            timerRef.current = setInterval(async () => {
                try {
                    const statusRes = await taskService.getStatus(task_id);
                    const { state, result: taskResult, message } = statusRes.data;

                    // 更新進度訊息，如果有
                    if (message) setProgressMessage(message);

                    if (state === 'SUCCESS') {
                        setStatus('SUCCESS');
                        setResult(taskResult);
                        stopPolling();
                    } else if (state === 'FAILURE' || state === 'REVOKED') {
                        setStatus('FAILURE');
                        setError('任務執行失敗或被取消');
                        stopPolling();
                    }
                    // 如果是 PENDING 或 RECEIVED，就繼續等下次輪詢
                } catch (err) {
                    setStatus('FAILURE');
                    setError('查詢狀態時發生錯誤');
                    stopPolling();
                }
            }, pollingInterval);

        } catch (err) {
            setStatus('FAILURE');
            setError(err.response?.data?.message || err.response?.data?.error || '無法啟動任務');
        }
    }, [pollingInterval]);

    return { runTask, status, result, error, progressMessage, isProcessing: status === 'PENDING' };
};