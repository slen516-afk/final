import apiClient from './apiClient';

export interface AuthResponse {
    user: {
        id: string;
        role: string;
    };
    auth: {
        accessToken: string;
        refreshToken: string;
        expiresIn: number;
    };
}

/**
 * 用戶登入
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
    const data = await apiClient.post<AuthResponse>('/auth/login', { email, password });

    // 儲存 Token
    if (data.auth?.accessToken) {
        localStorage.setItem('accessToken', data.auth.accessToken);
        localStorage.setItem('refreshToken', data.auth.refreshToken);
    }

    return data;
}

/**
 * 用戶註冊
 */
export async function register(email: string, password: string, username: string) {
    return apiClient.post('/auth/register', { email, password, username });
}

/**
 * 登出
 */
export function logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('token');
}
