export interface ProjectCategory {
  name: string;
  description: string;
  color: string[];
}

export interface Project {
  id: string;
  name: string;
  author: string;
  description: string;
  url: string;
  homepage?: string;
  stars: number;
  forks: number;
  language: string;
  license: string;
  tags: string[];
  category: string;
  lastCommit: string;
  highlights: string[];
  gradient: string[];
}

export interface ProjectsData {
  lastUpdated: string;
  categories: Record<string, ProjectCategory>;
  projects: Project[];
}

export type SortOption = "default" | "stars" | "name" | "updated";