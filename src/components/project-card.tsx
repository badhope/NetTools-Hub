import Link from "next/link";
import { Project } from "@/types/project";
import { formatNumber } from "@/lib/utils";

const languageColors: Record<string, string> = {
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  Go: "#00add8",
  Rust: "#dea584",
  Python: "#3572a5",
  C: "#555555",
  "C++": "#f34b7d",
  "C#": "#178600",
  Java: "#b07219",
  Ruby: "#701516",
  Swift: "#f05138",
  Kotlin: "#a97bff",
  Dart: "#00b4ab",
  PHP: "#4f5d95",
  Lua: "#000080",
  Shell: "#89e051",
  Markdown: "#083fa1",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Vue: "#41b883",
  Perl: "#0298c3",
};

export function ProjectCard({ project }: { project: Project }) {
  const dotColor = languageColors[project.language] || "#8b949e";

  return (
    <Link
      href={project.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex flex-col rounded-2xl border border-[#30363d] bg-[#161b22] p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-[#58a6ff]/40 hover:shadow-lg hover:shadow-black/30"
      style={{ borderLeftWidth: "3px", borderLeftColor: project.gradient[0] }}
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <h3 className="min-w-0 flex-1 text-[15px] font-semibold leading-snug text-[#e6edf3] group-hover:text-[#58a6ff] transition-colors line-clamp-1 break-all">
          {project.name}
        </h3>
        <div className="flex shrink-0 items-center gap-1 text-xs text-[#6e7681]">
          <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z" />
          </svg>
          {formatNumber(project.stars)}
        </div>
      </div>

      <p className="mb-5 text-[13px] leading-relaxed text-[#8b949e] line-clamp-2 break-words">
        {project.description}
      </p>

      <div className="mb-5 flex flex-wrap gap-1.5">
        {project.tags.slice(0, 2).map((tag) => (
          <span
            key={tag}
            className="rounded-md bg-[#21262d] px-2 py-0.5 text-[10px] font-medium text-[#8b949e] border border-[#30363d]"
          >
            {tag}
          </span>
        ))}
        {project.tags.length > 2 && (
          <span className="rounded-md bg-[#21262d] px-2 py-0.5 text-[10px] text-[#6e7681]">
            +{project.tags.length - 2}
          </span>
        )}
      </div>

      <div className="mt-auto flex items-center justify-between gap-2 border-t border-[#21262d] pt-4 text-[11px]">
        <div className="flex items-center gap-1.5 text-[#8b949e]">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: dotColor }}
          />
          <span className="truncate">{project.language}</span>
        </div>
        <span className="truncate text-[#6e7681]">@{project.author}</span>
      </div>
    </Link>
  );
}
