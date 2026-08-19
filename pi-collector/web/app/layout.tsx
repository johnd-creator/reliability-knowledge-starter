import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "PI Collector — BSR1 Telemetry & Historian",
  description: "PI Web API time-series telemetry collector & historian explorer for BSR1",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body>
        <nav className="app-navbar">
          <Link href="/" className="nav-brand">
            <div className="nav-logo-icon">⚡</div>
            <div>
              <div className="nav-title">PI Collector</div>
              <div className="nav-subtitle">BSR1 Plant Historian</div>
            </div>
          </Link>

          <div className="nav-links">
            <Link href="/" className="nav-link active">
              <span>Attributes</span>
            </Link>
            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="nav-link"
              title="FastAPI Swagger Documentation"
            >
              <span>API Docs ↗</span>
            </a>
          </div>
        </nav>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
