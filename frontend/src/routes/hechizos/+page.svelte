<script lang="ts">
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import Viz from '$lib/components/Viz.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { player } from '$lib/stores/player.svelte';
	import type { Artifact, Spell } from '$lib/types';

	let sel = $state(page.url.searchParams.get('id') ?? '');
	let tracks = $state<Artifact[]>([]);
	let loadingTracks = $state(false);

	$effect(() => {
		const fromUrl = page.url.searchParams.get('id');
		if (fromUrl) sel = fromUrl;
	});

	const spell = $derived(catalog.spells.find((s) => s.id === sel) ?? catalog.spells[0]);

	$effect(() => {
		const sp = spell;
		if (!sp) return;
		loadingTracks = true;
		void api
			.get<{ spell: Spell; tracks: Artifact[] }>(`/spells/${sp.id}`)
			.then((res) => (tracks = res.tracks))
			.finally(() => (loadingTracks = false));
	});

	// ── Crear hechizo ─────────────────────────────────────────
	let creating = $state(false);
	let newName = $state('');
	let newGlyph = $state('♪');
	let newHue = $state('#c9a84c');
	let newDesc = $state('');
	let createError = $state('');

	async function createSpell() {
		if (!newName.trim()) return;
		createError = '';
		try {
			const sp = await api.post<Spell>('/spells', {
				name: newName.trim(), glyph: newGlyph, hue: newHue, desc: newDesc.trim()
			});
			await catalog.load(true);
			sel = sp.id;
			creating = false;
			newName = ''; newGlyph = '♪'; newHue = '#c9a84c'; newDesc = '';
		} catch (e) {
			createError = e instanceof Error ? e.message : 'Error al crear el hechizo';
		}
	}

	// ── Borrar hechizo ────────────────────────────────────────
	let confirmDeleteSpell = $state(false);
	let deletingSpell = $state(false);

	async function deleteSpell() {
		if (!spell || deletingSpell) return;
		deletingSpell = true;
		try {
			await api.del(`/spells/${spell.id}`);
			await catalog.load(true);
			sel = catalog.spells[0]?.id ?? '';
			confirmDeleteSpell = false;
		} finally {
			deletingSpell = false;
		}
	}

	// ── Añadir pista ──────────────────────────────────────────
	let addingTrack = $state(false);
	let trackQuery = $state('');
	let addError = $state('');

	const playableArtifacts = $derived(
		catalog.artifacts
			.filter((a) => (a.media === 'audio' || a.media === 'video') && a.status === 'sellado')
			.filter((a) => !tracks.some((t) => t.id === a.id))
			.filter((a) => !trackQuery || a.title.toLowerCase().includes(trackQuery.toLowerCase()))
			.slice(0, 8)
	);

	async function addTrack(artId: string) {
		if (!spell) return;
		addError = '';
		try {
			const updated = await api.post<Spell>(`/spells/${spell.id}/tracks/${artId}`);
			catalog.spells = catalog.spells.map((s) => s.id === updated.id ? updated : s);
			const art = catalog.artifacts.find((a) => a.id === artId);
			if (art) tracks = [...tracks, art];
			trackQuery = '';
		} catch (e) {
			addError = e instanceof Error ? e.message : 'Error al añadir la pista';
		}
	}

	// ── Quitar pista ──────────────────────────────────────────
	async function removeTrack(artId: string) {
		if (!spell) return;
		try {
			const updated = await api.del<Spell>(`/spells/${spell.id}/tracks/${artId}`);
			catalog.spells = catalog.spells.map((s) => s.id === (updated as Spell).id ? (updated as Spell) : s);
			tracks = tracks.filter((t) => t.id !== artId);
		} catch { /* silencioso */ }
	}
</script>

<svelte:head><title>Hechizos · SPELLBOOK</title></svelte:head>

