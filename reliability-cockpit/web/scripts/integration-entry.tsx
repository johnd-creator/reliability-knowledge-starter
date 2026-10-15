// Test-only actual components. All network is intercepted; no listening server.
import React from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "../components/AppNavigation";
import { ThemeProvider } from "../components/ThemeProvider";
import SystemIntegrationCenter from "../components/SystemIntegrationCenter";
createRoot(document.getElementById("root")!).render(<ThemeProvider><AppShell engineeringVisible><aside className="scope-banner"><strong>DEMO — QA SINTETIS · UJI KOMPONEN</strong><span>Tidak ada koneksi ke runtime atau data pembangkit.</span></aside><SystemIntegrationCenter /></AppShell></ThemeProvider>);
