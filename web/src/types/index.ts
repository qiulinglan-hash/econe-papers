export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  categories: string[];
  published: string;
  updated: string;
  pdfUrl: string;
  
  chineseTitle: string;
  chineseAbstract: string;
  researchField: string;
  keywords: string[];
  tags?: string[];
  scores: {
    overall: number;
    novelty: number;
    quality: number;
    readability: number;
  };
  summary: string;
}

export interface DayPapers {
  date: string;
  papers: Paper[];
  total: number;
}

export type Category = '全部' | '中国' | '美国' | '日本' | '欧洲' | '中国台湾' | '韩国' | '澳大利亚' | '国际/多边';

export const CATEGORIES = ['全部', '中国', '美国', '日本', '欧洲', '中国台湾', '韩国', '澳大利亚', '国际/多边'] as const;
