"use client";
import {createContext,useContext} from 'react';
import type {LocalSession} from '../lib/local-session';
export const WorkspaceAccountContext=createContext<{identity:LocalSession;requestLogout:()=>void}|null>(null);
/** Existing topbar slot only. Session authority remains in AuthenticatedWorkspace/server. */
export default function WorkspaceAccount(){
 const account=useContext(WorkspaceAccountContext);
 if(!account)return null;
 const {identity,requestLogout}=account;
 return <div className="workspace-account" aria-label={`Akun terautentikasi: ${identity.username??identity.subject}`}><span className="workspace-username" title={`ID audit: ${identity.subject} · Peran: ${identity.roles.join(', ')}`}>{identity.username??identity.subject}</span><button className="theme-toggle logout-trigger" type="button" onClick={requestLogout} aria-label="Keluar dari NADI"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><path d="M10 4H4v16h6M14 8l4 4-4 4M8 12h11"/></svg><span>Keluar</span></button></div>;
}
