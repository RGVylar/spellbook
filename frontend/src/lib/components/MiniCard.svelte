<script lang="ts">
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Corner from '$lib/components/Corner.svelte';
	import Plate from '$lib/components/Plate.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import type { Artifact } from '$lib/types';

	let { art }: { art: Artifact } = $props();

	const school = $derived(catalog.school(art.school));
</script>

<a class="card mini cursor-star" href="/artefacto/{art.id}">
	<Corner cls="tl" /><Corner cls="tr" /><Corner cls="bl" /><Corner cls="br" />
	<Plate {art} compact />
	<div class="mini-body">
		<div style="margin-bottom: 5px"><ArtifactBadge type={art.type} size={11} /></div>
		<h3 class="mini-title">{art.title}</h3>
		<div class="mini-meta">
			<span style="color: {school?.hue ?? 'var(--gold)'}">{school?.glyph}</span>
			<span>{art.era}</span>
		</div>
	</div>
</a>

<style>
	a.card.mini {
		display: block;
		text-decoration: none;
		color: inherit;
	}
	.mini-body {
		padding: 10px 12px 12px;
	}
	.mini-title {
		font-family: var(--font-ui);
		font-weight: 650;
		font-size: 13px;
		letter-spacing: .01em;
		color: var(--parchment);
		margin: 0 0 4px;
		line-height: 1.3;
		overflow: hidden;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}
	.mini-meta {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 11px;
		color: var(--muted);
	}
</style>
