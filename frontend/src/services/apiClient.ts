/**
 * API Client – centralised HTTP helper.
 *
 * The base URL is read from Vite env variable VITE_API_BASE_URL.
 * During development it falls back to '/api' (or mock mode).
 *
 * TODO: Replace mock delay with real fetch calls once the backend is ready.
 */

const BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? '/api';

/** Simulate network latency for mock mode (ms) */
const MOCK_DELAY = 400;

export const mockDelay = (ms = MOCK_DELAY) =>
  new Promise<void>((resolve) => setTimeout(resolve, ms));

/* ── Generic request helper (ready for real backend) ── */

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  params?: Record<string, string>;
}

async function request<T>(
  endpoint: string,
  { body, params, headers, ...init }: RequestOptions = {},
): Promise<T> {
  // 修正：如果 BASE_URL 是相對路徑（如 /api），new URL() 會報錯。
  // 我們需要提供一個絕對的 Base，或是手動處理。
  const absoluteBase = BASE_URL.startsWith('http')
    ? BASE_URL
    : `${window.location.origin}${BASE_URL.startsWith('/') ? '' : '/'}${BASE_URL}`;

  // 確保 base 以斜線結尾，避免 new URL 替換掉最後一段路徑
  const baseWithSlash = absoluteBase.endsWith('/') ? absoluteBase : `${absoluteBase}/`;
  
  // 確保 endpoint 不會重複包含 base 資料，且路徑格式正確 (移除開頭斜線)
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  const url = new URL(cleanEndpoint, baseWithSlash);

  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }

  const isFormData = body instanceof FormData;
  const contentTypeHeader = isFormData ? {} : { 'Content-Type': 'application/json' };

  // 自動從 localStorage 取得 Token
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  const authHeader = token ? { 'Authorization': `Bearer ${token}` } : {};

  try {
    const res = await fetch(url.toString(), {
      ...init,
      headers: {
        ...contentTypeHeader,
        ...authHeader,
        ...headers,
      },
      body: isFormData ? (body as FormData) : (body ? JSON.stringify(body) : undefined),
    });

    if (!res.ok) {
      if (res.status === 401) {
        console.warn("Detected 401 Unauthorized - clearing session token");
        localStorage.removeItem('accessToken');
        localStorage.removeItem('token');
        // 可加強：如果是 401 且需要強迫重新整理
        // window.location.reload(); 
      }
      throw new Error(`API ${res.status}: ${res.statusText}`);
    }

    return await res.json() as T;
  } catch (err) {
    throw err;
  }
}

export const apiClient = {
  get: <T>(endpoint: string, opts?: RequestOptions) =>
    request<T>(endpoint, { ...opts, method: 'GET' }),

  post: <T>(endpoint: string, body: unknown, opts?: RequestOptions) =>
    request<T>(endpoint, { ...opts, method: 'POST', body }),

  put: <T>(endpoint: string, body: unknown, opts?: RequestOptions) =>
    request<T>(endpoint, { ...opts, method: 'PUT', body }),

  delete: <T>(endpoint: string, opts?: RequestOptions) =>
    request<T>(endpoint, { ...opts, method: 'DELETE' }),
};

export default apiClient;
