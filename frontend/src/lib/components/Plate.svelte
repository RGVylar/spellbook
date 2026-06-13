<script lang="ts">
	import type { Artifact } from '$lib/types';

	let { art, big = false }: { art: Artifact; big?: boolean } = $props();
</script>

<div class="plate" class:big>
	<!-- Fondo: media preservada, texto o vacío -->
	{#if art.mediaUrl && art.media === 'image'}
		<img class="plate-bg" src={art.mediaUrl} alt="" aria-hidden="true" />
	{:else if art.mediaUrl && art.media === 'video'}
		<video class="plate-bg" src={art.mediaUrl} muted preload="metadata" aria-hidden="true"></video>
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
		padding: 14px 16px;
		font-family: var(--font-ui);
		font-size: 10.5px;
		line-height: 1.55;
		color: var(--gold-deep);
		opacity: 0.45;
		overflow: hidden;
		pointer-events: none;
		word-break: break-word;
		mask-image: linear-gradient(to bottom, rgba(0,0,0,0.9) 40%, transparent 100%);
		-webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,0.9) 40%, transparent 100%);
	}
</style>
