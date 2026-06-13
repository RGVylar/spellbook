<script lang="ts">
	import { goto } from '$app/navigation';
	import { catalog } from '$lib/stores/catalog.svelte';
	import type { Artifact } from '$lib/types';

	let { art }: { art: Artifact } = $props();

	const W = 560;
	const H = 360;
	const cx = W / 2;
	const cy = H / 2;
	const RAD = 128;
	const uid = $props.id();

	let hover = $state<number | null>(null);

	const nodes = $derived((() => {
		const outgoing = art.links
			.map((id) => catalog.findArt(id))
			.filter((a): a is Artifact => Boolean(a));
		const incoming = catalog.artifacts.filter(
			(a) => a.id !== art.id && a.links.includes(art.id) && !art.links.includes(a.id)
		);
		const all = [...outgoing, ...incoming];
		return all.map((a, i) => {
			const ang = (i / all.length) * Math.PI * 2 - Math.PI / 2;
			return { a, x: cx + Math.cos(ang) * RAD, y: cy + Math.sin(ang) * RAD, reverse: i >= outgoing.length };
		});
	})());
</script>

<div class="graph-wrap" style="aspect-ratio: {W}/{H}">
	<svg viewBox="0 0 {W} {H}" width="100%" height="100%">
		<defs>
			<radialGradient id="gcen-{uid}">
				<stop offset="0" stop-color="#E6C868" />
				<stop offset="1" stop-color="#8A6D2A" />
			</radialGradient>
		</defs>
		<!-- anillo de invocación -->
		<circle
			{cx}
			{cy}
			r={RAD}
			fill="none"
			stroke="rgba(201,168,76,.16)"
			stroke-dasharray="3 7"
			class="spin-slow"
			style="transform-origin: {cx}px {cy}px"
		/>
		<circle {cx} {cy} r="150" fill="none" stroke="rgba(201,168,76,.08)" />
		{#each nodes as n, i (n.a.id)}
			<line
				x1={cx}
				y1={cy}
				x2={n.x}
				y2={n.y}
				stroke={hover === i ? 'var(--gold-bright)' : n.reverse ? 'rgba(160,120,201,.35)' : 'rgba(201,168,76,.28)'}
				stroke-width={hover === i ? 1.6 : 1}
				stroke-dasharray={n.reverse ? '4 4' : undefined}
			/>
		{/each}
		{#each nodes as n, i (n.a.id)}
			<g
				class="graph-node cursor-star"
				role="link"
				tabindex="0"
				onclick={() => goto(`/artefacto/${n.a.id}`)}
				onkeydown={(e) => e.key === 'Enter' && goto(`/artefacto/${n.a.id}`)}
				onmouseenter={() => (hover = i)}
				onmouseleave={() => (hover = null)}
			>
				<circle cx={n.x} cy={n.y} r={hover === i ? 26 : 22} fill="#120f17" stroke="var(--glass-border-hi)" />
				<text x={n.x} y={n.y + 7} text-anchor="middle" font-size="20" fill="var(--gold-bright)" font-family="var(--font-arcane)">
					{n.a.glyph}
				</text>
				<text x={n.x} y={n.y + 44} text-anchor="middle" class="gnode-label">
					{n.a.title.length > 18 ? n.a.title.slice(0, 17) + '…' : n.a.title}
				</text>
			</g>
		{/each}
		<!-- centro -->
		<circle {cx} {cy} r="34" fill="url(#gcen-{uid})" stroke="var(--gold-bright)" stroke-width="1.5" />
		<text x={cx} y={cy + 9} text-anchor="middle" font-size="26" fill="#1c1505" class="gnode-center">{art.glyph}</text>
	</svg>
</div>
