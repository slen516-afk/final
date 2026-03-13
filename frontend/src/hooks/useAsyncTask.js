import { useState, useCallback, useRef, useEffect } from 'react';
import { taskService } from '../services/api';

export const useAsyncTask = (pollingInterval = 2000) => {
    const [status, setStatus] = useState('IDLE'); // IDLE, PENDING, SUCCESS, FAILURE
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [progressMessage, setProgressMessage] = useState('');
    const [progress, setProgress] = useState(0); // 0-100
    const timerRef = useRef(null);
    const pollCountRef = useRef(0);

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
        setProgress(0);
        pollCountRef.current = 0;
        setProgressMessage('啟動任務中...');
        stopPolling();

        try {
            // 1. 觸發非同步任務
            const res = await taskService.submit(taskType, payload);
            const { task_id } = res.data;

            // 2. 開始輪詢
            timerRef.current = setInterval(async () => {
                pollCountRef.current += 1;
                
                // 🌟 每 3 次輪詢推進一次進度條 (例如增加 5%)
                if (pollCountRef.current % 3 === 0) {
                    setProgress(prev => {
                        const next = prev + 10;
                        return next > 95 ? 95 : next; // 最高停在 95%
                    });
                }

                try {
                    const statusRes = await taskService.getStatus(task_id);
                    const { state, result: taskResult, message } = statusRes.data;

                    // 更新進度訊息，如果有
                    if (message) setProgressMessage(message);

                    if (state === 'SUCCESS') {
                        setStatus('SUCCESS');
                        setResult(taskResult);
                        setProgress(100);
                        stopPolling();
                    } else if (state === 'FAILURE' || state === 'REVOKED') {
                        setStatus('FAILURE');
                        setError('任務執行失敗或被取消');
                        stopPolling();
                    }
                    // 如果是 PENDING 或 RECEIVED，就繼續等下次輪詢
                } catch (err) {
                    // 容錯：如果是網路瞬斷，不立刻報錯，等下次
                    console.warn('輪詢發生錯誤，嘗試繼續...', err);
                }
            }, pollingInterval);

        } catch (err) {
            setStatus('FAILURE');
            setError(err.response?.data?.message || err.response?.data?.error || '無法啟動任務');
        }
    }, [pollingInterval, stopPolling]);

    return { runTask, status, result, error, progressMessage, progress, isProcessing: status === 'PENDING' };
};