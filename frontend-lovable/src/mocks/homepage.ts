import type { HeroStat, NewsItem } from '@/types/homepage';

// TODO: Replace with API call (CMS)
export const heroStats: HeroStat[] = [
  { value: '10K+', label: '刊登中職缺' },
  { value: '90%', label: '匹配準確率' },
  { value: '300+', label: '合作企業' },
];

// TODO: Replace with API call (CMS)
export const news: NewsItem[] = [
  {
    date: '19',
    month: 'Mar',
    title: '公告：職星領航員服務正式上線',
    description: '為已經蓄勢待發的你，推薦適合職缺並優化歷程，助您在職涯路上更進一步',
  },
  {
    date: '23',
    month: 'Feb.',
    title: '動態：職星領航員服務將於三月中旬登場',
    description: '感謝到試用戶的積極參與及寶貴意見，我們將持續優化核心服務品質，並預計於三月中旬正式上線。',
  },
  {
    date: '10',
    month: 'Feb.',
    title: '動態：測試用戶募集中',
    description: '歡迎有興趣的用戶報名參與測試，提供寶貴意見',
  },
];
