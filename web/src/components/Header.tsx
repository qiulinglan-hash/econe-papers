'use client';

import { Category } from '@/types';

// 1. 修改第一排分类为核心地缘政治国家/地区
export const categories = ['全部', '中国', '美国', '日本', '欧洲', '中国台湾', '韩国', '澳大利亚', '国际/多边'];

// 2. 将第二排的旧经济学标签直接改成空数组，彻底在界面上抹去它们
export const tags = [];

interface HeaderProps {
  selectedCategory: Category;
  onCategoryChange: (category: Category) => void;
  selectedTag?: string;
  onTagChange?: (tag: string) => void;
}

export default function Header({ selectedCategory, onCategoryChange, selectedTag = '全部标签', onTagChange }: HeaderProps) {
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
            Econe Papers
          </h1>
          <span className="text-sm text-gray-500">
            今日更新: {today}
          </span>
        </div>
        
        <div className="mb-3">
          <div className="text-xs text-gray-500 mb-1">分类</div>
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
        
        {onTagChange && (
          <div className="overflow-x-auto pb-2 -mx-4 px-4">
            <div className="flex gap-2 whitespace-nowrap">
              {TAGS.map((tag) => (
                <button
                  key={tag}
                  onClick={() => onTagChange(tag)}
                  className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                    selectedTag === tag
                      ? 'bg-[#d4a574] text-white'
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
