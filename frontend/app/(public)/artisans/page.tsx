
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Search,
  MapPin,
  BadgeCheck,
  ArrowUpRight,
} from 'lucide-react';

import { SiteHeader } from '@/components/site-header';
import { api, Artisan, Paginated } from '@/lib/api';

export default function ArtisansPage() {
  const [items, setItems] = useState<Artisan[]>([]);
  const [q, setQ] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    api<Paginated<Artisan>>('/artisans/')
      .then((data) => {
        if (active) setItems(data.results);
      })
      .catch((err) => {
        if (active) setError(err.message || 'Unable to load artisans.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const shown = items.filter((artisan) =>
    `${artisan.display_name} ${artisan.skill} ${artisan.location}`
      .toLowerCase()
      .includes(q.toLowerCase())
  );

  const verifiedCount = items.filter((artisan) => artisan.verified).length;

  return (
    <>
      <SiteHeader />

      <main className="shell py-14">
        <div className="eyebrow">Find your person for the job</div>

        <div className="mt-3 flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <h1 className="max-w-2xl text-5xl leading-tight">
              Skilled people.
              <br />
              <span className="italic text-[var(--green)]">
                Right around you.
              </span>
            </h1>

            <p className="mt-4 max-w-lg text-sm leading-7 text-[var(--muted)]">
              Explore verified artisans and find the right experience for
              the work you have in mind.
            </p>
          </div>

          <div className="relative w-full md:max-w-sm">
            <Search
              className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--muted)]"
              size={17}
            />
            <input
              className="input pl-11"
              placeholder="Search skill, name or area"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
        </div>

        <div className="mt-10 border-t border-[var(--line)] pt-5">
          <div className="flex items-center justify-between text-xs text-[var(--muted)]">
            <span>
              {loading
                ? 'Loading artisans…'
                : `${shown.length} artisans found (${verifiedCount} verified)`}
            </span>
            <span>Warri & surrounding communities</span>
          </div>

          {error && (
            <div className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">
              {error}
              <button
                onClick={() => window.location.reload()}
                className="ml-2 font-semibold underline"
              >
                Try again
              </button>
            </div>
          )}

          {!loading && !error && items.length === 0 && (
            <div className="mt-8 rounded-xl border border-dashed border-[var(--line)] p-12 text-center">
              <h2 className="text-2xl">Artisans are coming soon</h2>
              <p className="mt-2 text-sm text-[var(--muted)]">
                We are preparing the directory. Check back soon to discover
                skilled professionals around Warri.
              </p>
            </div>
          )}

          {!loading && !error && items.length > 0 && shown.length === 0 && (
            <div className="mt-8 rounded-xl border border-dashed border-[var(--line)] p-12 text-center">
              <h2 className="text-2xl">No matching artisans found</h2>
              <p className="mt-2 text-sm text-[var(--muted)]">
                Try another skill, name or location.
              </p>
            </div>
          )}

          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {shown.map((artisan) => (
              <article
                key={artisan.id}
                className="surface p-5 transition hover:-translate-y-1 hover:shadow-lg"
              >
                <div className="flex items-start justify-between">
                  <div className="grid h-12 w-12 place-items-center rounded-full bg-[#E6EBDD] font-serif text-xl text-[var(--forest)]">
                    {artisan.display_name.slice(0, 1).toUpperCase()}
                  </div>

                  {artisan.verified && (
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-[var(--green)]">
                      <BadgeCheck size={15} />
                      Verified
                    </span>
                  )}
                </div>

                <h2 className="mt-5 text-2xl">{artisan.display_name}</h2>

                <p className="mt-1 text-sm font-semibold text-[var(--green)]">
                  {artisan.skill}
                </p>

                <p className="mt-3 flex items-center gap-1 text-xs text-[var(--muted)]">
                  <MapPin size={14} />
                  {artisan.location}
                </p>

                {artisan.bio && (
                  <p className="mt-4 line-clamp-2 text-sm leading-6 text-[var(--muted)]">
                    {artisan.bio}
                  </p>
                )}

                <div className="mt-6 flex items-center justify-between border-t border-[var(--line)] pt-4">
                  <Link
                    href={`/artisans/${artisan.id}`}
                    className="text-sm font-semibold text-[var(--forest)]"
                  >
                    View profile
                  </Link>

                  <Link
                    href={`/request/${artisan.id}`}
                    className="flex items-center gap-1 text-sm font-semibold text-[var(--green)]"
                  >
                    Request <ArrowUpRight size={16} />
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}
