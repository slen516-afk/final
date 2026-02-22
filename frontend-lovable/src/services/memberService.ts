import { mockDelay } from './apiClient';
import { mockUserId, mockProfile } from '@/mocks/member';
import type { UserProfile } from '@/types/member';

// TODO: Replace with API call – GET /members/me
export async function getMyProfile(): Promise<UserProfile> {
  await mockDelay();
  return mockProfile;
}

// TODO: Replace with API call – GET /members/me/id
export async function getMyUserId(): Promise<string> {
  await mockDelay();
  return mockUserId;
}

// TODO: Replace with API call – PUT /members/me
export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  await mockDelay();
  return { ...mockProfile, ...data };
}
