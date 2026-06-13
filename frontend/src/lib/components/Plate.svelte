<script lang="ts">
	import type { Artifact } from '$lib/types';

	let { art, big = false }: { art: Artifact; big?: boolean } = $props();

	function ytThumbnail(url: string): string | null {
		const m = url.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/);
		return m ? `https://img.youtube.com/vi/${m[1]}/hqdefault.jpg` : null;
	}

	const thumbSrc = $derived(
		art.thumbnailUrl ??
		(art.sourceUrl ? ytThumbnail(art.sourceUrl) : null) ??
		(art.media === 'image' ? (art.mediaUrl ?? null) : null)
	);
</script>

<div class="plate" class:big>
	{#if thumbSrc}
		<img class="plate-bg" src={thumbSrc} alt="" aria-hidden="true" />
	{:else if art.media === 'text' && art.desc}
		<div class="plate-text" aria-hidden="true">{art.desc}</div>
	{/if}

	<div class="frame"></div>
	<span class="glyph">{art.glyph}</span>
	<span class="seal-mark">{art.era}</span>
</div>

<style>
	.plate-bg {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		opacity: 0.28;
		pointer-events: none;
	}

	.plate-text {
		position: absolute;
		inset: 0;
		padding: 12px 14px;
		font-family: var(--font-arcane);
		font-size: 18px;
		line-height: 1.5;
		color: var(--gold-deep);
		opacity: 0.5;
		overflow: hidden;
		pointer-events: none;
		word-break: break-word;
		mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 30%, transparent 80%);
		-webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 30%, transparent 80%);
	}
</style>
