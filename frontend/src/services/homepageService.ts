import { mockDelay } from './apiClient';
import { heroStats, news } from '@/mocks/homepage';
import type { HeroStat, NewsItem } from '@/types/homepage';

// TODO: Replace with API call – GET /homepage/stats
export async function getHeroStats(): Promise<HeroStat[]> {
  await mockDelay();
  return heroStats;
}

// TODO: Replace with API call – GET /homepage/news
export async function getNews(): Promise<NewsItem[]> {
  await mockDelay();
  return news;
}
