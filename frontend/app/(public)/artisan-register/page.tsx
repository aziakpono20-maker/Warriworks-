
'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

export default function ArtisanRegister() {
  const [v, setV] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
  });

  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const router = useRouter();

  function change(k: string, x: string) {
    setV((previous) => ({ ...previous, [k]: x }));
  }

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError('');

    try {
     await api('/auth/register/artisan/', {
        method: 'POST',
        body: JSON.stringify({
          ...v,
          username: v.email.split('@')[0],
          role: 'artisan',
        }),
      });

      router.push('/artisan');
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to create account'
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-12">
      <form
        onSubmit={submit}
        className="surface w-full max-w-lg p-7 sm:p-10"
      >
        <Link
          href="/"
          className="text-lg font-semibold text-[var(--forest)]"
        >
          WarriWorks.
        </Link>

        <div className="eyebrow mt-8">Artisan registration</div>

        <h1 className="mt-2 text-4xl">Grow your business.</h1>

        <p className="mt-2 text-sm text-[var(--muted)]">
          Join WarriWorks and connect with customers looking for your skills.
        </p>

        <div className="mt-7 grid grid-cols-2 gap-3">
          <label className="text-sm font-semibold">
            First name
            <input
              className="input mt-2"
              required
              value={v.first_name}
              onChange={(e) => change('first_name', e.target.value)}
            />
          </label>

          <label className="text-sm font-semibold">
            Last name
            <input
              className="input mt-2"
              required
              value={v.last_name}
              onChange={(e) => change('last_name', e.target.value)}
            />
          </label>
        </div>

        <label className="mt-4 block text-sm font-semibold">
          Email
          <input
            className="input mt-2"
            type="email"
            required
            autoComplete="email"
            value={v.email}
            onChange={(e) => change('email', e.target.value)}
          />
        </label>

        <label className="mt-4 block text-sm font-semibold">
          Phone number
          <input
            className="input mt-2"
            type="tel"
            required
            autoComplete="tel"
            value={v.phone}
            onChange={(e) => change('phone', e.target.value)}
          />
        </label>

        <label className="mt-4 block text-sm font-semibold">
          Password
          <input
            className="input mt-2"
            type="password"
            minLength={10}
            required
            autoComplete="new-password"
            value={v.password}
            onChange={(e) => change('password', e.target.value)}
          />
        </label>

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={busy}
          className="btn-primary mt-6 w-full disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? 'Creating account…' : 'Create artisan account'}
        </button>

        <p className="mt-5 text-center text-sm text-[var(--muted)]">
          Already registered?{' '}
          <Link
            href="/artisan-login"
            className="font-semibold text-[var(--green)]"
          >
            Artisan login
          </Link>
        </p>

        <p className="mt-3 text-center text-sm text-[var(--muted)]">
          Looking for professional services?{' '}
          <Link
            href="/customer-register"
            className="font-semibold text-[var(--green)]"
          >
            Register as a customer
          </Link>
        </p>
      </form>
    </main>
  );
}
