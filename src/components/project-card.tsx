import Link from "next/link";
import { Project } from "@/types/project";
import { formatNumber } from "@/lib/utils";
import type { Lang } from "@/lib/i18n";

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

// Atlas entry: left rail uses the project's own first gradient stop
// as a hairline, never as a fill. The body is calm body text, the
// title is the display serif, the metadata is mono. The hover state
// warms the rail and the title — no translate, no shadow.
export function ProjectCard({
  project,
  lang = "en",
}: {
  project: Project;
  lang?: Lang;
}) {
  const dotColor = languageColors[project.language] || "#8b949e";
  const railColor = project.gradient[0] || "#d97a3a";

  return (
    <Link
      href={project.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group relative flex h-full flex-col gap-3 border border-line bg-bg-elev/60 p-5 pl-6 transition-colors duration-300 hover:border-dim hover:bg-bg-elev focus-visible:border-accent"
      style={
        {
          // The rail is a 1px-wide coloured bar inset on the left
          // edge. Implemented as a CSS custom property so the
          // hover-state override can re-tint it without recomputing
          // the gradient.
          ["--rail" as string]: railColor,
        } as React.CSSProperties
      }
    >
      <span
        aria-hidden
        className="absolute inset-y-3 left-0 w-px transition-colors duration-300 group-hover:bg-[var(--rail)]"
        style={{ backgroundColor: "var(--rail)" }}
      />

      <div className="flex items-start justify-between gap-3">
        <h3 className="min-w-0 flex-1 font-display text-[1.15rem] font-medium leading-tight text-fg transition-colors duration-200 group-hover:text-accent line-clamp-1 break-words">
          {project.name}
        </h3>
        <span className="flex shrink-0 items-baseline gap-1 font-mono text-[11px] text-muted">
          <span className="text-fg-2">{formatNumber(project.stars, lang)}</span>
          <span aria-hidden>★</span>
        </span>
      </div>

      <p className="text-[13px] leading-relaxed text-fg-2 line-clamp-2 break-words">
        {project.description}
      </p>

      <div className="mt-1 flex flex-wrap gap-x-2 gap-y-1">
        {project.tags.slice(0, 3).map((tag) => (
          <span
            key={tag}
            className="font-mono text-[10px] uppercase tracking-wider text-muted"
          >
            #{tag}
          </span>
        ))}
      </div>

      <div className="mt-auto flex items-center justify-between gap-2 border-t border-line pt-3 font-mono text-[10.5px] text-muted">
        <span className="flex items-center gap-1.5">
          <span
            className="inline-block h-1.5 w-1.5 rounded-full"
            style={{ backgroundColor: dotColor }}
          />
          {project.language}
        </span>
        <span className="truncate">@{project.author}</span>
      </div>
    </Link>
  );
}
