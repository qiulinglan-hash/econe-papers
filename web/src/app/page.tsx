'use client';

import { useState, useEffect, useCallback } from 'react';
import DaySection from '@/components/DaySection';
import Footer from '@/components/Footer';
import PaperCard from '@/components/PaperCard';
import { DayPapers, Paper, Category } from '@/types';

// ✨ 直接在主页面定义我们的半导体地缘政治国家阵营
const CORE_COUNTRIES = ['全部', '中国', '美国', '日本', '欧洲', '中国台湾', '韩国', '澳大利亚', '国际/多边'];

export default function Home() {
  const [category, setCategory] = useState<any>('全部');
  const [days, setDays] = useState<DayPapers[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [categoryPapers, setCategoryPapers] = useState<Paper[]>([]);
  const [showCategoryView, setShowCategoryView] = useState(false);

  const today = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    setLoading(true);
    const lastDate = days.length > 0 ? days[days.length - 1].date : undefined;
    
    try {
      const params = new URLSearchParams();
      if (lastDate) {
        params.set('before', lastDate);
        params.set('limit', '30');
      }
      const res = await fetch(`/api/papers?${params}`);
      const data = await res.json();
      if (data.days && data.days.length > 0) {
        setDays(prev => [...prev, ...data.days]);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Failed to load papers:', error);
    } finally {
      setLoading(false);
    }
  }, [days, loading, hasMore]);

  useEffect(() => {
    const init = async () => {
      const res = await fetch('/api/papers');
      const data = await res.json();
      if (data.days) setDays(data.days);
    };
    init();
  }, []);

  useEffect(() => {
    if (category === '全部') {
      setShowCategoryView(false);
      setCategoryPapers([]);
    } else {
      const papers: Paper[] = [];
      days.forEach(day => {
        day.papers.forEach(paper => {
          if (paper.researchField && paper.researchField.includes(category)) {
            papers.push(paper);
          }
        });
      });
      papers.sort((a, b) => (b.scores?.overall || 0) - (a.scores?.overall || 0));
      setCategoryPapers(papers);
      setShowCategoryView(true);
    }
  }, [category, days]);

  useEffect(() => {
    if (showCategoryView) return;
    const handleScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        loadMore();
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loadMore, showCategoryView]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50/50">
      {/* 🚀 顶替掉原本的 Header 组件，直接手写全新半导体导航栏 */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-[#1e3a5f] tracking-tight">
              💻 全球半导体地缘政治与经济学术情报站
            </h1>
            <span className="text-sm font-medium text-gray-500">
              今日更新: {today}
            </span>
          </div>
          
          <div className="mb-1">
            <div className="text-xs text-gray-400 mb-2 font-semibold uppercase tracking-wider">🎯 核心博弈阵营筛选</div>
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {CORE_COUNTRIES.map((item) => (
                <button
                  key={item}
                  onClick={() => setCategory(item)}
                  className={`px-3.5 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                    category === item
                      ? 'bg-[#1e3a5f] text-white shadow-sm'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>
      
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6">
        {showCategoryView ? (
          <section>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-px flex-1 bg-gray-200"></div>
              <h2 className="text-sm font-medium text-gray-500">
                📂 【{category}】涉及的重磅论文 {categoryPapers.length} 篇
              </h2>
              <div className="h-px flex-1 bg-gray-200"></div>
            </div>
            
            {categoryPapers.length === 0 ? (
              <div className="text-center py-12 text-gray-400 bg-white rounded-xl border border-gray-100 shadow-sm">
                📭 暂无涉及【{category}】的研究论文
              </div>
            ) : (
              categoryPapers.map((paper, idx) => (
                <PaperCard key={`${paper.id}-${idx}`} paper={paper} />
              ))
            )}
          </section>
        ) : (
          <>
            {days.map((dayPapers) => (
              <DaySection 
                key={dayPapers.date} 
                dayPapers={dayPapers} 
                selectedCategory={category}
              />
            ))}
            
            {loading && (
              <div className="text-center py-8 text-gray-500">情报加载中...</div>
            )}
            
            {!hasMore && days.length > 0 && (
              <div className="text-center py-8 text-gray-400 text-sm">已加载全部学术动态</div>
            )}
          </>
        )}
      </main>
      
      <Footer />
    </div>
  );
}
