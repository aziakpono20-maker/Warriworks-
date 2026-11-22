import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'WarriWorks — Find trusted artisans in Warri',description:'Connect with skilled, verified local artisans around Warri.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
