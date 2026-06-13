<script lang="ts">
	import { page } from '$app/state';
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import RuneCloud from '$lib/components/RuneCloud.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import SpellCard from '$lib/components/SpellCard.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { ARTIFACT_TYPES, TYPE_META, type ArtifactType } from '$lib/types';

	let view = $state<'grid' | 'list'>('grid');
	let types = $state<string[]>(page.url.searchParams.get('type') ? [page.url.searchParams.get('type')!] : []);
	let schools = $state<string[]>(
		page.url.searchParams.get('school') ? [page.url.searchParams.get('school')!] : []
	);
	let runes = $state<string[]>(page.url.searchParams.get('rune') ? [page.url.searchParams.get('rune')!] : []);

	function toggle(arr: string[], v: string): string[] {
		return arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v];
	}

	const filtered = $derived(
		catalog.artifacts.filter(
			(a) =>
				(types.length === 0 || types.includes(a.type)) &&
				(schools.length === 0 || schools.includes(a.school)) &&
				(runes.length === 0 || runes.some((r) => a.runes.includes(r)))
		)
	);

	const hasFilters = $derived(types.length > 0 || schools.length > 0 || runes.length > 0);
</script>

<svelte:head><title>Explorador · SPELLBOOK</title></svelte:head>

<div class="canvas">
	<SectionHead
		eyebrow="El Grimorio"
		title="Explorador de artefactos"
		sub="Filtra la bóveda por tipo, escuela, época y runas."
	/>
	<div style="display: flex; gap: 32px; align-items: flex-start; flex-wrap: wrap">
		<!-- Sidebar filtros -->
		<aside class="filters">
			<div class="fgroup">
				<h4>Tipo de artefacto</h4>
				{#each ARTIFACT_TYPES as t (t)}
					<div
						class="fitem cursor-star"
						class:on={types.includes(t)}
						role="checkbox"
						aria-checked={types.includes(t)}
						tabindex="0"
						onclick={() => (types = toggle(types, t))}
						onkeydown={(e) => e.key === 'Enter' && (types = toggle(types, t))}
					>
						<span class="fcheck">{#if types.includes(t)}<Icon name="check" s={12} />{/if}</span>
						{TYPE_META[t as ArtifactType]?.label}
						<span class="fcount">{catalog.artifacts.filter((a) => a.type === t).length}</span>
					</div>
				{/each}
			</div>
			<div class="fgroup">
				<h4>Escuela de magia</h4>
				{#each catalog.schools as s (s.id)}
					<div
						class="fitem cursor-star"
						class:on={schools.includes(s.id)}
						role="checkbox"
						aria-checked={schools.includes(s.id)}
						tabindex="0"
						onclick={() => (schools = toggle(schools, s.id))}
						onkeydown={(e) => e.key === 'Enter' && (schools = toggle(schools, s.id))}
					>
						<span class="fcheck">{#if schools.includes(s.id)}<Icon name="check" s={12} />{/if}</span>
						<span style="color: {s.hue}; margin-right: 2px">{s.glyph}</span>{s.name}
						<span class="fcount">{s.count}</span>
					</div>
				{/each}
			</div>
			<div class="fgroup">
				<h4>Runas</h4>
				<RuneCloud runes={catalog.runes.slice(0, 12)} active={runes} onToggle={(r) => (runes = toggle(runes, r))} />
			</div>
		</aside>

		<!-- Resultados -->
		<div style="flex: 1; min-width: 280px">
			<div class="row" style="justify-content: space-between; margin-bottom: 16px">
				<span class="muted" style="font-size: 13px">
					{filtered.length} artefacto{filtered.length !== 1 ? 's' : ''}
					{#if hasFilters}
						<button
							class="btn ghost cursor-star"
							style="padding: 2px 8px; margin-left: 8px; font-size: 12px"
							onclick={() => {
								types = [];
								schools = [];
								runes = [];
							}}
						>
							limpiar
						</button>
					{/if}
				</span>
				<div class="seg">
					<button class="cursor-star" class:on={view === 'grid'} onclick={() => (view = 'grid')}>
						<Icon name="grid" s={16} /> Cuadrícula
					</button>
					<button class="cursor-star" class:on={view === 'list'} onclick={() => (view = 'list')}>
						<Icon name="list" s={16} /> Lista
					</button>
				</div>
			</div>
			{#if filtered.length === 0}
				<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
					Ningún artefacto responde a esa invocación.
				</div>
			{:else if view === 'grid'}
				<div class="grid-cards">
					{#each filtered as a (a.id)}
						<SpellCard art={a} />
					{/each}
				</div>
			{:else}
				<div class="list-cards">
					{#each filtered as a (a.id)}
						{@const s = catalog.school(a.school)}
						<a class="lrow cursor-star" href="/artefacto/{a.id}" style="text-decoration: none; color: inherit">
							<div class="lglyph">{a.glyph}</div>
							<div style="flex: 1; min-width: 0">
								<div class="row gap-2" style="margin-bottom: 4px">
									<ArtifactBadge type={a.type} size={12} />
									<span class="card-title" style="margin: 0; font-size: 15px">{a.title}</span>
								</div>
								<div class="card-meta">
									<span style="color: {s?.hue}">{s?.glyph} {s?.name}</span>
									<span class="dot"></span><span>{a.era}</span>
									<span class="dot"></span><span>{a.links.length} vínculos</span>
								</div>
							</div>
							<div class="runecloud" style="max-width: 220px; justify-content: flex-end">
								{#each a.runes.slice(0, 2) as r (r)}
									<span class="rune" style="pointer-events: none">{r}</span>
								{/each}
							</div>
							<Icon name="chevron" s={18} style="color: var(--faint)" />
						</a>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
