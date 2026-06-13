<script lang="ts">
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Corner from '$lib/components/Corner.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import Plate from '$lib/components/Plate.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import type { Artifact } from '$lib/types';

	let { art }: { art: Artifact } = $props();

	const school = $derived(catalog.school(art.school));
</script>

<a class="card cursor-star" href="/artefacto/{art.id}">
	<Corner cls="tl" /><Corner cls="tr" /><Corner cls="bl" /><Corner cls="br" />
	<Plate {art} />
	<div class="card-body">
		<div class="row" style="justify-content: space-between; margin-bottom: 8px">
			<ArtifactBadge type={art.type} />
			<span class="muted" style="font-size: 11px; display: flex; align-items: center; gap: 5px">
				<Icon name="link" s={13} />
				{art.links.length}
			</span>
		</div>
		<h3 class="card-title">{art.title}</h3>
		<div class="card-meta">
			<span style="color: {school?.hue}">{school?.glyph} {school?.name}</span>
			<span class="dot"></span><span>{art.era}</span>
		</div>
	</div>
</a>

<style>
	a.card {
		display: block;
		text-decoration: none;
		color: inherit;
	}
</style>
