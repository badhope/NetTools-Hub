import type { Metadata } from "next";
import "./globals.css";
import { SetHtmlLang } from "@/components/set-html-lang";

export const metadata: Metadata = {
  title: "NetTools Hub - Network Tools Navigation Platform",
  description:
    "One-stop navigation platform for 120+ curated network tools, including proxies, VPNs, Clash, GitHub acceleration, DNS tools, security tools, and more.",
  openGraph: {
    title: "NetTools Hub - Network Tools Navigation Platform",
    description:
      "One-stop navigation platform for 120+ curated network tools, including proxies, VPNs, Clash, GitHub acceleration, DNS tools, security tools, and more.",
    url: "https://badhope.github.io/NetTools-Hub",
    siteName: "NetTools Hub",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "NetTools Hub - Network Tools Navigation Platform",
    description:
      "One-stop navigation platform for 120+ curated network tools, including proxies, VPNs, Clash, GitHub acceleration, DNS tools, security tools, and more.",
  },
  alternates: {
    canonical: "https://badhope.github.io/NetTools-Hub",
  },
};

const CSP =
  "default-src 'self'; " +
  "script-src 'self'; " +
  "style-src 'self' 'unsafe-inline'; " +
  "img-src 'self' data: https:; " +
  "font-src 'self' data:; " +
  "connect-src 'self'; " +
  "base-uri 'self'; " +
  "form-action 'self'; " +
  "object-src 'none'; " +
  "frame-ancestors 'none'";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/*
         * H-1 (JS-CSP-001): Emit the Content-Security-Policy as a real
         * <meta http-equiv> so browsers actually enforce it. GitHub Pages
         * does not allow custom HTTP headers, so the meta tag is the only
         * delivery channel available.
         *
         * Policy (the minimum the site needs):
         *   default-src 'self';        only same-origin by default
         *   script-src 'self';         no inline scripts, no eval, no remote JS
         *   style-src 'self' 'unsafe-inline';  Tailwind v4 emits runtime
         *                                utility classes via inline <style>;
         *                                CSP2 allows style 'unsafe-inline' as
         *                                a standard mitigation
         *   img-src 'self' data: https:;  project thumbnails are external
         *                                GitHub avatars / OG images
         *   font-src 'self' data:;     local fonts only
         *   connect-src 'self';        no XHR / fetch to third-party APIs
         *   base-uri 'self';           block <base> hijacking
         *   form-action 'self';        block third-party form submissions
         *   object-src 'none';         block <object> / <embed> Flash / PDF
         *   frame-ancestors 'none';    clickjacking protection
         *
         * Note: `frame-ancestors` and `report-uri` are ignored when the CSP
         * is delivered via <meta> (per CSP2). The rest is enforced.
         */}
        <meta httpEquiv="Content-Security-Policy" content={CSP} />
      </head>
      <body className="antialiased">
        <SetHtmlLang />
        {children}
      </body>
    </html>
  );
}
