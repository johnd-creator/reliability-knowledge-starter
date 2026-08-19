import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "CEMS Collector — BSR Emission Monitoring Store",
  description: "Read-only CEMS Modbus collection dashboard for stack BSR (PLTU Suralaya)",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body>
        <nav className="navbar">
          <div style={{ display: "flex", alignItems: "center" }}>
            <Link href="/" className="brand">
              <span className="brand-mark">C</span>
              <span>
                <strong>CEMS Collector</strong>
                <small>BSR · stack 1 (Modbus TCP, read-only)</small>
              </span>
            </Link>

            <div className="nav-links">
              <Link href="/" className="nav-link">
                Dashboard
              </Link>
              <Link href="/trending" className="nav-link">
                Tren 5-Menit
              </Link>
              <Link href="/parameters" className="nav-link">
                Parameter
              </Link>
            </div>
          </div>

          <div className="nav-actions">
            <span className="safe-badge">
              <i /> READ ONLY (FC03/FC04)
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
