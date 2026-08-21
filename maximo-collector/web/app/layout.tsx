import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Maximo Collector — BSR Asset & Work Order Store",
  description: "Read-only Maximo OSLC collection dashboard & explorer for site BSR",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body>
        <nav className="navbar">
          <div style={{ display: "flex", alignItems: "center" }}>
            <Link href="/" className="brand">
              <span className="brand-mark">M</span>
              <span>
                <strong>Maximo Collector</strong>
                <small>BSR · org IP (OSLC)</small>
              </span>
            </Link>

            <div className="nav-links">
              <Link href="/" className="nav-link">
                Dashboard
              </Link>
              <Link href="/equipment" className="nav-link">
                Equipment
              </Link>
              <Link href="/work-orders" className="nav-link">
                Work Orders
              </Link>
              <Link href="/service-requests" className="nav-link">
                Service Requests
              </Link>
              <Link href="/data-explorer" className="nav-link">
                Data Explorer
              </Link>
            </div>
          </div>

          <div className="nav-actions">
            <span className="safe-badge">
              <i /> READ ONLY (GET)
            </span>
            <a href="/api/collector/docs" target="_blank" rel="noreferrer" title="FastAPI Swagger Documentation">
              API docs ↗
            </a>
          </div>
        </nav>
        <main className="shell">{children}</main>
      </body>
    </html>
  );
}
