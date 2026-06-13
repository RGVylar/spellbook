<script lang="ts">
	import { api } from '$lib/api';
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import type { Artifact } from '$lib/types';

	let orphans = $state<Artifact[]>([]);
	let loading = $state(true);

	$effect(() => {
		if (!auth.loaded) return;
		if (!auth.isModerator) { loading = false; return; }
		void api
			.get<Artifact[]>('/artifacts/needs-ingest')
			.then((list) => (orphans = list))
			.catch(() => (orphans = []))
			.finally(() => (loading = false));
	});
</script>

<svelte:head><title>Sin preservar · SPELLBOOK</title></svelte:head>

<div class="canvas" style="max-width: 900px">
	<SectionHead
		eyebrow="El rito de preservación"
		title="Sin preservar"
		sub="Artefactos sellados cuyo archivo no pudo descargarse. Ve al artefacto para relanzar la descarga o subir el archivo manualmente."
	/>

	{#if !auth.isModerator}
		<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
			Solo magos y el <span class="archimago">Archimago</span> acceden a esta sala.
		</div>
	{:else if loading}
		<p class="t-arcane" style="font-size: 22px; color: var(--gold); text-align: center; padding: 40px 0">
			El oráculo medita…
		</p>
	{:else if orphans.length === 0}
		<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
			Todos los artefactos tienen su esencia preservada.
		</div>
	{:else}
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
</div>
