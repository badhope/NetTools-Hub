import type { Metadata, Viewport } from "next";
import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import { SetHtmlLang } from "@/components/set-html-lang";
import { SiteFooter } from "@/components/site-footer";
import { LANG_HTML_LANG, LANG_OG_LOCALE } from "@/lib/i18n";
import {
  PROJECT_COUNT,
  SITE_BASE_PATH,
  SITE_CANONICAL,
  SITE_OWNER,
} from "@/lib/site";
import "./globals.css";

// Content Security Policy.
//
// `script-src 'self'` alone is not viable for `output: "export"`:
// Next.js's static export emits inline `<script>` blocks for its
// hydration payload (the `self.__next_f.push([...])` calls) and
// those would be blocked, which would silently break *all* client
// state — the language switcher, the search bar, the sidebar, the
// project list filters — and the page would render the static HTML
// but never become interactive.
//
// We therefore allow `unsafe-inline` for scripts. The inline
// scripts that ship with the bundle are all generated at build
// time by Next.js, the contents are fully under our control, and
// the site has no user input, no auth, and no third-party embeds,
// so the XSS surface from re-enabling inline scripts is
// negligible. The remaining directives keep their restrictive
// defaults: no remote scripts, no remote styles except the
// Tailwind `unsafe-inline` (required for utility class generation),
// no `object-src`, and a same-origin default for everything else.
//
// `img-src` is tightened to `'self' data:` plus a same-origin
// `https://badhope.github.io` allowlist; the previous `'self' data:
// https:` accepted any HTTPS origin, which would have silently
// turned every future `<img src="…">` into a tracking-pixel
// honeypot the moment someone forgot to vet the URL.
//
// `referrer` and `Permissions-Policy` are added so a future
// Cloudflare/Netlify front-end (or a `<meta http-equiv>` here) can
// upgrade the site to full security-header coverage without
// revisiting this string.
//
// `frame-ancestors` is intentionally absent: when delivered via
// a `<meta>` element browsers ignore it (it must be a header),
// and keeping it here only produces noisy console warnings.
const CSP =
  "default-src 'self'; " +
  "script-src 'self' 'unsafe-inline'; " +
  "style-src 'self' 'unsafe-inline'; " +
  "img-src 'self' data: https://badhope.github.io; " +
  "font-src 'self' data:; " +
  "connect-src 'self'; " +
  "base-uri 'self'; " +
  "form-action 'self'; " +
  "object-src 'none'; " +
  "referrer 'strict-origin-when-cross-origin'; " +
  "permissions-policy camera=(), microphone=(), geolocation=(), interest-cohort=()";

// Display + body sans: IBM Plex Sans is a humanist grotesque
// designed at IBM Research. It is the only major sans shipped
// with a true monospace sibling (IBM Plex Mono) so the type
// pairing is guaranteed to match. We use IBM Plex Sans for
// both body and headings — the "field manual" design system
// does not mix faces; the personality comes from spacing and
// hairline rules, not from a contrasting display face.
const plex = IBM_Plex_Sans({
  subsets: ["latin", "latin-ext"],
  display: "swap",
  variable: "--font-plex-sans",
  weight: ["400", "500", "600", "700"],
});

// Mono for technical data: project stars, repo URLs, version
// numbers, category counts, "last updated" timestamps. Plex
// Mono is the only monospace that ships with the same metrics
// as Plex Sans, so the two faces align on the same baseline.
const plexMono = IBM_Plex_Mono({
  subsets: ["latin", "latin-ext"],
  display: "swap",
  variable: "--font-plex-mono",
  weight: ["400", "500", "600"],
});

