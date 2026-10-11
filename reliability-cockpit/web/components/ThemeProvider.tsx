"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type Theme = "light" | "dark";
const ThemeContext = createContext<{ theme: Theme; toggleTheme: () => void }>({ theme: "light", toggleTheme: () => {} });

/** Presentation preference shared across authentication and workspace layouts. */
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  useEffect(() => {
    let saved: Theme = "light";
    try { saved = localStorage.getItem("nadi-theme") === "dark" ? "dark" : "light"; } catch { /* Storage is optional. */ }
    setTheme(saved);
    document.documentElement.dataset.theme = saved;
  }, []);
  function toggleTheme() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("nadi-theme", next); } catch { /* Preference still works for this visit. */ }
  }
  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return <button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={`Ganti ke tema ${theme === "light" ? "gelap" : "terang"}`} aria-pressed={theme === "dark"}>{theme === "light" ? "☾ Gelap" : "☀ Terang"}</button>;
}
