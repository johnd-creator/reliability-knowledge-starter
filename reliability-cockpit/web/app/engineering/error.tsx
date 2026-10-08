"use client";
export default function Error({reset}:{reset:()=>void}){return <section className="state-card" role="alert"><h2>Engineering Workspace unavailable.</h2><p>Factual browsing remains available. Unsaved demo changes may be lost.</p><button onClick={reset}>Retry view</button></section>;}
