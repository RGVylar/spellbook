import { browser } from '$app/environment';
import type { TokenResponse, User } from '$lib/types';

const TOKEN_KEY = 'spellbook.token';

class AuthStore {
	token = $state<string | null>(browser ? localStorage.getItem(TOKEN_KEY) : null);
	user = $state<User | null>(null);
	loaded = $state(false);

	get isArchimago() {
		return this.user?.role === 'archimago';
	}
	get isModerator() {
		return this.user?.role === 'archimago' || this.user?.role === 'mago';
	}

	apply(res: TokenResponse) {
		this.token = res.accessToken;
		this.user = res.user;
		if (browser) localStorage.setItem(TOKEN_KEY, res.accessToken);
	}

	setUser(user: User) {
		this.user = user;
	}

	logout() {
		this.token = null;
		this.user = null;
		if (browser) localStorage.removeItem(TOKEN_KEY);
	}
}

export const auth = new AuthStore();
