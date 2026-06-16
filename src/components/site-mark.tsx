/**
 * Site mark.
 *
 * The only mark still used in the post-de-AI design: the brand
 * glyph in the top nav. The 21 category marks and 6 group marks
 * that used to live in this file were tied to the old
 * "editorial atlas" landing / explore pages, which the new
 * URL-tree + table layout replaces. They have been deleted to
 * stop them being imported by mistake.
 *
 * The mark itself is a "compass + meridian" that doubles as a
 * network node. The horizontal cross-line is the equator, the
 * vertical stroke is the prime meridian, the diagonal needle
 * hints at a navigation / field-guide instrument, and the
 * centred dot is the indexer.
 */

import * as React from 'react';

interface SiteMarkProps {
  size?: number;
  className?: string;
  strokeWidth?: number;
}

export function SiteMark({ size = 22, className, strokeWidth = 1.5 }: SiteMarkProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="square"
      strokeLinejoin="miter"
      className={className}
      role="presentation"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18" />
      <path d="M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" />
      <path d="M8 8l8 8M16 8l-8 8" />
      <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none" />
    </svg>
  );
}
