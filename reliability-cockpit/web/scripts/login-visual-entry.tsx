// Synthetic component QA only: every request is intercepted, no application server.
import React from 'react';
import {createRoot} from 'react-dom/client';
import {ThemeProvider} from '../components/ThemeProvider';
import AuthenticatedWorkspace from '../components/AuthenticatedWorkspace';
import {AppShell} from '../components/AppNavigation';
import LoginPage from '../components/LoginPage';
const identity={subject:'local:SYNTHETIC-VISUAL',username:'QA_VISUAL_ONLY',roles:['ADMIN'],asset_ids:['asset:SYNTHETIC']};
createRoot(document.getElementById('root')!).render(<ThemeProvider>{location.pathname==='/login'?<main className="authentication-layout"><LoginPage/></main>:<AuthenticatedWorkspace identity={identity}><AppShell engineeringVisible><h1>QA SINTETIS — workspace visual</h1><p>Uji komponen terisolasi; bukan data pembangkit.</p></AppShell></AuthenticatedWorkspace>}</ThemeProvider>);
