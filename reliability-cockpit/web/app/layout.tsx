import type { Metadata } from "next";
import "./globals.css";
import "./engineering.css";
import { AppShell } from "../components/ui";

export const metadata: Metadata = {
  title: "NADI — Navigasi Analitik Data dan Informasi",
  description: "Platform Analitik Keandalan Aset Pembangkit",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>
        <AppShell engineeringVisible={process.env.NADI_ENGINEERING_WORKSPACE_ENABLED === "true"}>{children}</AppShell>
      </body>
    </html>
  );
}
