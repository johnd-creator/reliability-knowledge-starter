"use client";
import {FormEvent,useState} from "react";
import {useRouter} from "next/navigation";
import {engineeringRequest,EngineeringHttpError} from "../lib/engineering-http";
import {SectionCard} from "./ui";

type Session = {subject:string;roles:string[];asset_ids:string[];csrf_token:string};
export default function LocalLogin({onAuthenticated,expired=false}:{onAuthenticated?:(who:Session)=>void;expired?:boolean}) {
 const router=useRouter();
 const [username,setUsername]=useState(""),[password,setPassword]=useState(""),[newPassword,setNewPassword]=useState("");
 const [show,setShow]=useState(false),[change,setChange]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState("");
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
    setChange(true);setError("Password change required. Enter your temporary password and a new password.");
   }else if(caught instanceof EngineeringHttpError&&caught.status===429){setError("Sign-in temporarily limited. Try later; no automatic retry.");}
   else if(caught instanceof EngineeringHttpError&&caught.code==="PASSWORD_POLICY_DENIED"){setError("New password must meet the configured password policy and differ from the current password.");}
   else if(caught instanceof EngineeringHttpError&&[401,403,422].includes(caught.status)){setError("Unable to sign in. Check your credentials.");}
   else setError("Sign-in is unavailable. Try later.");
  }finally{setBusy(false);}
 }
 return <SectionCard><div className="nadi-local-login"><h2>Sign in to NADI</h2>
 <p>Local authentication · development / disposable QA. Access is assigned by an authorized administrator.</p>
 {expired&&<p role="status">Your session expired or was revoked. Sign in again.</p>}
 <form onSubmit={submit} aria-busy={busy}>
 <label htmlFor="nadi-login-username">Username</label><input id="nadi-login-username" name="username" autoComplete="username" maxLength={64} required value={username} onChange={e=>setUsername(e.target.value)} disabled={busy}/>
 <label htmlFor="nadi-login-password">Password</label><div className="nadi-password-field"><input id="nadi-login-password" name="password" type={show?"text":"password"} autoComplete="current-password" maxLength={256} required value={password} onChange={e=>setPassword(e.target.value)} disabled={busy}/>
 <button type="button" aria-controls="nadi-login-password" aria-pressed={show} onClick={()=>setShow(!show)}>{show?"Hide password":"Show password"}</button></div>
 {change&&<><label htmlFor="nadi-login-new-password">New password</label><input id="nadi-login-new-password" type="password" autoComplete="new-password" maxLength={256} required value={newPassword} onChange={e=>setNewPassword(e.target.value)} disabled={busy}/></>}
 {error&&<p role="alert">{error}</p>}<button type="submit" disabled={busy||!username||!password||(change&&!newPassword)}>{busy?"Signing in…":change?"Change password and sign in":"Sign in"}</button>
 </form><p>No self-registration. Contact the approved operator for account or access changes.</p></div></SectionCard>;
}
