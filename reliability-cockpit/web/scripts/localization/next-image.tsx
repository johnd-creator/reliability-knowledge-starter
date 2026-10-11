import React from 'react';
// Test-only renderer for original image bytes. No server-side optimizer is started.
export default function Image({src,alt,width,height}:{src:string;alt:string;width:number;height:number}){return <img src={src} alt={alt} width={width} height={height}/>;}
