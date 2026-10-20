// Build actual components for isolated test runners; never starts a frontend.
import {mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {browserBundle} from './localization-browser-build.mjs';
if(process.argv.length!==3)throw Error('Usage: node scripts/pdm-follow-up-browser-bundle.mjs OUTPUT_DIRECTORY');
const target=resolve(process.argv[2]),bundle=await browserBundle('scripts/pdm-auth/entry.tsx');
mkdirSync(target,{recursive:true});writeFileSync(target+'/candidate.js',bundle.js);writeFileSync(target+'/candidate.css',bundle.css);
console.log('Isolated PdM package component bundle ready.');
