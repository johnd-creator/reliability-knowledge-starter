import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Reliability Cockpit",
  description: "Reliability data views from the verified knowledge contracts",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>
        <header>
          <h1>Reliability Cockpit</h1>
          <nav>
            <a href="/">Equipment</a>
            <a href="/work-orders">Work Orders</a>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
