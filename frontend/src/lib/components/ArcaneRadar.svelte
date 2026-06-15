<script lang="ts">
	import type { ArcaneStats } from '$lib/types';

	let { stats }: { stats: ArcaneStats } = $props();

	const CX = 100, CY = 108, R = 72;

	// Vértice en el eje dado (0=top/Resonancia, 1=BR/Estirpe, 2=BL/Estudio)
	function vertex(axis: number, scale: number = 1) {
		const angle = axis * (2 * Math.PI / 3); // 0, 120°, 240° clockwise desde arriba
		return {
			x: CX + R * scale * Math.sin(angle),
			y: CY - R * scale * Math.cos(angle),
		};
	}

	function trianglePath(scale: number) {
		const [a, b, c] = [0, 1, 2].map((i) => vertex(i, scale));
		return `M ${a.x} ${a.y} L ${b.x} ${b.y} L ${c.x} ${c.y} Z`;
	}

	// Normaliza cada eje contra el máximo de los 3 para que la forma sea legible
	// independientemente de la escala absoluta. Los valores reales se muestran en etiquetas.
	const maxVal = $derived(Math.max(stats.resonancia, stats.estudio, stats.estirpe, 1));
	const sr = $derived(stats.resonancia / maxVal);
	const se = $derived(stats.estirpe / maxVal);
	const st = $derived(stats.estudio / maxVal);

	const poder = $derived(Math.round(stats.resonancia + stats.estudio + stats.estirpe));

	const dataPath = $derived(() => {
		const r = vertex(0, sr);
		const e = vertex(1, se);
		const t = vertex(2, st);
		return `M ${r.x} ${r.y} L ${e.x} ${e.y} L ${t.x} ${t.y} Z`;
	});

	const GRID_LEVELS = [0.2, 0.4, 0.6, 0.8, 1.0];
	const LABELS = [
		{ axis: 0, label: 'Resonancia', dy: -12, anchor: 'middle' },
		{ axis: 1, label: 'Estirpe',    dy: 18,  anchor: 'middle' },
		{ axis: 2, label: 'Estudio',    dy: 18,  anchor: 'middle' },
	];
</script>

<div class="radar-wrap">
	<svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg" aria-label="Perfil arcano">
		<defs>
			<filter id="glow-gold">
				<feGaussianBlur stdDeviation="2.5" result="blur" />
				<feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
			</filter>
		</defs>

		<!-- Cuadrícula de fondo -->
		{#each GRID_LEVELS as scale}
			<path
				d={trianglePath(scale)}
				fill="none"
				stroke="rgba(201,168,76,{scale === 1 ? 0.28 : 0.12})"
				stroke-width={scale === 1 ? 1.2 : 0.7}
			/>
		{/each}

		<!-- Ejes -->
		{#each [0, 1, 2] as axis}
			{@const tip = vertex(axis, 1)}
			<line
				x1={CX} y1={CY}
				x2={tip.x} y2={tip.y}
				stroke="rgba(201,168,76,0.18)"
				stroke-width="0.8"
			/>
		{/each}

		<!-- Relleno de datos -->
		<path
			d={dataPath()}
			fill="rgba(107,63,160,0.35)"
			stroke="rgba(155,114,203,0.7)"
			stroke-width="1.5"
			stroke-linejoin="round"
			filter="url(#glow-gold)"
		/>

		<!-- Puntos de datos -->
		{#each [[0, sr], [1, se], [2, st]] as [axis, scale]}
			{@const pt = vertex(axis, scale)}
			<circle cx={pt.x} cy={pt.y} r="3.5" fill="var(--gold-bright)" filter="url(#glow-gold)" />
		{/each}

		<!-- Etiquetas -->
		{#each LABELS as { axis, label, dy, anchor }}
			{@const tip = vertex(axis, 1)}
			<text
				x={tip.x}
				y={tip.y + dy}
				text-anchor={anchor}
				font-family="var(--font-ui)"
				font-size="9"
				font-weight="600"
				letter-spacing="0.12em"
				text-transform="uppercase"
				fill="var(--gold)"
				opacity="0.85"
			>{label.toUpperCase()}</text>
		{/each}

		<!-- Valores numéricos en los puntos (solo si > 2 para no saturar el centro) -->
		{#each [[0, sr, stats.resonancia], [1, se, stats.estirpe], [2, st, stats.estudio]] as [axis, scale, val]}
			{#if val > 2}
				{@const pt = vertex(axis, scale)}
				<text
					x={pt.x}
					y={pt.y - 6}
					text-anchor="middle"
					font-family="var(--font-ui)"
					font-size="7.5"
					fill="var(--gold-bright)"
					opacity="0.9"
				>{Math.round(val)}</text>
			{/if}
		{/each}

		<!-- Separador -->
		<line x1="20" y1="212" x2="180" y2="212" stroke="rgba(201,168,76,0.15)" stroke-width="0.8" />

		<!-- Poder Total -->
		<text x="100" y="225" text-anchor="middle" font-family="var(--font-ui)" font-size="8" font-weight="600" letter-spacing="0.18em" fill="var(--muted)">PODER TOTAL</text>
		<text x="100" y="238" text-anchor="middle" font-family="var(--font-display)" font-size="16" font-weight="700" fill="var(--gold-bright)" filter="url(#glow-gold)">{poder}</text>
	</svg>
</div>

<style>
	.radar-wrap {
		width: 100%;
		max-width: 200px;
		margin: 0 auto;
	}
</style>
