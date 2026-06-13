import { auth } from '$lib/stores/auth.svelte';

const BASE = '/api';

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
	const headers: Record<string, string> = { 'Content-Type': 'application/json' };
	const token = auth.token;
	if (token) headers['Authorization'] = `Bearer ${token}`;

	const res = await fetch(`${BASE}${path}`, { ...opts, headers: { ...headers, ...opts.headers } });

	if (res.status === 401 && token) {
		auth.logout();
		throw new Error('La sesión ha expirado');
	}
	if (!res.ok) {
		const body = await res.json().catch(() => ({}));
		const detail = body.detail;
		throw new Error(
			typeof detail === 'string' ? detail : detail?.[0]?.msg || res.statusText
		);
	}
	if (res.status === 204) return undefined as T;
	return res.json();
}

async function requestForm<T>(path: string, body: FormData): Promise<T> {
	const headers: Record<string, string> = {};
	const token = auth.token;
	if (token) headers['Authorization'] = `Bearer ${token}`;
	const res = await fetch(`${BASE}${path}`, { method: 'POST', body, headers });
	if (!res.ok) {
		const b = await res.json().catch(() => ({}));
		throw new Error(typeof b.detail === 'string' ? b.detail : res.statusText);
	}
	if (res.status === 204) return undefined as T;
	return res.json();
}

export const api = {
	get: <T>(path: string) => request<T>(path),
	post: <T>(path: string, body?: unknown) =>
		request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
	postForm: <T>(path: string, body: FormData) => requestForm<T>(path, body),
	patch: <T>(path: string, body: unknown) =>
		request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
	del: <T>(path: string) => request<T>(path, { method: 'DELETE' })
};
