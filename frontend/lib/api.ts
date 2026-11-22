
const API =
  process.env.NEXT_PUBLIC_API_URL ??
  'https://super-duper-adventure-5gpq4x66qxxgf4pqq-8000.app.github.dev/api';

export type Artisan = {
  id: number;
  display_name: string;
  skill: string;
  location: string;
  bio: string;
  verified: boolean;
  profile_image: string | null;
  years_experience: number;
  is_available: boolean;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

async function getCsrfToken(): Promise<string> {
  const response = await fetch(`${API}/csrf/`, {
    method: 'GET',
    credentials: 'include',
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error('Unable to initialize security token.');
  }

  const data = await response.json();

  if (!data.csrfToken) {
    throw new Error('Security token was not provided by the server.');
  }

  return data.csrfToken;
}

export async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const method = (options.method ?? 'GET').toUpperCase();
  const headers = new Headers(options.headers);

  // Only add JSON content type when a request has a body.
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has('Content-Type')
  ) {
    headers.set('Content-Type', 'application/json');
  }

  // Initialize CSRF protection for requests that modify data.
  if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
    const csrfToken = await getCsrfToken();
    headers.set('X-CSRFToken', csrfToken);
  }

  const response = await fetch(`${API}${path}`, {
    ...options,
    headers,
    credentials: 'include',
    cache: 'no-store',
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const body = await response.json();
      message = body.detail ?? JSON.stringify(body);
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}
