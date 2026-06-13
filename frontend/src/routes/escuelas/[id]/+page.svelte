<script lang="ts">
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import Icon from '$lib/components/Icon.svelte';
	import SealRing from '$lib/components/SealRing.svelte';
	import SpellCard from '$lib/components/SpellCard.svelte';
	import StarSep from '$lib/components/StarSep.svelte';
	import type { Artifact, School } from '$lib/types';

	const id = $derived(page.params.id ?? '');

	let school = $state<School | null>(null);
	let artifacts = $state<Artifact[]>([]);
	let loading = $state(true);

	$effect(() => {
		const schoolId = id;
		loading = true;
		void api
			.get<{ school: School; artifacts: Artifact[] }>(`/schools/${schoolId}`)
			.then((res) => {
				school = res.school;
				artifacts = res.artifacts;
			})
			.catch(() => (school = null))
			.finally(() => (loading = false));
	});
</script>

<svelte:head><title>{school?.name ?? 'Escuela'} · SPELLBOOK</title></svelte:head>

<div class="canvas">
	<a class="btn ghost cursor-star" style="margin-bottom: 18px; padding: 6px 10px; text-decoration: none" href="/escuelas">
		<Icon name="chevron" s={16} style="transform: rotate(180deg)" /> Todas las escuelas
	</a>
	{#if loading}
		<p class="t-arcane" style="font-size: 22px; color: var(--gold); text-align: center; padding: 60px 0">
			Consultando el grimorio…
		</p>
	{:else if !school}
		<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
			Esa escuela no consta entre las disciplinas.
		</div>
	{:else}
		<div class="row gap-4" style="margin-bottom: 24px; align-items: center; flex-wrap: wrap">
			<div style="width: 84px; height: 84px"><SealRing glyph={school.glyph} hue={school.hue} /></div>
			<div>
				<div class="eyebrow" style="margin-bottom: 6px">Escuela de magia · {artifacts.length} artefactos</div>
				<h1 class="t-arcane" style="font-size: 44px; margin: 0 0 8px; color: {school.hue}">{school.name}</h1>
				<p class="lede" style="max-width: 580px; margin: 0">{school.desc}</p>
			</div>
		</div>
		<StarSep w={200} />
		<div class="grid-cards" style="margin-top: 24px">
			{#each artifacts as a (a.id)}
				<SpellCard art={a} />
			{/each}
		</div>
	{/if}
</div>
