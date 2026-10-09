import type { Metadata } from "next";
import "./globals.css";
import "./engineering.css";
import DevelopmentStatus from "../components/DevelopmentStatus";
import { AppShell } from "../components/ui";

export const metadata: Metadata = {
  title: "NADI — Navigasi Analitik Data dan Informasi",
  description: "Platform Analitik Keandalan Aset Pembangkit",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>
        <AppShell engineeringVisible={process.env.NADI_ENGINEERING_WORKSPACE_ENABLED === "true"} liveDevelopment={process.env.NODE_ENV === "development" && process.env.NADI_LIVE_DEV === "true"}>
          {process.env.NODE_ENV === "development" && process.env.NADI_LIVE_DEV === "true" && <DevelopmentStatus/>}{children}</AppShell>
      </body>
    </html>
  );
}
