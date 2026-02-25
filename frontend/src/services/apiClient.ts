/**
 * API Client – centralised HTTP helper.
 *
 * The base URL is read from Vite env variable VITE_API_BASE_URL.
 * During development it falls back to '/api' (or mock mode).
 *
 * TODO: Replace mock delay with real fetch calls once the backend is ready.
 */

const BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? (window.location.origin + '/api');

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
  // Ensure endpoint doesn't have a leading slash if BASE_URL already has /api
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  const baseUrlWithSlash = BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`;
  const url = new URL(cleanEndpoint, baseUrlWithSlash);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }

  // Get token from localStorage (common for Supabase or custom auth)
  const token = localStorage.getItem('sb-access-token');

  const isFormData = body instanceof FormData;

  const res = await fetch(url.toString(), {
    ...init,
    headers: {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...headers,
    },
    body: isFormData ? (body as FormData) : (body ? JSON.stringify(body) : undefined),
  });

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }

  return res.json() as Promise<T>;
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