<div class="canvas">
	<SectionHead
		eyebrow="Cánticos sellados"
		title="Hechizos"
		sub="Playlists del grimorio. Invoca un hechizo y resonará en el dock arcano."
	/>
	<div style="display: grid; grid-template-columns: 300px 1fr; gap: 30px; align-items: start" class="spells-grid">
		<!-- Lista de hechizos -->
		<div style="display: flex; flex-direction: column; gap: 10px">
			{#each catalog.spells as s (s.id)}
				<div
					class="card flat cursor-star"
					role="button"
					tabindex="0"
					onclick={() => (sel = s.id)}
					onkeydown={(e) => e.key === 'Enter' && (sel = s.id)}
					style="padding: 14px 16px; display: flex; gap: 14px; align-items: center; cursor: pointer; border-color: {s.id === spell?.id ? 'var(--glass-border-hi)' : 'var(--glass-border)'}; box-shadow: {s.id === spell?.id ? 'var(--glow-amber)' : 'var(--inner-vellum)'}"
				>
					<div
						style="width: 48px; height: 48px; border-radius: 10px; display: grid; place-items: center; flex: 0 0 auto; font-family: var(--font-arcane); font-size: 24px; color: {s.hue}; background: radial-gradient(circle at 38% 32%, {s.hue}26, rgba(0,0,0,.3)); border: 1px solid var(--glass-border)"
					>
						{s.glyph}
					</div>
					<div style="min-width: 0; flex: 1">
						<div class="card-title" style="margin: 0 0 2px; font-size: 14px">{s.name}</div>
						<div class="muted" style="font-size: 11.5px">{s.tracks.length} pistas</div>
					</div>
				</div>
			{/each}

			{#if auth.isModerator}
				{#if creating}
					<div class="glass" style="border-radius: var(--r-md); padding: 14px 16px">
						<div class="field" style="margin-bottom: 10px">
							<label for="sp-name" style="font-size: 12px">Nombre</label>
							<input id="sp-name" class="input" placeholder="Nombre del hechizo" bind:value={newName} />
						</div>
						<div class="row gap-2" style="margin-bottom: 10px">
							<div class="field" style="flex: 1; margin: 0">
								<label for="sp-glyph" style="font-size: 12px">Glyph</label>
								<input id="sp-glyph" class="input" maxlength="2" bind:value={newGlyph} style="font-size: 22px; text-align: center" />
							</div>
							<div class="field" style="flex: 1; margin: 0">
								<label for="sp-hue" style="font-size: 12px">Color</label>
								<input id="sp-hue" type="color" bind:value={newHue} style="width: 100%; height: 38px; border-radius: var(--r-sm); border: 1px solid var(--glass-border); background: transparent; cursor: pointer; padding: 2px 4px" />
							</div>
						</div>
						<div class="field" style="margin-bottom: 10px">
							<label for="sp-desc" style="font-size: 12px">Descripción</label>
							<input id="sp-desc" class="input" placeholder="Breve descripción…" bind:value={newDesc} />
						</div>
						{#if createError}<p style="color: var(--ember); font-size: 12px; margin: 0 0 8px">{createError}</p>{/if}
						<div class="row gap-2">
							<button class="btn cursor-star" style="flex: 1" onclick={createSpell} disabled={!newName.trim()}>
								<Icon name="sparkle" s={14} /> Sellar
							</button>
							<button class="btn ghost cursor-star" style="flex: 1" onclick={() => { creating = false; createError = ''; }}>
								Cancelar
							</button>
						</div>
					</div>
				{:else}
					<button class="btn cursor-star" style="width: 100%" onclick={() => (creating = true)}>
						<Icon name="invoke" s={15} /> Nuevo hechizo
					</button>
				{/if}
			{/if}
		</div>

		<!-- Detalle del hechizo -->
		{#if spell}
			<div class="glass" style="border-radius: var(--r-xl); overflow: hidden">
				<!-- Cabecera -->
				<div style="padding: 24px 24px 18px; display: flex; gap: 20px; align-items: center; background: linear-gradient(135deg, {spell.hue}1f, transparent 70%); border-bottom: 1px solid rgba(201,168,76,.14)">
					<div
						style="width: 88px; height: 88px; border-radius: 16px; display: grid; place-items: center; flex: 0 0 auto; font-family: var(--font-arcane); font-size: 44px; color: {spell.hue}; background: radial-gradient(circle at 38% 32%, {spell.hue}33, rgba(0,0,0,.35)); border: 1px solid var(--glass-border-hi); box-shadow: var(--glow-amber)"
					>
						{spell.glyph}
					</div>
					<div style="flex: 1; min-width: 0">
						<div class="eyebrow" style="margin-bottom: 4px">Hechizo · {tracks.length} cánticos</div>
						<h2 class="t-arcane" style="font-size: 28px; margin: 0 0 4px; color: {spell.hue}">{spell.name}</h2>
						<p class="muted" style="margin: 0; font-size: 13px; line-height: 1.4">{spell.desc}</p>
					</div>
					<div class="row gap-2" style="align-self: flex-start">
						<button
							class="btn cursor-star"
							style="padding: 7px 14px; gap: 6px"
							onclick={() => player.play(tracks[0], tracks)}
							disabled={tracks.length === 0}
						>
							<Icon name="play" s={15} /> Invocar todo
						</button>
						{#if auth.isArchimago}
							{#if confirmDeleteSpell}
								<button class="btn cursor-star" style="border-color: var(--ember); color: var(--ember)" onclick={deleteSpell} disabled={deletingSpell}>
									{deletingSpell ? '…' : '¿Borrar?'}
								</button>
								<button class="btn ghost cursor-star" onclick={() => (confirmDeleteSpell = false)}>
									<Icon name="close" s={14} />
								</button>
							{:else}
								<button class="btn ghost cursor-star" style="padding: 7px 10px" onclick={() => (confirmDeleteSpell = true)} title="Borrar hechizo">
									<Icon name="close" s={16} />
								</button>
							{/if}
						{/if}
					</div>
				</div>

				<!-- Pistas -->
				<div style="padding: 8px 12px 16px">
					{#if loadingTracks}
						<p class="t-arcane" style="color: var(--gold); padding: 20px; text-align: center">El oráculo medita…</p>
					{/if}
					{#each tracks as t, i (t.id)}
						{@const isCur = player.current?.id === t.id}
						{@const sc = catalog.school(t.school)}
						<div
							class="lrow cursor-star"
							role="button"
							tabindex="0"
							style="background: transparent; border: 1px solid transparent; border-bottom: 1px dashed rgba(201,168,76,.10); border-radius: 0"
							onclick={() => player.play(t, tracks)}
							onkeydown={(e) => e.key === 'Enter' && player.play(t, tracks)}
						>
							<span class="muted" style="width: 22px; text-align: center; font-variant-numeric: tabular-nums; flex: 0 0 auto">
								{isCur && player.playing ? '♪' : i + 1}
							</span>
							<div class="lglyph" style="width: 40px; height: 40px; flex: 0 0 auto">{t.glyph}</div>
							<div style="flex: 1; min-width: 0">
								<div class="card-title" style="margin: 0 0 2px; font-size: 14px; color: {isCur ? 'var(--gold-bright)' : 'var(--parchment)'}">
									{t.title}
								</div>
								<div class="card-meta">
									<span style="color: {sc?.hue}">{sc?.glyph} {sc?.name}</span>
									<span class="dot"></span><span>{t.era}</span>
								</div>
							</div>
							{#if isCur && player.playing}
								<Viz active bars={10} />
							{:else}
								<Icon name="play" s={16} style="color: var(--muted)" />
							{/if}
							<a
								class="btn ghost cursor-star"
								style="padding: 5px 8px"
								href="/artefacto/{t.id}"
								onclick={(e) => e.stopPropagation()}
								aria-label="Ver artefacto"
							>
								<Icon name="chevron" s={15} />
							</a>
							{#if auth.isModerator}
								<button
									class="btn ghost cursor-star"
									style="padding: 5px 8px; color: var(--muted)"
									onclick={(e) => { e.stopPropagation(); void removeTrack(t.id); }}
									title="Quitar pista"
								>
									<Icon name="close" s={14} />
								</button>
							{/if}
						</div>
					{/each}

					{#if tracks.length === 0 && !loadingTracks}
						<p class="muted" style="text-align: center; padding: 28px; font-size: 13px">Este hechizo no tiene pistas aún.</p>
					{/if}

					<!-- Añadir pistas (mago+) -->
					{#if auth.isModerator}
						<div style="margin-top: 14px; border-top: 1px dashed rgba(201,168,76,.14); padding-top: 14px">
							{#if addingTrack}
								<input
									class="input"
									placeholder="Buscar artefacto de audio o vídeo…"
									bind:value={trackQuery}
									style="margin-bottom: 8px"
									autofocus
								/>
								{#each playableArtifacts as a (a.id)}
									{@const sc = catalog.school(a.school)}
									<div
										class="lrow cursor-star"
										role="button"
										tabindex="0"
										style="border-radius: var(--r-sm); border: 1px solid transparent; padding: 8px"
										onclick={() => { void addTrack(a.id); addingTrack = false; }}
										onkeydown={(e) => e.key === 'Enter' && addTrack(a.id)}
									>
										<div class="lglyph" style="width: 36px; height: 36px; font-size: 16px; flex: 0 0 auto">{a.glyph}</div>
										<div style="flex: 1; min-width: 0">
											<div style="font-size: 13.5px; font-weight: 600">{a.title}</div>
											<div class="muted" style="font-size: 11px">{sc?.name} · {a.era} · {a.media}</div>
										</div>
										<Icon name="invoke" s={15} style="color: var(--muted)" />
									</div>
								{/each}
								{#if addError}<p style="color: var(--ember); font-size: 12px; margin: 6px 0 0">{addError}</p>{/if}
								<button class="btn ghost cursor-star" style="margin-top: 8px; width: 100%" onclick={() => { addingTrack = false; trackQuery = ''; }}>
									Cancelar
								</button>
							{:else}
								<button class="btn cursor-star" style="width: 100%; font-size: 12.5px" onclick={() => (addingTrack = true)}>
									<Icon name="invoke" s={14} /> Añadir pista
								</button>
							{/if}
						</div>
					{/if}
				</div>
			</div>
		{:else}
			<div class="glass" style="border-radius: var(--r-xl); padding: 48px; text-align: center; color: var(--muted)">
				{auth.isModerator ? 'Crea tu primer hechizo con el botón de la izquierda.' : 'Aún no hay hechizos sellados en el grimorio.'}
			</div>
		{/if}
	</div>
</div>
