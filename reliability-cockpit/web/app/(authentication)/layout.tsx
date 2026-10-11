/** Authentication presentation only. Server-side QA access gates remain in the page and API. */
export default function AuthenticationLayout({ children }: { children: React.ReactNode }) {
  return <main id="main-content" className="authentication-layout">{children}</main>;
}
