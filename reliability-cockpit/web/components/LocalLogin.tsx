"use client";
import { idText } from "../lib/id-copy";
import {FormEvent,useEffect,useId,useRef,useState} from "react";
import {useRouter} from "next/navigation";
import {engineeringRequest,EngineeringHttpError} from "../lib/engineering-http";
import {Button,SectionCard} from "./ui";

type Session = {subject:string;roles:string[];asset_ids:string[];csrf_token:string};
export default function LocalLogin({onAuthenticated,expired=false}:{onAuthenticated?:(who:Session)=>void;expired?:boolean}) {
 const router=useRouter();
 const id=useId(),errorRef=useRef<HTMLParagraphElement>(null);
 const usernameId=id+"-username",passwordId=id+"-password",newPasswordId=id+"-new-password",helpId=id+"-help",errorId=id+"-error";
 const [username,setUsername]=useState(""),[password,setPassword]=useState(""),[newPassword,setNewPassword]=useState("");
 const [show,setShow]=useState(false),[change,setChange]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState("");
 useEffect(()=>{if(error)errorRef.current?.focus();},[error]);
 async function submit(event:FormEvent<HTMLFormElement>){
  event.preventDefault();if(busy)return;setBusy(true);setError("");
  try {
   await engineeringRequest("auth/login","POST",{username,password,...(change?{new_password:newPassword}:{})});
   // Only backend directory supplies identity. GET resumes session-bound CSRF after reload/navigation.
   const who=await engineeringRequest("session") as Session;
   setPassword("");setNewPassword("");
   if(onAuthenticated)onAuthenticated(who);else router.push("/engineering/local");
  }catch(caught){
   setPassword("");setNewPassword("");
   if(caught instanceof EngineeringHttpError&&caught.code==="PASSWORD_CHANGE_REQUIRED"){
    setChange(true);setError(idText("Password change required. Enter your temporary password and a new password."));
   }else if(caught instanceof EngineeringHttpError&&caught.status===429){setError(idText("Sign-in temporarily limited. Try later; no automatic retry."));}
   else if(caught instanceof EngineeringHttpError&&caught.code==="PASSWORD_POLICY_DENIED"){setError(idText("New password must meet the configured password policy and differ from the current password."));}
   else if(caught instanceof EngineeringHttpError&&[401,403,422].includes(caught.status)){setError(idText("Unable to sign in. Check your credentials."));}
   else setError(idText("Sign-in is unavailable. Try later."));
  }finally{setBusy(false);}
 }
 return <SectionCard className="login-card"><div className="nadi-local-login">
  <p className="eyebrow">{idText("WELCOME TO NADI")}</p><h2>{idText("Sign in to NADI")}</h2>
  <p className="login-introduction">{idText("Use your assigned account to access isolated Engineering QA.")}</p>
  {expired&&<p className="feedback login-expired" role="status">{idText("Your session expired or was revoked. Sign in again.")}</p>}
  <form onSubmit={submit} aria-label={idText("NADI sign-in")} aria-busy={busy} aria-describedby={error?`${helpId} ${errorId}`:helpId}>
    <p id={helpId} className="login-form-help">{idText("Username and password are required.")}</p>
    <div className="login-field"><label htmlFor={usernameId}>{idText("Username")}</label>
      <input className="input-control" id={usernameId} name="username" autoComplete="username" maxLength={64} required value={username} onChange={e=>setUsername(e.target.value)} disabled={busy}/></div>
    <div className="login-field"><label htmlFor={passwordId}>{idText("Password")}</label>
      <div className="nadi-password-field"><input className="input-control" id={passwordId} name="password" type={show?"text":"password"} autoComplete="current-password" maxLength={256} required value={password} onChange={e=>setPassword(e.target.value)} disabled={busy}/>
        <Button aria-controls={passwordId} aria-pressed={show} disabled={busy} onClick={()=>setShow(!show)}>{show?idText("Hide password"):idText("Show password")}</Button></div></div>
    {change&&<div className="login-field"><label htmlFor={newPasswordId}>{idText("New password")}</label>
      <input className="input-control" id={newPasswordId} type="password" autoComplete="new-password" maxLength={256} required value={newPassword} onChange={e=>setNewPassword(e.target.value)} disabled={busy}/></div>}
    {error&&<p className="feedback error login-feedback" id={errorId} role="alert" tabIndex={-1} ref={errorRef}>{error}</p>}
    <Button className="login-submit" type="submit" variant="primary" disabled={busy||!username||!password||(change&&!newPassword)}>{busy?<><span className="spinner" aria-hidden="true"/>{idText("Signing in…")}</>:change?idText("Change password and sign in"):idText("Sign in")}</Button>
    {busy&&<p className="sr-only" role="status">{idText("Signing in. Please wait.")}</p>}
  </form>
  <p className="login-account-help">{idText("No self-registration. Contact the approved operator for account or access changes.")}</p>
 </div></SectionCard>;
}
