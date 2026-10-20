import type {QaSession} from './product-records';

export type QaSessionEvent = {state:'ready';session:QaSession}|{state:'expired'|'denied'|'disabled'};
export const QA_SESSION_EVENT='nadi:qa-session';
// In-memory privacy lifecycle only. The server remains the session authority.
export function notifyQaSession(detail:QaSessionEvent){
 if(typeof window!=='undefined')window.dispatchEvent(new CustomEvent(QA_SESSION_EVENT,{detail}));
}
