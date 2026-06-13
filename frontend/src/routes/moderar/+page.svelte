<script lang="ts">
	import { api } from '$lib/api';
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { moderation } from '$lib/stores/moderation.svelte';
	import type { Artifact } from '$lib/types';

	type Tab = 'propuestas' | 'huerfanos';
	let tab = $state<Tab>('propuestas');

	let pending = $state<Artifact[]>([]);
	let orphans = $state<Artifact[]>([]);
	let loadingPending = $state(true);
	let loadingOrphans = $state(false);
	let orphansLoaded = $state(false);
	let error = $state('');

	$effect(() => {
		if (!auth.loaded) return;
		if (!auth.isModerator) { loadingPending = false; return; }
		void api
			.get<Artifact[]>('/artifacts?status=pendiente')
			.then((list) => (pending = list))
			.catch(() => (pending = []))
			.finally(() => (loadingPending = false));
	});

	$effect(() => {
		if (tab !== 'huerfanos' || orphansLoaded || !auth.isModerator) return;
		orphansLoaded = true;
		loadingOrphans = true;
		void api
			.get<Artifact[]>('/artifacts/needs-ingest')
			.then((list) => (orphans = list))
			.catch(() => (orphans = []))
			.finally(() => (loadingOrphans = false));
	});

	async function judge(art: Artifact, status: 'sellado' | 'rechazado') {
		error = '';
		try {
			await api.patch(`/artifacts/${art.id}/status`, { status });
			pending = pending.filter((a) => a.id !== art.id);
			await Promise.all([moderation.refresh(), status === 'sellado' ? catalog.load(true) : Promise.resolve()]);
		} catch (e) {
			error = e instanceof Error ? e.message : 'El juicio falló';
		}
	}
</script>

<svelte:head><title>Cónclave · SPELLBOOK</title></svelte:head>

<div class="canvas" style="max-width: 900px">
	<SectionHead
		eyebrow="El juicio del cónclave"
		title="Sala de moderación"
		sub="Propuestas en espera y artefactos cuya preservación ha fallado."
	/>

	{#if !auth.isModerator}
		<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
			Solo magos y el <span class="archimago">Archimago</span> participan del juicio.
		</div>
	{:else}
		<!-- Tabs -->
		<div class="seg" style="margin-bottom: 28px; width: fit-content">
			<button class="cursor-star" class:on={tab === 'propuestas'} onclick={() => (tab = 'propuestas')}>
				<Icon name="scroll" s={15} /> Propuestas
				{#if pending.length > 0}
					<span class="badge">{pending.length}</span>
				{/if}
			</button>
			<button class="cursor-star" class:on={tab === 'huerfanos'} onclick={() => (tab = 'huerfanos')}>
				<Icon name="upload" s={15} /> Sin preservar
				{#if orphans.length > 0}
					<span class="badge" style="background: var(--ember)">{orphans.length}</span>
				{/if}
			</button>
		</div>

		{#if error}<p style="color: var(--ember); font-size: 13px">{error}</p>{/if}

		<!-- Tab: Propuestas -->
		{#if tab === 'propuestas'}
			{#if loadingPending}
				<p class="t-arcane" style="font-size: 22px; color: var(--gold); text-align: center; padding: 40px 0">
					El oráculo medita…
				</p>
			{:else if pending.length === 0}
				<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
					No hay propuestas aguardando juicio. El cónclave descansa.
				</div>
			{:else}
				<div class="list-cards">
					{#each pending as a (a.id)}
						{@const s = catalog.school(a.school)}
						<div class="lrow" style="align-items: flex-start; cursor: default">
							<div class="lglyph">{a.glyph}</div>
							<div style="flex: 1; min-width: 0">
								<div class="row gap-2" style="margin-bottom: 4px; flex-wrap: wrap">
									<ArtifactBadge type={a.type} size={12} />
									<a class="card-title cursor-star" style="margin: 0; font-size: 15px; color: var(--parchment); text-decoration: none" href="/artefacto/{a.id}">
										{a.title}
									</a>
								</div>
								<div class="card-meta" style="margin-bottom: 8px">
									<span style="color: {s?.hue}">{s?.glyph} {s?.name}</span>
									<span class="dot"></span><span>{a.era}</span>
									<span class="dot"></span><span>propuesto por {a.sealedBy}</span>
								</div>
								<p class="muted" style="font-size: 13px; line-height: 1.55; margin: 0">
									{a.desc.length > 220 ? a.desc.slice(0, 219) + '…' : a.desc}
								</p>
							</div>
							<div style="display: flex; flex-direction: column; gap: 8px; flex: 0 0 auto">
								<button
									class="btn cursor-star"
									style="border-color: var(--gold); color: var(--gold-bright)"
									onclick={() => judge(a, 'sellado')}
								>
									<Icon name="check" s={15} /> Sellar
								</button>
								<button class="btn ghost cursor-star" onclick={() => judge(a, 'rechazado')}>
									<Icon name="close" s={15} /> Rechazar
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}

		<!-- Tab: Sin preservar -->
		{:else if tab === 'huerfanos'}
			{#if loadingOrphans}
				<p class="t-arcane" style="font-size: 22px; color: var(--gold); text-align: center; padding: 40px 0">
					El oráculo medita…
				</p>
			{:else if orphans.length === 0}
				<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
					Todos los artefactos tienen su esencia preservada.
				</div>
			{:else}
				<p class="muted" style="font-size: 13px; margin-bottom: 16px">
					Artefactos sellados cuyo archivo no pudo descargarse. Ve al artefacto para relanzar la descarga o subir el archivo manualmente.
				</p>
				<div class="list-cards">
					{#each orphans as a (a.id)}
						{@const s = catalog.school(a.school)}
						<div class="lrow" style="align-items: center; cursor: default">
							<div class="lglyph">{a.glyph}</div>
							<div style="flex: 1; min-width: 0">
								<div class="row gap-2" style="margin-bottom: 4px; flex-wrap: wrap">
									<ArtifactBadge type={a.type} size={12} />
									<span class="card-title" style="margin: 0; font-size: 15px">{a.title}</span>
								</div>
								<div class="card-meta">
									<span style="color: {s?.hue}">{s?.glyph} {s?.name}</span>
									<span class="dot"></span><span>{a.era}</span>
									<span class="dot"></span><span>sellado por {a.sealedBy}</span>
								</div>
								{#if a.sourceUrl}
									<div style="margin-top: 5px; font-size: 11.5px; color: var(--faint); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 420px">
										{a.sourceUrl}
									</div>
								{/if}
							</div>
							<a
								class="btn cursor-star"
								href="/artefacto/{a.id}"
								style="text-decoration: none; flex-shrink: 0; border-color: var(--ember); color: var(--ember)"
							>
								<Icon name="upload" s={14} /> Preservar
							</a>
						</div>
					{/each}
				</div>
			{/if}
		{/if}
	{/if}
</div>

<style>
	.badge {
		display: inline-grid;
		place-items: center;
		min-width: 18px;
		height: 18px;
		padding: 0 4px;
		border-radius: 9px;
		background: var(--gold);
		color: var(--ink);
		font-size: 10px;
		font-weight: 700;
		line-height: 1;
	}
</style>
