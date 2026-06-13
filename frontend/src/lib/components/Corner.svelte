<script lang="ts">
	let { cls }: { cls: 'tl' | 'tr' | 'bl' | 'br' } = $props();
</script>

<svg class="corner {cls}" viewBox="0 0 26 26" fill="none" aria-hidden="true">
	<path d="M2 13C2 7 7 2 13 2" stroke="currentColor" stroke-width="1" />
	<path d="M2 9C2 5 5 2 9 2" stroke="currentColor" stroke-width=".8" opacity=".7" />
	<circle cx="3" cy="3" r="1.4" fill="currentColor" />
	<path d="M2 18c2 0 3-1 3-3M18 2c0 2-1 3-3 3" stroke="currentColor" stroke-width=".8" opacity=".6" />
</svg>
