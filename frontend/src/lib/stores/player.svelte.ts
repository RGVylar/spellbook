import { browser } from '$app/environment';
import { api } from '$lib/api';
import type { Artifact } from '$lib/types';

const TRACK_KEY = 'spellbook.track';

function restore(): Artifact | null {
	if (!browser) return null;
	try {
		const raw = localStorage.getItem(TRACK_KEY);
		return raw ? (JSON.parse(raw) as Artifact) : null;
	} catch {
		return null;
	}
}

class PlayerStore {
	// El autoplay está bloqueado tras recargar → la pista restaurada reaparece en pausa
	current = $state<Artifact | null>(restore());
	playing = $state(false);
	queue = $state<Artifact[]>([]);
	currentTime = $state(0);
	duration = $state(0);

	/** Petición pendiente que ArcanePlayer consume con $effect */
	intent = $state<{ action: 'play' | 'pause' } | null>(null);

	play(art: Artifact, queue?: Artifact[]) {
		if (queue) this.queue = queue.filter((a) => a.media === 'audio' || a.media === 'video');
		if (this.current?.id === art.id) {
			this.intent = { action: this.playing ? 'pause' : 'play' };
			return;
		}
		this.current = art;
		this.currentTime = 0;
		this.duration = 0;
		this.intent = { action: 'play' };
		if (browser) void api.post(`/artifacts/${art.id}/view`, {}).catch(() => {});
		if (browser) {
			try {
				localStorage.setItem(TRACK_KEY, JSON.stringify(art));
			} catch {
				/* sin persistencia */
			}
		}
	}

	toggle() {
		if (!this.current) return;
		this.intent = { action: this.playing ? 'pause' : 'play' };
	}

	step(dir: 1 | -1) {
		if (this.queue.length === 0 || !this.current) return;
		let i = this.queue.findIndex((a) => a.id === this.current?.id);
		if (i === -1) i = 0;
		const next = this.queue[(i + dir + this.queue.length) % this.queue.length];
		this.play(next);
	}
}

export const player = new PlayerStore();
