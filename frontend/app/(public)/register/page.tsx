import { redirect } from 'next/navigation';

type RegisterPageProps = {
  searchParams: Promise<{ role?: string }>;
};

export default async function RegisterPage({
  searchParams,
}: RegisterPageProps) {
  const params = await searchParams;

  if (params.role === 'artisan') {
    redirect('/artisan-register');
  }

  redirect('/customer-register');
}