export const viewport: Viewport = {
  // Match the cool dark palette (`--color-bg` in globals.css) so
  // the browser chrome (Safari status bar, Android system bar, PWA
  // splash) blends in. The "field manual" look is monochrome-cool;
  // a warm theme would clash with the hairlines and the steel-blue
  // accent.
  themeColor: "#0b0d10",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: {
    default: "NetTools Hub — A field manual of open-source network tools",
    template: "%s — NetTools Hub",
  },
  description: `A field manual of ${PROJECT_COUNT}+ open-source network tools, organised by kind (proxy, VPN, DNS, acceleration, security, monitoring, ops, tools) and by platform (desktop, mobile, CLI, server, browser, router).`,
  keywords: [
    "network tools",
    "open source",
    "proxy",
    "VPN",
    "Clash",
    "sing-box",
    "WireGuard",
    "GitHub acceleration",
    "DNS",
    "monitoring",
  ],
  authors: [{ name: SITE_OWNER }],
  creator: SITE_OWNER,
  metadataBase: new URL(`${SITE_CANONICAL}/`),
  // Per-language alternates. `<link rel="alternate" hreflang>` is
  // what tells Google which URL serves which language so it does
  // not have to guess from the URL's `?lang=` query. The English
  // variant is the canonical URL (no query) and the `x-default`
  // fallback for unrecognised locales.
  alternates: {
    canonical: `${SITE_CANONICAL}/`,
    languages: {
      en: `${SITE_CANONICAL}/`,
      "zh-Hans": `${SITE_CANONICAL}/?lang=zh`,
      ja: `${SITE_CANONICAL}/?lang=ja`,
      "x-default": `${SITE_CANONICAL}/`,
    },
  },
  // The PWA manifest is a sibling of the favicon in /public. We
  // link it from here so Next.js emits the `<link rel="manifest">`
  // tag in the document head.
  manifest: `${SITE_BASE_PATH}/manifest.webmanifest`,
  openGraph: {
    title: "NetTools Hub — A field manual of open-source network tools",
    description: `A field manual of ${PROJECT_COUNT}+ open-source network tools, organised by kind and by platform.`,
    url: `${SITE_CANONICAL}/`,
    siteName: "NetTools Hub",
    // Static export means `<html lang>` and the OG card both have to be
    // resolved at build time — we have no per-request metadata. We
    // pick English as the primary locale and expose the other two as
    // `og:locale:alternate` (the BCP-47-valid underscore form, e.g.
    // `zh_CN` rather than `zh-CN`, that crawlers actually parse).
    // The per-language URLs themselves are still discoverable via
    // `alternates.languages` above, which is what Google indexes.
    locale: LANG_OG_LOCALE.en,
    alternateLocale: [LANG_OG_LOCALE.zh, LANG_OG_LOCALE.ja],
    type: "website",
    // Social-card preview. The PNG lives in /public; using a PNG
    // (not SVG) means Twitter, LinkedIn, WeChat and most other
    // link-preview bots can render it.
    images: [
      {
        url: `${SITE_CANONICAL}/og-image.png`,
        width: 1200,
        height: 630,
        alt: `NetTools Hub — A field manual of ${PROJECT_COUNT}+ open-source network tools`,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "NetTools Hub — A field manual of open-source network tools",
    description: `A field manual of ${PROJECT_COUNT}+ open-source network tools, organised by kind and by platform.`,
    images: [`${SITE_CANONICAL}/og-image.png`],
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: `${SITE_BASE_PATH}/favicon.ico`,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang={LANG_HTML_LANG.en}
      className={`${plex.variable} ${plexMono.variable}`}
    >
      <head>
        <meta httpEquiv="Content-Security-Policy" content={CSP} />
      </head>
      <body>
        {/* Skip-to-content link. Rendered outside the normal flow so
         *  it does not contribute to layout; visually hidden until
         *  focused, at which point it slides into the top-left of
         *  the viewport. The destination `id="main"` lives on the
         *  per-page `<main>` element. The label is statically
         *  English (it is a global UI primitive, not a piece of
         *  content) but visually a keyboard user will only ever
         *  see it for a fraction of a second during the Tab key. */}
        <a href="#main" className="skip-link">
          Skip to main content
        </a>
        <SetHtmlLang />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
