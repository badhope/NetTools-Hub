/**
 * Loading state for /explore route.
 *
 * Shows a minimal skeleton while the page loads. The design follows
 * the field manual aesthetic: monochrome, hairline borders, no
 * decorative elements. The skeleton uses the same 3-column card
 * grid as the actual content so the transition feels seamless.
 */
export default function ExploreLoading() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="border border-line bg-bg-elev/40 p-4">
          {/* Header: name + badges */}
          <div className="mb-3 flex items-start justify-between gap-2">
            <div className="flex-1 space-y-2">
              <div className="h-4 w-32 animate-pulse bg-bg-elev" />
              <div className="h-3 w-20 animate-pulse bg-bg-elev" />
            </div>
            <div className="h-3 w-14 animate-pulse bg-bg-elev" />
          </div>

          {/* Description (2 lines) */}
          <div className="mb-3 space-y-1.5">
            <div className="h-3 w-full animate-pulse bg-bg-elev" />
            <div className="h-3 w-3/4 animate-pulse bg-bg-elev" />
          </div>

          {/* Metric grid (2x2) */}
          <div className="mb-3 grid grid-cols-2 gap-2">
            {Array.from({ length: 4 }).map((_, j) => (
              <div key={j} className="border border-line px-2 py-1">
                <div className="h-2 w-10 animate-pulse bg-bg-elev" />
                <div className="mt-1 h-3 w-12 animate-pulse bg-bg-elev" />
              </div>
            ))}
          </div>

          {/* Platform badges */}
          <div className="mb-3 flex gap-1.5">
            <div className="h-4 w-12 animate-pulse bg-bg-elev" />
            <div className="h-4 w-10 animate-pulse bg-bg-elev" />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between border-t border-line pt-2">
            <div className="h-2 w-16 animate-pulse bg-bg-elev" />
            <div className="h-2 w-12 animate-pulse bg-bg-elev" />
          </div>
        </div>
      ))}
    </div>
  );
}
