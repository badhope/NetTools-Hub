'use client';

import { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import type { Project } from '@/types/project';
import { ProjectTable } from './project-table';
import { t, Lang } from '@/lib/i18n';

interface SearchFilterProps {
  projects: readonly Project[];
  lang: Lang;
}

/**
 * Client-side enhancement layer for the /explore table.
 *
 * The actual project rows are server-rendered (passed in as
 * `projects` and rendered by `ProjectTable` immediately), so
 * users can see and click rows *before* JS hydrates. This
 * wrapper only adds the search/filter/sort controls on top, and
 * re-renders the table from the already-rendered list when the
 * user types.
 *
 * URL state is synced via the standard `history.replaceState`
 * API rather than `useSearchParams` from next/navigation. This
 * matters because the whole site is statically exported —
 * `useSearchParams` would force the entire client tree below
 * the surrounding layout into CSR-only mode, which means users
 * would see a loading skeleton until JS hydrates. The standard
 * browser API gives us URL persistence without that cost.
 */
export function SearchFilter({ projects, lang }: SearchFilterProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [sortBy, setSortBy] = useState<'stars' | 'name' | 'lastCommit'>('stars');

  // Read initial state from URL (runs once after mount)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    setSearchTerm(params.get('q') || '');
    setLanguageFilter(params.get('language') || '');
    const sort = params.get('sort');
    if (sort === 'stars' || sort === 'name' || sort === 'lastCommit') {
      setSortBy(sort);
    }
  }, []);

  // 防抖：延迟更新实际用于过滤的搜索词
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

  // 同步到 URL（不触发 Next.js 路由刷新）
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams();
    if (debouncedSearchTerm) params.set('q', debouncedSearchTerm);
    if (languageFilter) params.set('language', languageFilter);
    if (sortBy !== 'stars') params.set('sort', sortBy);

    const newUrl = params.toString()
      ? `${window.location.pathname}?${params.toString()}`
      : window.location.pathname;
    window.history.replaceState(null, '', newUrl);
  }, [debouncedSearchTerm, languageFilter, sortBy]);

  // 提取所有唯一的编程语言
  const availableLanguages = useMemo(() => {
    const langs = new Set<string>();
    projects.forEach((p) => {
      if (p.language) langs.add(p.language);
    });
    return Array.from(langs).sort();
  }, [projects]);

  // 过滤和排序项目
  const filteredProjects = useMemo(() => {
    let result = [...projects];

    if (debouncedSearchTerm.trim()) {
      const term = debouncedSearchTerm.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(term) ||
          p.description.toLowerCase().includes(term) ||
          p.tags.some((tag) => tag.toLowerCase().includes(term)),
      );
    }

    if (languageFilter) {
      result = result.filter((p) => p.language === languageFilter);
    }

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
  const clearAllFilters = useCallback(() => {
    setSearchTerm('');
    setLanguageFilter('');
    setSortBy('stars');
  }, []);

  const hasActiveFilters = searchTerm.trim() || languageFilter || sortBy !== 'stars';

  return (
    <div className="space-y-4" role="search" aria-label={t(lang, 'search.placeholder')}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
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
