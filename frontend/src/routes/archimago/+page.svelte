<script lang="ts">
	import { api } from '$lib/api';
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';

	type ArtifactMini = { id: string; title: string; school: string; views: number; likes: number };
	type SchoolCount = { id: string; name: string; glyph: string; hue: string; count: number };
	type AdminStats = {
		total: number;
		sellado: number;
		pendiente: number;
		rechazado: number;
		byType: Record<string, number>;
		byMedia: Record<string, number>;
		bySchool: SchoolCount[];
		totalUsers: number;
		byRole: Record<string, number>;
		topViews: ArtifactMini[];
		topLikes: ArtifactMini[];
		totalNotes: number;
		totalReactions: number;
		totalConnections: number;
	};

	let stats = $state<AdminStats | null>(null);
	let loading = $state(true);
	let error = $state('');

	$effect(() => {
		if (!auth.loaded) return;
		if (!auth.isArchimago) { loading = false; return; }
		void api.get<AdminStats>('/admin/stats')
			.then((s) => (stats = s))
			.catch((e) => (error = e instanceof Error ? e.message : 'Error'))
			.finally(() => (loading = false));
	});

	const TYPE_LABELS: Record<string, string> = {
		pergamino: 'Pergamino', reliquia: 'Reliquia', hechizo: 'Hechizo', 'visión': 'Visión'
	};
	const MEDIA_LABELS: Record<string, string> = {
		text: 'Texto', image: 'Imagen', audio: 'Audio', video: 'Vídeo'
	};
	const MEDIA_GLYPH: Record<string, string> = {
		text: '☽', image: '✶', audio: '♫', video: '☥'
	};
	const ROLE_LABELS: Record<string, string> = {
		archimago: '⚷ Archimago', mago: '⁂ Mago', aprendiz: '✦ Aprendiz'
	};

	function maxVal(obj: Record<string, number>): number {
		return Math.max(1, ...Object.values(obj));
	}
</script>

<svelte:head><title>Panel del Archimago · SPELLBOOK</title></svelte:head>

