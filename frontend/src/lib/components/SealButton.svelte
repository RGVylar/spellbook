<script lang="ts">
	import Icon from '$lib/components/Icon.svelte';
	import type { Snippet } from 'svelte';

	let {
		onclick,
		sealed = false,
		disabled = false,
		children
	}: { onclick?: () => void; sealed?: boolean; disabled?: boolean; children: Snippet } = $props();
</script>

<button type="button" class="seal-btn cursor-star" class:sealed {disabled} {onclick}>
	<span class="shine"></span>
	<Icon name="seal" s={18} />
	{@render children()}
</button>

<style>
	button:disabled {
		opacity: 0.5;
		pointer-events: none;
	}
</style>
