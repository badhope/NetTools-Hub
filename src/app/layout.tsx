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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <SetHtmlLang />
        {children}
      </body>
    </html>
  );
}
