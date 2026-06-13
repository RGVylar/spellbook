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
	const ERA_MIN = 1970;
	const ERA_MAX = new Date().getFullYear();

	const initEra = page.url.searchParams.get('era');
	let eraA = $state(initEra ? Number(initEra) : ERA_MIN);
	let eraB = $state(ERA_MAX);

	const eraFrom = $derived(Math.min(eraA, eraB));
	const eraTo   = $derived(Math.max(eraA, eraB));
	const eraActive = $derived(eraFrom > ERA_MIN || eraTo < ERA_MAX);

	let barEl = $state<HTMLDivElement | undefined>();

	function startDrag(which: 'A' | 'B') {
		function onMove(e: MouseEvent) {
			if (!barEl) return;
			const r = barEl.getBoundingClientRect();
			const yr = Math.round(ERA_MIN + Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * (ERA_MAX - ERA_MIN));
			if (which === 'A') eraA = yr; else eraB = yr;
		}
		function onUp() { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); }
		window.addEventListener('mousemove', onMove);
		window.addEventListener('mouseup', onUp);
	}

	function commitEraInput(which: 'A' | 'B', raw: string) {
		const v = parseInt(raw);
		if (isNaN(v)) return;
		const clamped = Math.max(ERA_MIN, Math.min(ERA_MAX, v));
		if (which === 'A') eraA = clamped; else eraB = clamped;
	}

	function toggle(arr: string[], v: string): string[] {
		return arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v];
	}

	const filtered = $derived(
		catalog.artifacts.filter(
			(a) =>
				(types.length === 0 || types.includes(a.type)) &&
				(schools.length === 0 || schools.includes(a.school)) &&
				(runes.length === 0 || runes.some((r) => a.runes.includes(r))) &&
				(!eraActive || (a.era >= eraFrom && a.era <= eraTo))
		)
	);

	const hasFilters = $derived(types.length > 0 || schools.length > 0 || runes.length > 0 || eraActive);
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
				<h4>Época</h4>
				<div class="era-inputs">
					<div class="era-inp-wrap">
						<div class="era-inp-label">desde</div>
						<input
							class="era-inp"
							type="text"
							inputmode="numeric"
							value={eraFrom}
							onblur={(e) => commitEraInput('A', (e.target as HTMLInputElement).value)}
							onkeydown={(e) => { if (e.key === 'Enter') { commitEraInput('A', (e.target as HTMLInputElement).value); (e.target as HTMLInputElement).blur(); } }}
						/>
					</div>
					<span class="era-sep">—</span>
					<div class="era-inp-wrap">
						<div class="era-inp-label">hasta</div>
						<input
							class="era-inp"
							type="text"
							inputmode="numeric"
							value={eraTo}
							onblur={(e) => commitEraInput('B', (e.target as HTMLInputElement).value)}
							onkeydown={(e) => { if (e.key === 'Enter') { commitEraInput('B', (e.target as HTMLInputElement).value); (e.target as HTMLInputElement).blur(); } }}
						/>
					</div>
				</div>
				<div class="era-bar-wrap">
					<div class="era-bar" bind:this={barEl}>
						<div class="era-track">
							<div class="era-fill" style="left:{((eraFrom-ERA_MIN)/(ERA_MAX-ERA_MIN))*100}%; width:{((eraTo-eraFrom)/(ERA_MAX-ERA_MIN))*100}%"></div>
						</div>
						<div
							class="era-thumb cursor-star"
							style="left:{((eraA-ERA_MIN)/(ERA_MAX-ERA_MIN))*100}%"
							role="slider" aria-label="Año inicio" aria-valuemin={ERA_MIN} aria-valuemax={ERA_MAX} aria-valuenow={eraA}
							tabindex="0"
							onmousedown={() => startDrag('A')}
						></div>
						<div
							class="era-thumb cursor-star"
							style="left:{((eraB-ERA_MIN)/(ERA_MAX-ERA_MIN))*100}%"
							role="slider" aria-label="Año fin" aria-valuemin={ERA_MIN} aria-valuemax={ERA_MAX} aria-valuenow={eraB}
							tabindex="0"
							onmousedown={() => startDrag('B')}
						></div>
					</div>
					<div class="era-minmax">
						<span>{ERA_MIN}</span><span>{ERA_MAX}</span>
					</div>
				</div>
				{#if eraFrom === eraTo}
					<div class="era-hint">Año exacto: <strong>{eraFrom}</strong></div>
				{:else if eraActive}
					<div class="era-hint">{eraTo - eraFrom} año{eraTo - eraFrom !== 1 ? 's' : ''} seleccionados</div>
				{/if}
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
								eraA = ERA_MIN;
								eraB = ERA_MAX;
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
