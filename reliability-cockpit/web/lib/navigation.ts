import { idText } from "./id-copy";
export interface NavLink { href: string; label: string; section?: string; }
export interface NavItem { id: string; label: string; icon: string; href?: string; children?: NavLink[]; planned?: boolean; }

export const navigation: NavItem[] = [
  { id: "overview", href: "/", label: idText("Executive Overview"), icon: "overview" },
  { id: "assets", label: idText("Asset Health"), icon: "assets", children: [
    { href: "/assets", label: idText("Asset Register") },
    { href: "/asset-health", label: idText("Assessment Records") },
  ] },
  { id: "pdm", href: "/pdm", label: idText("PdM Center"), icon: "chart" },
  { id: "recommendations", href: "/recommendations", label: idText("Recommendations"), icon: "idea" },
  { id: "actions", href: "/action-board", label: idText("Action Board"), icon: "board" },
  { id: "reports", label: idText("Reports"), icon: "report", planned: true },
  { id: "integration", label: idText("System Integration"), icon: "integration", children: [
    { href: "/data-quality", label: idText("Data Trust Center") },
    { href: "/maintenance", label: idText("Maintenance"), section: "Maximo" },
    { href: "/maintenance/investigation", label: idText("Maintenance Investigation"), section: "Maximo" },
    { href: "/work-orders", label: idText("Work Orders"), section: "Maximo" },
    { href: "/fmea", label: "FMEA", section: "Maximo" },
    { href: "/rcfa", label: "RCFA", section: "Maximo" },
    { href: "/overhauls", label: "Overhaul", section: "Maximo" },
  ] },
  { id: "administration", label: idText("Administration"), icon: "settings", planned: true },
  { id: "guide", href: "/panduan/istilah", label: "Panduan & Istilah", icon: "report" },
];

export function routeMatches(path: string, href: string): boolean {
  return path === href || (href !== "/" && path.startsWith(`${href}/`));
}
export function activeLink(path: string, links: NavLink[]): string | undefined {
  return links.filter(link => routeMatches(path, link.href)).sort((a, b) => b.href.length - a.href.length)[0]?.href;
}
export function navigationGroup(path: string): string | undefined {
  if (routeMatches(path, "/equipment")) return "integration";
  return navigation.find(item => item.href ? routeMatches(path, item.href) : item.children?.some(link => routeMatches(path, link.href)))?.id;
}
