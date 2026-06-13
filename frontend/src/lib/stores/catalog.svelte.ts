import { api } from '$lib/api';
import type { Artifact, School, Spell, Stats } from '$lib/types';

/* Catálogo global del grimorio (lo sellado): alimenta oráculo, tarjetas y filtros. */
class CatalogStore {
	artifacts = $state<Artifact[]>([]);
	schools = $state<School[]>([]);
	spells = $state<Spell[]>([]);
	runes = $state<string[]>([]);
	stats = $state<Stats | null>(null);
	loaded = $state(false);

	async load(force = false): Promise<void> {
		if (this.loaded && !force) return;
		const [artifacts, schools, spells, runes, stats] = await Promise.all([
			api.get<Artifact[]>('/artifacts'),
			api.get<School[]>('/schools'),
			api.get<Spell[]>('/spells'),
			api.get<string[]>('/runes'),
			api.get<Stats>('/stats')
		]);
		this.artifacts = artifacts;
		this.schools = schools;
		this.spells = spells;
		this.runes = runes;
		this.stats = stats;
		this.loaded = true;
	}

	school(id: string): School | undefined {
		return this.schools.find((s) => s.id === id);
	}

	findArt(id: string): Artifact | undefined {
		return this.artifacts.find((a) => a.id === id);
	}

	get playable(): Artifact[] {
		return this.artifacts.filter((a) => a.media === 'audio' || a.media === 'video');
	}
}

export const catalog = new CatalogStore();
