<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		eyebrow,
		title,
		sub,
		right
	}: { eyebrow?: string; title: string; sub?: string; right?: Snippet } = $props();
</script>

<div class="row" style="justify-content: space-between; align-items: flex-end; margin-bottom: 20px; gap: 16px; flex-wrap: wrap">
	<div>
		{#if eyebrow}<div class="eyebrow" style="margin-bottom: 8px">{eyebrow}</div>{/if}
		<h2 class="t-arcane" style="font-size: 34px; margin: 0">{title}</h2>
		{#if sub}<p class="muted" style="margin: 8px 0 0; max-width: 560px; line-height: 1.6">{sub}</p>{/if}
	</div>
	{#if right}{@render right()}{/if}
</div>
