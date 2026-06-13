<script lang="ts">
	let { glyph = '✦', hue = 'var(--gold-bright)' }: { glyph?: string; hue?: string } = $props();

	const dots = Array.from({ length: 8 }, (_, i) => {
		const a = (i / 8) * Math.PI * 2;
		return { x: 42 + Math.cos(a) * 34, y: 42 + Math.sin(a) * 34 };
	});
</script>

<svg class="seal-ring" viewBox="0 0 84 84" fill="none" aria-hidden="true">
	<circle cx="42" cy="42" r="40" stroke="var(--glass-border)" stroke-width="1" />
	<circle
		cx="42"
		cy="42"
		r="34"
		stroke={hue}
		stroke-width="1.2"
		stroke-dasharray="2 5"
		opacity=".7"
		class="spin-slow"
		style="transform-origin: 42px 42px"
	/>
	<circle cx="42" cy="42" r="27" stroke={hue} stroke-width="1" opacity=".4" />
	{#each dots as d (d.x + '-' + d.y)}
		<circle cx={d.x} cy={d.y} r="1.3" fill={hue} />
	{/each}
	<text x="42" y="52" text-anchor="middle" font-size="30" fill={hue} font-family="var(--font-arcane)">{glyph}</text>
</svg>
