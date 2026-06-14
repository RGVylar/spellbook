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

	schoolMap = $derived(new Map(this.schools.map((s) => [s.id, s])));
	artifactMap = $derived(new Map(this.artifacts.map((a) => [a.id, a])));

	school(id: string): School | undefined {
		return this.schoolMap.get(id);
	}

	findArt(id: string): Artifact | undefined {
		return this.artifactMap.get(id);
	}

	get playable(): Artifact[] {
		return this.artifacts.filter((a) => a.media === 'audio' || a.media === 'video');
	}

	// Igual que playable pero excluyendo los sin preservar (tienen sourceUrl pero no mediaUrl)
	get playablePreserved(): Artifact[] {
		return this.artifacts.filter(
			(a) =>
				(a.media === 'audio' || a.media === 'video') &&
				!(a.sourceUrl && !a.mediaUrl)
		);
	}
}

export const catalog = new CatalogStore();
