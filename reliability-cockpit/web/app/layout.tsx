import type { Metadata } from "next";
import "./globals.css";
import "./engineering.css";
import "./login-refresh.css";
import "./enterprise.css";
import "./experience.css";
import { ThemeProvider } from "../components/ThemeProvider";

export const metadata: Metadata = {
  title: "NADI — Navigasi Analitik Data dan Informasi",
  description: "Platform Analitik Keandalan Aset Pembangkit",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
