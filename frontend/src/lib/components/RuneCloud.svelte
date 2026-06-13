<script lang="ts">
	let {
		runes,
		active = [],
		onToggle
	}: { runes: string[]; active?: string[]; onToggle?: (rune: string) => void } = $props();
</script>

<div class="runecloud">
	{#each runes as r (r)}
		<button type="button" class="rune cursor-star" class:on={active.includes(r)} onclick={() => onToggle?.(r)}>
			{r}
		</button>
	{/each}
</div>

<style>
	button.rune {
		font-family: var(--font-ui);
	}
</style>
