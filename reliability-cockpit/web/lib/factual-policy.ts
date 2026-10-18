import type {LocalSession} from './local-session';
/** AUTH-03 PO decision, 2026-10-18: explicit application READ capability.
 * Canonical subject verified against retained local directory, not a username match.
 * Applies only behind the exact laptop runtime/session gates in factualGateway.
 * No directory role, asset grant, SQL privilege, Engineering action or export changes. */
export const LOCAL_PORTFOLIO_READ={
 subject:'local:c759c2d1-19a4-4291-9b66-9218dbd12dea',
 capability:'BSR_IP_FACTUAL_PORTFOLIO_READ',site:'BSR',organization:'IP',
} as const;
export function hasPortfolioRead(session:LocalSession):boolean{
 return session.subject===LOCAL_PORTFOLIO_READ.subject&&session.roles.includes('ADMIN');
}
export const portfolioRoutes=new Set(['assets','registry','decision-overview','asset-health/overview','fmea/overview','rcfa/overview','maintenance-investigation','maintenance-events','fmea','rcfa','asset-health','overhauls/overview','overhauls','data-trust','integrity','integration-status']);
