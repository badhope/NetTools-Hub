'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import type { Project } from '@/types/project';
import { ProjectTable } from './project-table';
import { t, Lang } from '@/lib/i18n';

interface SearchFilterProps {
  projects: readonly Project[];
  lang: Lang;
}

export function SearchFilter({ projects, lang }: SearchFilterProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // 从 URL 读取初始状态
  // 注意：使用 'language' 参数避免与 UI 语言的 'lang' 冲突
  const [searchTerm, setSearchTerm] = useState(searchParams.get('q') || '');
  const [languageFilter, setLanguageFilter] = useState(searchParams.get('language') || '');
  const [sortBy, setSortBy] = useState<'stars' | 'name' | 'lastCommit'>(
    (searchParams.get('sort') as 'stars' | 'name' | 'lastCommit') || 'stars',
  );

  // 防抖：延迟更新实际用于过滤的搜索词
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState(searchTerm);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchTerm]);

  // 更新 URL 参数（使用防抖后的搜索词）
  useEffect(() => {
    const params = new URLSearchParams();

    // 保留现有的 UI 语言参数
    const currentLang = searchParams.get('lang');
    if (currentLang) params.set('lang', currentLang);

    // 添加搜索和筛选参数
    if (debouncedSearchTerm) params.set('q', debouncedSearchTerm);
    if (languageFilter) params.set('language', languageFilter);
    if (sortBy !== 'stars') params.set('sort', sortBy);

    const newUrl = params.toString() ? `/explore?${params.toString()}` : '/explore';

    router.replace(newUrl, { scroll: false });
  }, [debouncedSearchTerm, languageFilter, sortBy, router, searchParams]);

  // 提取所有唯一的编程语言
  const availableLanguages = useMemo(() => {
    const langs = new Set<string>();
    projects.forEach((p) => {
      if (p.language) langs.add(p.language);
    });
    return Array.from(langs).sort();
  }, [projects]);

  // 过滤和排序项目（使用防抖后的搜索词）
  const filteredProjects = useMemo(() => {
    let result = [...projects];

    // 搜索过滤
    if (debouncedSearchTerm.trim()) {
      const term = debouncedSearchTerm.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(term) ||
          p.description.toLowerCase().includes(term) ||
          p.tags.some((tag) => tag.toLowerCase().includes(term)),
      );
    }

    // 语言过滤
    if (languageFilter) {
      result = result.filter((p) => p.language === languageFilter);
    }

    // 排序
    result.sort((a, b) => {
      switch (sortBy) {
        case 'stars':
          return b.stars - a.stars;
        case 'name':
          return a.name.localeCompare(b.name);
        case 'lastCommit':
          return b.lastCommit.localeCompare(a.lastCommit);
        default:
          return 0;
      }
    });

    return result;
  }, [projects, debouncedSearchTerm, languageFilter, sortBy]);

  // 清除所有筛选条件
  const clearAllFilters = () => {
    setSearchTerm('');
    setLanguageFilter('');
    setSortBy('stars');
  };

  // 检查是否有活跃的筛选条件
  const hasActiveFilters = searchTerm.trim() || languageFilter || sortBy !== 'stars';

  return (
    <div className="space-y-4" role="search" aria-label={t(lang, 'search.placeholder')}>
      {/* 搜索和筛选控件 */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        {/* 搜索框 */}
        <div className="flex-1 relative">
          <label htmlFor="search-input" className="sr-only">
            {t(lang, 'search.placeholder')}
          </label>
          <input
            id="search-input"
            type="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t(lang, 'search.placeholder')}
            aria-label={t(lang, 'search.placeholder')}
            aria-describedby="search-description"
            className="w-full rounded-none border border-line bg-bg-elev px-3 py-2 pr-10 font-mono text-sm text-fg placeholder:text-muted focus:border-accent focus:outline-none"
          />
          {searchTerm && (
            <button
              type="button"
              onClick={() => setSearchTerm('')}
              aria-label={t(lang, 'search.clear')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted hover:text-fg transition-colors"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>

        {/* 语言筛选 */}
        <div className="sm:w-48">
          <label htmlFor="language-filter" className="sr-only">
            {t(lang, 'filter.all_languages')}
          </label>
          <select
            id="language-filter"
            value={languageFilter}
            onChange={(e) => setLanguageFilter(e.target.value)}
            aria-label={t(lang, 'filter.all_languages')}
            className="w-full rounded-none border border-line bg-bg-elev px-3 py-2 font-mono text-sm text-fg focus:border-accent focus:outline-none"
          >
            <option value="">{t(lang, 'filter.all_languages')}</option>
            {availableLanguages.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </div>

        {/* 排序选择 */}
        <div className="sm:w-48">
          <label htmlFor="sort-select" className="sr-only">
            {t(lang, 'sort.stars')}
          </label>
          <select
            id="sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'stars' | 'name' | 'lastCommit')}
            aria-label={t(lang, 'sort.stars')}
            className="w-full rounded-none border border-line bg-bg-elev px-3 py-2 font-mono text-sm text-fg focus:border-accent focus:outline-none"
          >
            <option value="stars">{t(lang, 'sort.stars')}</option>
            <option value="name">{t(lang, 'sort.name')}</option>
            <option value="lastCommit">{t(lang, 'sort.last_commit')}</option>
          </select>
        </div>
      </div>

      {/* 结果计数和清除按钮 */}
      <div className="flex items-center justify-between gap-4">
        <div
          id="search-description"
          className="font-mono text-xs text-muted"
          aria-live="polite"
          aria-atomic="true"
        >
          {t(lang, 'search.results_count', { count: filteredProjects.length })}
        </div>
        {hasActiveFilters && (
          <button
            type="button"
            onClick={clearAllFilters}
            aria-label={t(lang, 'search.clear_all')}
            className="font-mono text-xs text-muted hover:text-accent transition-colors"
          >
            {t(lang, 'search.clear_all')}
          </button>
        )}
      </div>

      {/* 项目表格或空状态 */}
      {filteredProjects.length > 0 ? (
        <ProjectTable projects={filteredProjects} lang={lang} />
      ) : (
        <div className="border border-line p-8 text-center">
          <p className="text-lg text-fg-2 mb-2">{t(lang, 'empty.title')}</p>
          <p className="text-sm text-muted mb-4">{t(lang, 'empty.description')}</p>
          <button
            type="button"
            onClick={clearAllFilters}
            className="inline-flex items-center gap-2 px-4 py-2 border border-accent text-accent hover:bg-accent hover:text-bg transition-colors"
          >
            {t(lang, 'empty.back')}
          </button>
        </div>
      )}
    </div>
  );
}
