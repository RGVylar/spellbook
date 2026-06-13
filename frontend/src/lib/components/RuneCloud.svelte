<script lang="ts">
	let {
		runes,
		active = [],
		onToggle
	}: { runes: string[]; active?: string[]; onToggle?: (rune: string) => void } = $props();
</script>

<div class="runecloud">
	{#each runes as r (r)}
		{#if onToggle}
			<button type="button" class="rune cursor-star" class:on={active.includes(r)} onclick={() => onToggle(r)}>
				{r}
			</button>
		{:else}
			<a class="rune cursor-star" class:on={active.includes(r)} href="/explorar?rune={encodeURIComponent(r)}">
				{r}
			</a>
		{/if}
	{/each}
</div>

<style>
	button.rune, a.rune {
		font-family: var(--font-ui);
		text-decoration: none;
	}
</style>
