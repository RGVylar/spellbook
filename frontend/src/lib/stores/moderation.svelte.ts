import { api } from '$lib/api';
import { auth } from '$lib/stores/auth.svelte';

class ModerationStore {
	pendingCount = $state(0);

	async refresh(): Promise<void> {
		if (!auth.isModerator) {
			this.pendingCount = 0;
			return;
		}
		try {
			const res = await api.get<{ count: number }>('/artifacts/pending-count');
			this.pendingCount = res.count;
		} catch {
			this.pendingCount = 0;
		}
	}
}

export const moderation = new ModerationStore();
