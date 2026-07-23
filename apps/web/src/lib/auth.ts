'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { apiPost, AUTH_COOKIE_NAME } from './api';

export type LoginFormState = { error?: string } | null;

interface LoginUser {
  id: number;
  username: string;
  full_name: string | null;
  role: 'YONETICI' | 'CALISAN';
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: LoginUser;
}

// ~1 yil - kucuk, guvenilir bir ekip icin her seferinde sifre sorulmasin.
const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 365;

export async function loginAction(_prevState: LoginFormState, formData: FormData): Promise<LoginFormState> {
  const username = String(formData.get('username') ?? '').trim();
  const password = String(formData.get('password') ?? '');

  if (!username || !password) {
    return { error: 'Kullanıcı adı ve şifre gerekli.' };
  }

  const result = await apiPost<LoginResponse>('/auth/login', { username, password });
  if (result.error !== undefined) {
    return { error: result.error };
  }

  const cookieStore = await cookies();
  cookieStore.set(AUTH_COOKIE_NAME, result.data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: COOKIE_MAX_AGE_SECONDS,
  });

  redirect('/');
}

export async function logoutAction(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(AUTH_COOKIE_NAME);
  redirect('/login');
}
