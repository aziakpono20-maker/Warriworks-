'use client';

import { FormEvent, useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { SiteHeader } from '@/components/site-header';

type Profile = {
  display_name: string;
  skill: string;
  location: string;
  bio: string;
  phone_public: boolean;
  years_experience: number;
  is_available: boolean;
};

const empty: Profile = {
  display_name: '', skill: '', location: '', bio: '',
  phone_public: false, years_experience: 0, is_available: true,
};

export default function ArtisanProfilePage() {
  const [profile, setProfile] = useState<Profile>(empty);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    api<Profile>('/artisans/me/').then(setProfile)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function update<K extends keyof Profile>(key: K, value: Profile[K]) {
    setProfile((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true); setError(''); setSuccess('');
    try {
      const saved = await api<Profile>('/artisans/me/', {
        method: 'PATCH', body: JSON.stringify(profile),
      });
      setProfile(saved);
      setSuccess('Your artisan profile has been updated.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to save your profile.');
    } finally { setSaving(false); }
  }

  return <><SiteHeader /><main className="shell max-w-3xl py-10">
    <Link href="/artisan" className="text-sm text-[var(--green)]">← Back to workspace</Link>
    <div className="eyebrow mt-6">Artisan workspace</div>
    <h1 className="mt-2 text-4xl">Your professional profile</h1>
    <p className="mt-2 text-sm leading-6 text-[var(--muted)]">Keep your service details accurate so customers understand what you do and where you work. Verification status is managed separately by WarriWorks.</p>
    {loading ? <p className="mt-8">Loading your profile…</p> : <form onSubmit={submit} className="surface mt-8 space-y-5 p-6">
      <Field label="Business or display name"><input required minLength={2} className="input" value={profile.display_name} onChange={e => update('display_name', e.target.value)} /></Field>
      <Field label="Primary skill or service"><input required className="input" placeholder="e.g. Plumbing, Electrical, Carpentry" value={profile.skill} onChange={e => update('skill', e.target.value)} /></Field>
      <Field label="Service location"><input required className="input" placeholder="e.g. Effurun, Warri" value={profile.location} onChange={e => update('location', e.target.value)} /></Field>
      <Field label="About your work"><textarea rows={5} maxLength={3000} className="input" value={profile.bio} onChange={e => update('bio', e.target.value)} placeholder="Describe your experience, services and what customers can expect." /></Field>
      <Field label="Years of experience"><input type="number" min={0} max={80} className="input" value={profile.years_experience} onChange={e => update('years_experience', Math.max(0, Number(e.target.value)))} /></Field>
      <label className="flex items-center gap-3 text-sm"><input type="checkbox" checked={profile.is_available} onChange={e => update('is_available', e.target.checked)} /> I am currently available for new work</label>
      <label className="flex items-center gap-3 text-sm"><input type="checkbox" checked={profile.phone_public} onChange={e => update('phone_public', e.target.checked)} /> Allow my phone number to be shown publicly (where supported)</label>
      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {success && <p role="status" className="rounded-lg bg-green-50 p-3 text-sm text-green-800">{success}</p>}
      <button disabled={saving} className="btn-primary" type="submit">{saving ? 'Saving…' : 'Save profile'}</button>
    </form>}
  </main></>;
}

function Field({label, children}:{label:string;children:React.ReactNode}) {
  return <label className="block space-y-2 text-sm font-medium">{label}{children}</label>;
}
