'use client';

import { Category } from '@/types';

// ✨ 统一使用大写，直接覆盖原作者的旧定义，和底下的渲染完美对接
export const CATEGORIES = ['全部', '中国', '美国', '日本', '欧洲', '中国台湾', '韩国', '澳大利亚', '国际/多边'];
export const TAGS: string[] = []; // 彻底清空标签

interface HeaderProps {
  selectedCategory: Category;
  onCategoryChange: (category: Category) => void;
  selectedTag?: string;
  onTagChange?: (tag: string) => void;
}

export default function Header({ selectedCategory, onCategoryChange }: HeaderProps) {
  const today = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-[#1e3a5f]">
            Semi Geopolitics Papers
          </h1>
          <span className="text-sm text-gray-500">
            今日更新: {today}
          </span>
        </div>
        
        <div className="mb-1">
          <div className="text-xs text-gray-500 mb-2 font-medium">🎯 核心阵营与国家筛选</div>
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {CATEGORIES.map((category) => (
              <button
                key={category}
                onClick={() => onCategoryChange(category as Category)}
                className={`px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
                  selectedCategory === category
                    ? 'bg-[#1e3a5f] text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
        
        {/* ✂️ 已经彻底移除了原本第二排的 TAGS 渲染区域，界面现在绝无死角 */}
      </div>
    </header>
  );
}
