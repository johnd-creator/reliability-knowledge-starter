// Actual candidate components; every browser request is intercepted. No server.
import React from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "../components/AppNavigation";
import { ThemeProvider } from "../components/ThemeProvider";
import ReportsCenter from "../components/ReportsCenter";
createRoot(document.getElementById("root")!).render(<ThemeProvider><AppShell engineeringVisible><aside className="scope-banner"><strong>DEMO / QA SYNTHETIC — UJI KOMPONEN</strong><span>Bukan data pembangkit atau preview runtime yang diterapkan.</span></aside><ReportsCenter /></AppShell></ThemeProvider>);
