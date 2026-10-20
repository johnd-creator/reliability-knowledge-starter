'use client';
import type {ReactNode} from 'react';
import {CaseDraftProvider} from './CaseDraftContext';
import {RecommendationDraftProvider} from './RecommendationDraftContext';

// App Router keeps this workspace layout alive across Back/Forward and module links.
// Leaving for the authentication layout destroys both private in-memory caches.
export default function EngineeringDraftProviders({children}:{children:ReactNode}){
 return <CaseDraftProvider><RecommendationDraftProvider>{children}</RecommendationDraftProvider></CaseDraftProvider>;
}
