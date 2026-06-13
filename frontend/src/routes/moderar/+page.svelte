<script lang="ts">
	import { api } from '$lib/api';
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { moderation } from '$lib/stores/moderation.svelte';
	import type { Artifact } from '$lib/types';

	let pending = $state<Artifact[]>([]);
	let loading = $state(true);
	let error = $state('');

	$effect(() => {
		if (!auth.loaded) return;
		if (!auth.isModerator) {
			loading = false;
			return;
		}
		void api
			.get<Artifact[]>('/artifacts?status=pendiente')
			.then((list) => (pending = list))
			.catch(() => (pending = []))
			.finally(() => (loading = false));
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

<svelte:head><title>Propuestas · SPELLBOOK</title></svelte:head>

<div class="canvas" style="max-width: 900px">
	<SectionHead
		eyebrow="El juicio del cónclave"
		title="Propuestas pendientes"
		sub="Conocimiento que los aprendices ofrecen al grimorio. Sella lo digno, rechaza lo profano."
	/>

	{#if !auth.isModerator}
		<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
			Solo magos y el Archimago participan del juicio.
		</div>
	{:else if loading}
		<p class="t-arcane" style="font-size: 22px; color: var(--gold); text-align: center; padding: 40px 0">
			El oráculo medita…
		</p>
	{:else if pending.length === 0}
		<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
			No hay propuestas aguardando juicio. El cónclave descansa.
		</div>
	{:else}
		{#if error}<p style="color: var(--ember); font-size: 13px">{error}</p>{/if}
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
</div>
