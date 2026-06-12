/**
 * Loading state for /explore route.
 *
 * Shows a minimal skeleton while the page loads. The design follows
 * the field manual aesthetic: monochrome, hairline borders, no
 * decorative elements. The skeleton uses the same spacing and
 * typography as the actual content so the transition feels seamless.
 */
export default function ExploreLoading() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header skeleton */}
      <div className="mb-8 space-y-3">
        <div className="h-8 w-48 animate-pulse bg-bg-elev" />
        <div className="h-4 w-96 max-w-full animate-pulse bg-bg-elev" />
      </div>

      {/* Search and filter skeleton */}
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="h-10 flex-1 animate-pulse bg-bg-elev" />
        <div className="h-10 w-40 animate-pulse bg-bg-elev sm:w-48" />
        <div className="h-10 w-40 animate-pulse bg-bg-elev sm:w-48" />
      </div>

      {/* Table skeleton */}
      <div className="space-y-2">
        {/* Table header */}
        <div className="grid grid-cols-7 gap-4 border-b border-line pb-3">
          <div className="col-span-2 h-3 w-20 animate-pulse bg-bg-elev" />
          <div className="h-3 w-16 animate-pulse bg-bg-elev" />
          <div className="h-3 w-12 animate-pulse bg-bg-elev" />
          <div className="h-3 w-20 animate-pulse bg-bg-elev" />
          <div className="h-3 w-16 animate-pulse bg-bg-elev" />
          <div className="h-3 w-16 animate-pulse bg-bg-elev" />
        </div>

        {/* Table rows */}
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="grid grid-cols-7 gap-4 border-b border-line py-4">
            <div className="col-span-2 space-y-2">
              <div className="h-4 w-32 animate-pulse bg-bg-elev" />
              <div className="h-3 w-48 animate-pulse bg-bg-elev" />
              <div className="h-3 w-24 animate-pulse bg-bg-elev" />
            </div>
            <div className="h-4 w-16 animate-pulse bg-bg-elev" />
            <div className="h-4 w-12 animate-pulse bg-bg-elev" />
            <div className="h-4 w-20 animate-pulse bg-bg-elev" />
            <div className="h-4 w-16 animate-pulse bg-bg-elev" />
            <div className="h-4 w-16 animate-pulse bg-bg-elev" />
          </div>
        ))}
      </div>
    </div>
  );
}
