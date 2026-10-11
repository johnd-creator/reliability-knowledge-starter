"use client";
import { idText } from "../../../lib/id-copy";
export default function Error({reset}:{reset:()=>void}){return <section className="state-card" role="alert"><h2>{idText("Engineering Workspace unavailable.")}</h2><p>{idText("Factual browsing remains available. Unsaved demo changes may be lost.")}</p><button onClick={reset}>{idText("Retry view")}</button></section>;}