<div class="canvas" style="max-width: 1100px">
	<SectionHead
		eyebrow="⚷ Acceso restringido"
		title="Panel del Archimago"
		sub="Visión completa del grimorio. Métricas, estado de la bóveda y actividad de los magos."
	/>

	{#if !auth.isArchimago}
		<div class="glass locked-panel">
			<Icon name="crown" s={32} style="color: var(--gold-bright); margin-bottom: 12px" />
			<p>Solo el <span class="archimago">Archimago</span> puede contemplar estos secretos.</p>
		</div>
	{:else if loading}
		<p class="t-arcane loading-text">El oráculo consulta los registros…</p>
	{:else if error}
		<div class="glass" style="padding: 32px; color: var(--ember); border-radius: var(--r-lg)">Error: {error}</div>
	{:else if stats}
		<!-- KPIs principales -->
		<div class="kpi-grid">
			<div class="kpi-card glass">
				<div class="kpi-value">{stats.sellado}</div>
				<div class="kpi-label">Artefactos sellados</div>
				<div class="kpi-sub">de {stats.total} totales</div>
			</div>
			<div class="kpi-card glass kpi-warn">
				<div class="kpi-value">{stats.pendiente}</div>
				<div class="kpi-label">Pendientes</div>
				<div class="kpi-sub">aguardando juicio</div>
			</div>
			<div class="kpi-card glass">
				<div class="kpi-value">{stats.rechazado}</div>
				<div class="kpi-label">Rechazados</div>
				<div class="kpi-sub">por el cónclave</div>
			</div>
			<div class="kpi-card glass">
				<div class="kpi-value">{stats.totalUsers}</div>
				<div class="kpi-label">Magos inscritos</div>
				<div class="kpi-sub">{stats.byRole['archimago'] ?? 0} archimago · {stats.byRole['mago'] ?? 0} magos · {stats.byRole['aprendiz'] ?? 0} aprendices</div>
			</div>
			<div class="kpi-card glass">
				<div class="kpi-value">{stats.totalConnections}</div>
				<div class="kpi-label">Conexiones</div>
				<div class="kpi-sub">entre artefactos sellados</div>
			</div>
			<div class="kpi-card glass">
				<div class="kpi-value">{stats.totalNotes}</div>
				<div class="kpi-label">Anotaciones</div>
				<div class="kpi-sub">{stats.totalReactions} reacciones</div>
			</div>
		</div>

		<div class="two-col">
			<!-- Por tipo -->
			<div class="stat-block glass">
				<div class="stat-block-title">Por naturaleza</div>
				{#each Object.entries(TYPE_LABELS) as [key, label]}
					{@const val = stats.byType[key] ?? 0}
					<div class="bar-row">
						<span class="bar-label">{label}</span>
						<div class="bar-track">
							<div class="bar-fill" style="width: {(val / maxVal(stats.byType)) * 100}%"></div>
						</div>
						<span class="bar-count">{val}</span>
					</div>
				{/each}
			</div>

			<!-- Por media -->
			<div class="stat-block glass">
				<div class="stat-block-title">Por soporte</div>
				{#each Object.entries(MEDIA_LABELS) as [key, label]}
					{@const val = stats.byMedia[key] ?? 0}
					<div class="bar-row">
						<span class="bar-label">{MEDIA_GLYPH[key]} {label}</span>
						<div class="bar-track">
							<div class="bar-fill" style="width: {(val / maxVal(stats.byMedia)) * 100}%"></div>
						</div>
						<span class="bar-count">{val}</span>
					</div>
				{/each}
			</div>
		</div>

		<!-- Por escuela -->
		<div class="stat-block glass" style="margin-bottom: 24px">
			<div class="stat-block-title">Por escuela de magia</div>
			<div class="school-bars">
				{#each stats.bySchool as s}
					{@const pct = stats.sellado > 0 ? (s.count / stats.sellado) * 100 : 0}
					<div class="bar-row">
						<span class="bar-label" style="color: {s.hue}">{s.glyph} {s.name}</span>
						<div class="bar-track">
							<div class="bar-fill" style="width: {pct}%; background: {s.hue}; opacity: 0.75"></div>
						</div>
						<span class="bar-count">{s.count}</span>
					</div>
				{/each}
			</div>
		</div>

		<div class="two-col">
			<!-- Top por vistas -->
			<div class="stat-block glass">
				<div class="stat-block-title">Más contemplados</div>
				{#each stats.topViews as a, i}
					{@const school = catalog.school(a.school)}
					<a class="top-row cursor-star" href="/artefacto/{a.id}">
						<span class="top-rank">{i + 1}</span>
						<span class="top-glyph" style="color: {school?.hue}">{school?.glyph}</span>
						<span class="top-title">{a.title}</span>
						<span class="top-stat"><Icon name="eye" s={12} /> {a.views}</span>
					</a>
				{/each}
			</div>

			<!-- Top por likes -->
			<div class="stat-block glass">
				<div class="stat-block-title">Más venerados</div>
				{#each stats.topLikes as a, i}
					{@const school = catalog.school(a.school)}
					<a class="top-row cursor-star" href="/artefacto/{a.id}">
						<span class="top-rank">{i + 1}</span>
						<span class="top-glyph" style="color: {school?.hue}">{school?.glyph}</span>
						<span class="top-title">{a.title}</span>
						<span class="top-stat"><Icon name="thumbup" s={12} /> {a.likes}</span>
					</a>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.locked-panel {
		padding: 60px;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		border-radius: var(--r-lg);
		color: var(--muted);
		font-size: 14px;
	}

	.loading-text {
		font-size: 22px;
		color: var(--gold);
		text-align: center;
		padding: 60px 0;
	}

	.kpi-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
		margin-bottom: 24px;
	}

	.kpi-card {
		padding: 20px 22px;
		border-radius: var(--r-lg);
	}

	.kpi-warn {
		border-color: rgba(201, 168, 76, 0.5) !important;
	}

	.kpi-value {
		font-family: var(--font-arcane, serif);
		font-size: 36px;
		color: var(--gold-bright);
		line-height: 1;
		margin-bottom: 6px;
	}

	.kpi-label {
		font-size: 12px;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--parchment-2);
		margin-bottom: 4px;
	}

	.kpi-sub {
		font-size: 11px;
		color: var(--muted);
	}

	.two-col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16px;
		margin-bottom: 24px;
	}

	.stat-block {
		padding: 18px 20px;
		border-radius: var(--r-lg);
	}

	.stat-block-title {
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
		margin-bottom: 14px;
	}

	.bar-row {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 9px;
	}

	.bar-label {
		font-size: 12px;
		color: var(--parchment-2);
		flex: 0 0 110px;
		white-space: nowrap;
	}

	.bar-track {
		flex: 1;
		height: 6px;
		border-radius: 3px;
		background: rgba(255, 255, 255, 0.07);
		overflow: hidden;
	}

	.bar-fill {
		height: 100%;
		border-radius: 3px;
		background: linear-gradient(90deg, var(--gold-deep), var(--gold-bright));
		transition: width 0.4s ease;
	}

	.bar-count {
		font-size: 12px;
		color: var(--muted);
		flex: 0 0 28px;
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	.school-bars .bar-label {
		flex: 0 0 140px;
	}

	.top-row {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 7px 0;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		text-decoration: none;
		transition: background 0.1s;
	}

	.top-row:last-child { border-bottom: none; }
	.top-row:hover .top-title { color: var(--gold-bright); }

	.top-rank {
		font-size: 11px;
		color: var(--faint);
		flex: 0 0 16px;
		text-align: center;
		font-variant-numeric: tabular-nums;
	}

	.top-glyph { font-size: 15px; flex: 0 0 18px; }

	.top-title {
		flex: 1;
		font-size: 12.5px;
		color: var(--parchment);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		transition: color 0.1s;
	}

	.top-stat {
		font-size: 11px;
		color: var(--muted);
		display: flex;
		align-items: center;
		gap: 4px;
		flex: 0 0 auto;
	}

	@media (max-width: 860px) {
		.kpi-grid { grid-template-columns: 1fr 1fr; }
		.two-col { grid-template-columns: 1fr; }
	}

	@media (max-width: 500px) {
		.kpi-grid { grid-template-columns: 1fr; }
	}
</style>
