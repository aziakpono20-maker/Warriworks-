
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

export default function CustomerLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError('');

    try {
      const user = await api<{ role: string }>('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      if (user.role !== 'customer') {
        await api('/auth/logout/', { method: 'POST' });
        setError('This is not a customer account. Please use the artisan login page.');
        return;
      }

      router.push('/customer');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      <section className="hidden flex-col justify-between bg-[var(--forest)] p-12 text-white lg:flex">
        <Link href="/" className="text-2xl font-semibold tracking-tight">
          WarriWorks.
        </Link>

        <div>
          <p className="text-xs font-bold uppercase tracking-[.18em] text-[#D5B86E]">
            Find trusted artisans in Warri
          </p>
          <h1 className="mt-5 max-w-lg text-6xl leading-[1.03] text-white">
            Good work starts with the right hands.
          </h1>
          <p className="mt-6 max-w-md text-sm leading-7 text-white/70">
            Find skilled professionals and manage your service requests.
          </p>
        </div>

        <p className="text-xs text-white/50">© WarriWorks</p>
      </section>

      <section className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-[410px]">
          <Link href="/" className="text-lg font-semibold text-[var(--forest)] lg:hidden">
            WarriWorks.
          </Link>

          <div className="eyebrow mt-10">Customer portal</div>
          <h2 className="mt-3 text-4xl">Welcome back.</h2>
          <p className="mt-3 text-sm text-[var(--muted)]">
            Sign in to find artisans and manage your service requests.
          </p>

          <label className="mt-8 block text-sm font-semibold">
            Email address
            <input
              className="input mt-2"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label className="mt-5 block text-sm font-semibold">
            Password
            <input
              className="input mt-2"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && (
            <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {error}
            </p>
          )}

          <button
            disabled={busy}
            className="btn-primary mt-7 w-full disabled:opacity-60"
          >
            {busy ? 'Signing in…' : 'Customer sign in'}
          </button>

          <p className="mt-6 text-center text-sm text-[var(--muted)]">
            New customer?{' '}
            <Link
              className="font-semibold text-[var(--green)]"
              href="/customer-register"
            >
              Create a customer account
            </Link>
          </p>

          <p className="mt-3 text-center text-sm text-[var(--muted)]">
            Are you an artisan?{' '}
            <Link
              className="font-semibold text-[var(--green)]"
              href="/artisan-login"
            >
              Artisan sign in
            </Link>
          </p>
        </form>
      </section>
    </main>
  );
}
