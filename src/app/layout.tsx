import type { Metadata, Viewport } from "next";
import { Fraunces, Instrument_Sans, JetBrains_Mono } from "next/font/google";
import { SetHtmlLang } from "@/components/set-html-lang";
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
// `frame-ancestors` is intentionally absent: when delivered via
// a `<meta>` element browsers ignore it (it must be a header),
// and keeping it here only produces noisy console warnings.
const CSP =
  "default-src 'self'; " +
  "script-src 'self' 'unsafe-inline'; " +
  "style-src 'self' 'unsafe-inline'; " +
  "img-src 'self' data: https:; " +
  "font-src 'self' data:; " +
  "connect-src 'self'; " +
  "base-uri 'self'; " +
  "form-action 'self'; " +
  "object-src 'none'";

// Display serif: Fraunces is a variable serif with optical sizing,
// soft curves and a humanist warmth that doesn't appear in any of
// the typical "AI default" front-end stacks (Inter / Space Grotesk /
// Geist). It is the visual signature of the editorial-atlas
// direction: the hero / section headings all use it.
// "opsz" 9..144 makes the optical-size axis available, which lets
// the browser pick a tighter or looser cut depending on rendered
// size; that alone makes the type feel "drawn for" the page.
const fraunces = Fraunces({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-fraunces",
  axes: ["opsz", "SOFT", "WONK"],
});

// Body / UI sans: Instrument Sans is a humanist geometric sans
// with a slight terminal flavour, designed by Instrument (the
// same studio behind Linear / Vercel's design system) but
// deliberately not the Vercel-default Geist. Its character lies
// in the slightly condensed x-height and the open apertures,
// which give UI text a calm, considered feel.
const instrumentSans = Instrument_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-instrument",
  weight: ["400", "500", "600", "700"],
});

// Monospace for technical metadata: project stars, repo URLs,
// version numbers, category counts, "last updated" timestamps.
// JetBrains Mono is the only monospace that ships with the
// "calt" ligature set we want for `=>`, `!=`, and `>=` glyphs
// in this codebase.
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-jetbrains",
  weight: ["400", "500", "600"],
});

const SITE_URL = "https://badhope.github.io/NetTools-Hub";
const BASE_PATH = "/NetTools-Hub";

export const viewport: Viewport = {
  // Match the warm dark palette so the browser chrome (Safari
  // status bar, Android system bar, PWA splash) blends in.
  themeColor: "#0e0c0a",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: {
    default: "NetTools Hub — An Atlas of Network Tools",
    template: "%s — NetTools Hub",
  },
  description:
    "A curated atlas of 120+ open-source network tools, organised by purpose, with multilingual annotations and editorial notes.",
  keywords: [
    "network tools",
    "open source",
    "atlas",
    "proxy",
    "VPN",
    "Clash",
    "GitHub acceleration",
    "DNS",
    "monitoring",
  ],
  authors: [{ name: "badhope" }],
  creator: "badhope",
  metadataBase: new URL(SITE_URL),
  // Per-language alternates. `<link rel="alternate" hreflang>` is
  // what tells Google which URL serves which language so it does
  // not have to guess from the URL's `?lang=` query. The English
  // variant is the canonical URL (no query) and the `x-default`
  // fallback for unrecognised locales.
  alternates: {
    canonical: SITE_URL,
    languages: {
      en: SITE_URL,
      "zh-Hans": `${SITE_URL}/?lang=zh`,
      ja: `${SITE_URL}/?lang=ja`,
      "x-default": SITE_URL,
    },
  },
  // The PWA manifest is a sibling of the favicon in /public. We
  // link it from here so Next.js emits the `<link rel="manifest">`
  // tag in the document head.
  manifest: `${BASE_PATH}/manifest.webmanifest`,
  openGraph: {
    title: "NetTools Hub — An Atlas of Network Tools",
    description:
      "A curated atlas of 120+ open-source network tools, organised by purpose, with multilingual annotations and editorial notes.",
    url: SITE_URL,
    siteName: "NetTools Hub",
    locale: "en_US",
    type: "website",
    // Social-card preview. The PNG lives in /public; using a PNG
    // (not SVG) means Twitter, LinkedIn, WeChat and most other
    // link-preview bots can render it.
    images: [
      {
        url: `${SITE_URL}/og-image.png`,
        width: 1200,
        height: 630,
        alt: "NetTools Hub — A curated atlas of 120+ open-source network tools",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "NetTools Hub — An Atlas of Network Tools",
    description:
      "A curated atlas of 120+ open-source network tools, organised by purpose, with multilingual annotations and editorial notes.",
    images: [`${SITE_URL}/og-image.png`],
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: `${BASE_PATH}/favicon.ico`,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${instrumentSans.variable} ${jetbrainsMono.variable}`}
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
      </body>
    </html>
  );
}
