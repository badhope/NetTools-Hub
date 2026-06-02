"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getAllProjects, getCategoryCounts, getCategories } from "@/lib/projects";
import { t, Lang } from "@/lib/i18n";
import { TopNav } from "@/components/top-nav";

function readLangFromUrl(): Lang | null {
  if (typeof window === "undefined") return null;
  const urlLang = new URLSearchParams(window.location.search).get("lang");
  if (urlLang === "en" || urlLang === "zh" || urlLang === "ja") return urlLang;
  return null;
}

export function LandingContent() {
  const [lang, setLang] = useState<Lang>("en");

  useEffect(() => {
    const fromUrl = readLangFromUrl();
    if (fromUrl && fromUrl !== lang) setLang(fromUrl);
  }, []);

  const handleLangChange = (newLang: Lang) => {
    setLang(newLang);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      if (newLang === "en") url.searchParams.delete("lang");
      else url.searchParams.set("lang", newLang);
      window.history.replaceState({}, "", url.toString());
    }
  };

  const projects = getAllProjects();
  const counts = getCategoryCounts();
  const categories = getCategories();
  const totalProjects = projects.length;
  const totalStars = projects.reduce((sum, p) => sum + p.stars, 0);
  const langParam = (path: string) => (lang !== "en" ? `${path}?lang=${lang}` : path);

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#e6edf3]">
      <TopNav
        lang={lang}
        onLangChange={handleLangChange}
        categories={categories}
        counts={counts}
        variant="landing"
      />

      <section className="relative flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center overflow-hidden px-6 py-24">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[600px] w-[600px] rounded-full bg-[#58a6ff]/5 blur-3xl" />
          <div className="absolute top-20 -left-40 h-[400px] w-[400px] rounded-full bg-[#3fb950]/5 blur-3xl" />
          <div className="absolute -bottom-20 right-0 h-[400px] w-[400px] rounded-full bg-[#bc8cff]/5 blur-3xl" />
        </div>

        <div className="relative z-10 mx-auto max-w-4xl text-center">
          <h1 className="mb-8 text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
            <span className="block">{t(lang, "hero.title1")}</span>
            <span className="bg-gradient-to-r from-[#58a6ff] via-[#bc8cff] to-[#3fb950] bg-clip-text text-transparent">
              {t(lang, "hero.title2")}
            </span>
          </h1>

          <p className="mx-auto mb-12 max-w-2xl text-base leading-relaxed text-[#8b949e] sm:text-lg">
            {t(lang, "hero.description", { total: totalProjects })}
          </p>

          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href={langParam("/explore")}
              className="inline-flex items-center gap-2 rounded-xl bg-[#238636] px-8 py-3 text-base font-medium text-white transition-all hover:bg-[#2ea043] hover:shadow-lg hover:shadow-[#238636]/20"
            >
              {t(lang, "hero.explore_platform")}
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            <a
              href="#features"
              className="inline-flex items-center gap-2 rounded-xl border border-[#30363d] bg-[#161b22] px-8 py-3 text-base text-[#8b949e] transition-colors hover:border-[#58a6ff] hover:text-[#e6edf3]"
            >
              {t(lang, "hero.learn_more")}
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </a>
          </div>

          <div className="mt-10 inline-flex items-center gap-2 rounded-full border border-[#30363d] bg-[#161b22] px-4 py-1.5 text-sm text-[#8b949e]">
            <span className="inline-block h-2 w-2 rounded-full bg-[#3fb950] animate-pulse" />
            {t(lang, "hero.updated")}
          </div>
        </div>

        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
          <svg className="h-6 w-6 text-[#6e7681]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      <section id="features" className="border-t border-[#21262d] bg-[#0d1117] py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-2xl font-bold sm:text-3xl">{t(lang, "features.title")}</h2>
            <p className="text-[#8b949e]">{t(lang, "features.subtitle")}</p>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: "📦",
                title: t(lang, "features.curated", { total: totalProjects }),
                desc: t(lang, "features.curated_desc"),
              },
              {
                icon: "🔍",
                title: t(lang, "features.search"),
                desc: t(lang, "features.search_desc"),
              },
              {
                icon: "📊",
                title: t(lang, "features.sort"),
                desc: t(lang, "features.sort_desc"),
              },
              {
                icon: "📱",
                title: t(lang, "features.responsive"),
                desc: t(lang, "features.responsive_desc"),
              },
              {
                icon: "🔄",
                title: t(lang, "features.maintained"),
                desc: t(lang, "features.maintained_desc"),
              },
              {
                icon: "⭐",
                title: t(lang, "features.stars", { stars: (totalStars / 1000000).toFixed(1) }),
                desc: t(lang, "features.stars_desc"),
              },
            ].map((f) => (
              <div
                key={f.title}
                className="rounded-2xl border border-[#30363d] bg-[#161b22] p-7 transition-colors hover:border-[#58a6ff]/30"
              >
                <span className="mb-4 inline-block text-3xl">{f.icon}</span>
                <h3 className="mb-3 text-base font-semibold">{f.title}</h3>
                <p className="text-sm leading-relaxed text-[#8b949e]">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-[#21262d] bg-[#0d1117] py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-2xl font-bold sm:text-3xl">{t(lang, "categories.title")}</h2>
            <p className="text-[#8b949e]">{t(lang, "categories.subtitle")}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {Object.entries(counts).map(([slug, count]) => {
              const catInfo = categories[slug];
              return (
                <Link
                  key={slug}
                  href={lang !== "en" ? `/explore?category=${slug}&lang=${lang}` : `/explore?category=${slug}`}
                  className="flex flex-col items-center gap-2 rounded-2xl border border-[#30363d] bg-[#161b22] px-4 py-6 text-center transition-colors hover:border-[#58a6ff]/30 hover:bg-[#1c2333]"
                >
                  <span className="truncate text-sm font-medium text-[#e6edf3]">{catInfo?.icon} {catInfo?.name || slug}</span>
                  <span className="text-xs text-[#6e7681]">{t(lang, "categories.count", { count })}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      <section className="border-t border-[#21262d] bg-[#0d1117] py-24">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="mb-5 text-2xl font-bold sm:text-3xl">{t(lang, "cta.title")}</h2>
          <p className="mb-10 text-[#8b949e]">{t(lang, "cta.description")}</p>
          <Link
            href={langParam("/explore")}
            className="inline-flex items-center gap-2 rounded-xl bg-[#238636] px-10 py-3.5 text-base font-medium text-white transition-all hover:bg-[#2ea043] hover:shadow-lg hover:shadow-[#238636]/20"
          >
            {t(lang, "cta.button")}
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </section>

      <footer className="border-t border-[#21262d] bg-[#010409] py-10">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-[#6e7681]">
            <span>🛠️</span>
            <span>{t(lang, "footer.text")}</span>
          </div>
          <p className="mt-3 text-xs text-[#6e7681]">
            {t(lang, "footer.disclaimer")}
          </p>
        </div>
      </footer>
    </div>
  );
}
