'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {api} from '@/lib/api';
import {SiteHeader} from '@/components/site-header';

type Result={payment_id:number;status:string;reference:string};
export default function PaymentReturn(){
 const [reference,setReference]=useState<string|null>(null);
 const [message,setMessage]=useState('Verifying your payment with Paystack…'); const [done,setDone]=useState(false);
 useEffect(()=>{setReference(new URLSearchParams(window.location.search).get('reference'))},[]);
 useEffect(()=>{let active=true;(async()=>{if(reference===null)return;if(!reference){setMessage('No payment reference was provided. Check your project page.');return;}try{const result=await api<Result>('/payments/verify/',{method:'POST',body:JSON.stringify({reference})});if(active){setMessage(result.status==='successful'?'Payment verified. Your project payment is confirmed.':`Payment status: ${result.status}`);setDone(true)}}catch(e){if(active)setMessage(e instanceof Error?e.message:'We could not verify this payment yet. Please refresh your project page shortly.')}})();return()=>{active=false}},[reference]);
 return <><SiteHeader/><main className="shell max-w-2xl py-20"><section className="surface p-8"><div className="eyebrow">WarriWorks payment</div><h1 className="mt-3 text-3xl">{done?'Payment update':'Checking payment'}</h1><p className="mt-4 text-sm leading-7 text-[var(--muted)]">{message}</p>{reference&&<p className="mt-4 break-all text-xs text-[var(--muted)]">Reference: {reference}</p>}<Link href="/customer" className="btn-primary mt-7 inline-flex">Return to dashboard</Link></section></main></>;
}
