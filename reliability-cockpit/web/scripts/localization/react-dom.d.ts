// The browser test harness only needs createRoot; production dependencies stay unchanged.
declare module 'react-dom/client' {
 export function createRoot(container:Element): {render(children:import('react').ReactNode):void;unmount():void};
}
