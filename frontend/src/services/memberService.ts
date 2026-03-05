import { apiClient } from './apiClient';
import type { UserProfile } from '@/types/member';

/**
 * 取得當前使用者的個人資料
 * 對應後端: GET /api/auth/profile
 */
export async function getMyProfile(): Promise<UserProfile> {
  return apiClient.get<UserProfile>('/auth/profile');
}

/**
 * 取得當前使用者的資料庫 ID
 */
export async function getMyUserId(): Promise<string> {
  const profile = await getMyProfile();
  // 優先嘗試取得資料庫 user_id，否則回傳 id
  const idValue = (profile as any).user_id || (profile as any).id;
  return idValue ? idValue.toString() : '';
}

/**
 * 更新個人資料
 * 對應後端: PUT /api/auth/profile
 */
export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  return apiClient.put<UserProfile>('/auth/profile', data);
}

/**
 * 上傳個人大頭貼
 * 對應後端: POST /api/auth/upload-avatar
 */
export async function uploadAvatar(file: File): Promise<{ avatar_url: string }> {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post<{ avatar_url: string }>('/auth/upload-avatar', formData);
}

