export interface NavLink { href: string; label: string; section?: string; }
export interface NavItem { id: string; label: string; icon: string; href?: string; children?: NavLink[]; planned?: boolean; }

export const navigation: NavItem[] = [
  { id: "overview", href: "/", label: "Executive Overview", icon: "overview" },
  { id: "assets", label: "Asset Health", icon: "assets", children: [
    { href: "/assets", label: "Asset Register" },
    { href: "/asset-health", label: "Assessment Records" },
  ] },
  { id: "pdm", href: "/pdm", label: "PdM Center", icon: "chart" },
  { id: "recommendations", label: "Recommendations", icon: "idea", planned: true },
  { id: "actions", label: "Action Board", icon: "board", planned: true },
  { id: "reports", label: "Reports", icon: "report", planned: true },
  { id: "integration", label: "System Integration", icon: "integration", children: [
    { href: "/data-quality", label: "Data Trust Center" },
    { href: "/maintenance", label: "Maintenance", section: "Maximo" },
    { href: "/maintenance/investigation", label: "Maintenance Investigation", section: "Maximo" },
    { href: "/work-orders", label: "Work Orders", section: "Maximo" },
    { href: "/fmea", label: "FMEA", section: "Maximo" },
    { href: "/rcfa", label: "RCFA", section: "Maximo" },
    { href: "/overhauls", label: "Overhaul", section: "Maximo" },
  ] },
  { id: "administration", label: "Administration", icon: "settings", planned: true },
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
