import { ProjectsData, ProjectCategory } from "@/types/project";
// data/projects.json lives at the repository root (kept outside src/ so
// that future tooling — e.g. a separate data-validation script — can
// read it without going through the Next.js import graph). Resolve
// with a relative path; the @/ alias only covers src/.
import rawData from "../../data/projects.json";
import { formatNumber } from "@/lib/utils";

export { formatNumber };

const data = rawData as ProjectsData;

export function getAllProjects() {
  return data.projects;
}

export function getCategories(): Record<string, ProjectCategory> {
  return data.categories;
}

export function getCategoryCounts(): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const p of data.projects) {
    counts[p.category] = (counts[p.category] || 0) + 1;
  }
  return counts;
}

export function getProjectsByCategory(category: string) {
  if (!category || category === "all") return data.projects;
  return data.projects.filter((p) => p.category === category);
}

export function searchProjects(query: string, category?: string) {
  const base = category ? getProjectsByCategory(category) : data.projects;
  if (!query.trim()) return base;
  const q = query.toLowerCase();
  return base.filter(
    (p) =>
      p.name.toLowerCase().includes(q) ||
      p.author.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.tags.some((t) => t.toLowerCase().includes(q)) ||
      p.highlights.some((h) => h.toLowerCase().includes(q))
  );
}
