<script lang="ts">
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Corner from '$lib/components/Corner.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import Plate from '$lib/components/Plate.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import type { Artifact } from '$lib/types';
	import { fmtNum } from '$lib/utils';

	let { art }: { art: Artifact } = $props();

	const school = $derived(catalog.school(art.school));
</script>

<a class="card cursor-star" href="/artefacto/{art.id}">
	<Corner cls="tl" /><Corner cls="tr" /><Corner cls="bl" /><Corner cls="br" />
	<Plate {art} />
	<div class="card-body">
		<div class="row" style="justify-content: space-between; margin-bottom: 8px; gap: 4px">
			<ArtifactBadge type={art.type} />
			<div class="stats">
				<span class="stat"><Icon name="link" s={11} />{art.links.length}</span>
				<span class="sep"></span>
				<span class="stat"><Icon name="eye" s={11} />{fmtNum(art.views ?? 0)}</span>
				<span class="stat"><Icon name="thumbup" s={11} />{fmtNum(art.likes ?? 0)}</span>
				<span class="stat"><Icon name="thumbdown" s={11} />{fmtNum(art.dislikes ?? 0)}</span>
				<span class="stat"><Icon name="quill" s={11} />{fmtNum(art.noteCount ?? 0)}</span>
			</div>
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
	.stats {
		display: flex;
		align-items: center;
		gap: 5px;
		flex-shrink: 0;
	}
	.stat {
		display: flex;
		align-items: center;
		gap: 2px;
		font-size: 10px;
		color: rgba(200, 180, 140, 0.45);
		white-space: nowrap;
	}
	.sep {
		width: 1px;
		height: 9px;
		background: rgba(201, 168, 76, 0.18);
	}
</style>
