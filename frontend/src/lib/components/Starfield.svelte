<script lang="ts">
	const stars = Array.from({ length: 46 }, (_, i) => ({
		id: i,
		x: Math.random() * 100,
		y: Math.random() * 100,
		r: Math.random() * 1.3 + 0.3,
		d: Math.random() * 3
	}));
</script>

<svg class="ostars" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
	{#each stars as s (s.id)}
		<circle cx={s.x} cy={s.y} r={s.r} fill="var(--gold-bright)" opacity="0">
			<animate attributeName="opacity" values="0;.7;0" dur="{2 + s.d}s" repeatCount="indefinite" begin="{s.d}s" />
		</circle>
	{/each}
</svg>
