<script lang="ts">
	let { w = 220 }: { w?: number } = $props();
	const uid = $props.id();
</script>

<svg width={w} height="22" viewBox="0 0 220 22" fill="none" style="opacity: calc(.8 * var(--ornament, 1))" aria-hidden="true">
	<path d="M0 11h78M142 11h78" stroke="url(#sg-{uid})" stroke-width="1" />
	<circle cx="58" cy="11" r="1.3" fill="var(--gold)" />
	<circle cx="162" cy="11" r="1.3" fill="var(--gold)" />
	<path d="M110 2l1.7 5.5L117 9l-5 1.7L110 16l-1.7-5.3L103 9l5.3-1.5z" fill="var(--gold-bright)" />
	<circle cx="92" cy="11" r="1" fill="var(--gold-deep)" />
	<circle cx="128" cy="11" r="1" fill="var(--gold-deep)" />
	<defs>
		<linearGradient id="sg-{uid}" x1="0" x2="220" gradientUnits="userSpaceOnUse">
			<stop stop-color="var(--gold)" stop-opacity="0" />
			<stop offset=".5" stop-color="var(--gold)" stop-opacity=".6" />
			<stop offset="1" stop-color="var(--gold)" stop-opacity="0" />
		</linearGradient>
	</defs>
</svg>
