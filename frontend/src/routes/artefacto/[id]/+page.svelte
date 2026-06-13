<script lang="ts">
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import ArtifactBadge from '$lib/components/ArtifactBadge.svelte';
	import Corner from '$lib/components/Corner.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import Plate from '$lib/components/Plate.svelte';
	import RelicGraph from '$lib/components/RelicGraph.svelte';
	import RuneCloud from '$lib/components/RuneCloud.svelte';
	import SpellCard from '$lib/components/SpellCard.svelte';
	import Viz from '$lib/components/Viz.svelte';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { player } from '$lib/stores/player.svelte';
	import { TYPE_META, type Artifact, type Note } from '$lib/types';
	import { arcaneTime } from '$lib/utils';
	import { arcaneHtml } from '$lib/arcane-text';

	const id = $derived(page.params.id ?? '');

	let art = $state<Artifact | null>(null);
	let notes = $state<Note[]>([]);
	let variants = $state<Artifact[]>([]);
	let draft = $state('');
	let noteError = $state('');
	let loading = $state(true);

	$effect(() => {
		const artifactId = id;
		loading = true;
		art = null;
		void (async () => {
			try {
				const [a, n, v] = await Promise.all([
					api.get<Artifact>(`/artifacts/${artifactId}`),
					api.get<Note[]>(`/artifacts/${artifactId}/notes`),
					api.get<Artifact[]>(`/artifacts?variantOf=${artifactId}`)
				]);
				art = a;
				notes = n;
				variants = v;
			} catch {
				art = null;
			} finally {
				loading = false;
			}
		})();
	});

	const school = $derived(art ? catalog.school(art.school) : undefined);
	const mother = $derived(art?.variantOf ? catalog.findArt(art.variantOf) : undefined);
	const playable = $derived(art?.media === 'audio' || art?.media === 'video');
	const isCurrent = $derived(player.current?.id === art?.id);

	function ytVideoId(url: string | null | undefined): string | null {
		if (!url) return null;
		const m = url.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/);
		return m ? m[1] : null;
	}
	const ytId = $derived(ytVideoId(art?.sourceUrl));

	let deleting = $state(false);
	let confirmDelete = $state(false);
	let videoError = $state(false);
	let ingesting = $state(false);
	let ingestRetrying = $state(false);
	let ingestPollTimer: ReturnType<typeof setInterval> | null = null;

	async function retryIngest() {
		if (!art?.sourceUrl || ingestRetrying) return;
		ingestRetrying = true;
		videoError = false;
		try {
			const fd = new FormData();
			fd.append('source_url', art.sourceUrl);
			await api.postForm(`/artifacts/${art.id}/media`, fd);
			startIngestPoll(art.id);
		} catch (e) {
			console.error('retryIngest:', e);
		} finally {
			ingestRetrying = false;
		}
	}

	function startIngestPoll(artifactId: string) {
		if (ingestPollTimer) return;
		ingesting = true;
		let attempts = 0;
		const MAX_ATTEMPTS = 30; // 2 minutos
		ingestPollTimer = setInterval(async () => {
			attempts++;
			try {
				const s = await api.get<{ mediaUrl: string | null; thumbnailUrl: string | null; fileReady: boolean }>(
					`/artifacts/${artifactId}/ingest-status`
				);
				if (s.fileReady && s.mediaUrl) {
					if (art) {
						art.mediaUrl = s.mediaUrl;
						if (s.thumbnailUrl) art.thumbnailUrl = s.thumbnailUrl;
					}
					ingesting = false;
					if (ingestPollTimer) { clearInterval(ingestPollTimer); ingestPollTimer = null; }
					return;
				}
			} catch { /* sigue intentando */ }
			if (attempts >= MAX_ATTEMPTS) {
				ingesting = false;
				if (ingestPollTimer) { clearInterval(ingestPollTimer); ingestPollTimer = null; }
			}
		}, 4000);
	}

	$effect(() => {
		// Limpiar poll al salir de la página
		return () => {
			if (ingestPollTimer) { clearInterval(ingestPollTimer); ingestPollTimer = null; }
			ingesting = false;
		};
	});

	async function deleteArt() {
		if (!art || deleting) return;
		deleting = true;
		try {
			await api.del(`/artifacts/${art.id}`);
			await catalog.load(true);
			goto('/explorar');
		} catch (e) {
			deleting = false;
			confirmDelete = false;
		}
	}

	// ── Añadir a hechizo ─────────────────────────────────────
	let spellPickerOpen = $state(false);
	let addingToSpell = $state('');

	async function addToSpell(spellId: string) {
		if (!art || addingToSpell) return;
		addingToSpell = spellId;
		try {
			await api.post(`/spells/${spellId}/tracks/${art.id}`);
			await catalog.load(true);
			spellPickerOpen = false;
		} catch { /* silencioso */ } finally {
			addingToSpell = '';
		}
	}

	// ── Visitas ──────────────────────────────────────────────
	$effect(() => {
		if (art?.status === 'sellado') {
			void api.post(`/artifacts/${art.id}/view`).catch(() => {});
		}
	});

	// ── Autoplay ─────────────────────────────────────────────
	//$effect(() => {
	//	if (art?.status === 'sellado' && art.media === 'audio') {
	//		player.play(art, catalog.playable);
	//	}
	//});

	// ── Reacciones ───────────────────────────────────────────
	let reacting = $state(false);

	async function react(reaction: 'like' | 'dislike') {
		if (!art || reacting || !auth.user) return;
		reacting = true;
		// toggle: si ya tenías esa reacción, la quitas
		const next = art.userReaction === reaction ? null : reaction;
		try {
			const res = await api.post<{ likes: number; dislikes: number; userReaction: string | null }>(
				`/artifacts/${art.id}/react`,
				{ reaction: next }
			);
			art.likes = res.likes;
			art.dislikes = res.dislikes;
			art.userReaction = res.userReaction;
		} catch { /* silencioso */ } finally {
			reacting = false;
		}
	}

	async function addNote() {
		if (!art || !draft.trim()) return;
		noteError = '';
		try {
			const note = await api.post<Note>(`/artifacts/${art.id}/notes`, { text: draft.trim() });
			notes = [note, ...notes];
			draft = '';
		} catch (e) {
			noteError = e instanceof Error ? e.message : 'El pergamino rechazó la tinta';
		}
	}
</script>

<svelte:head><title>{art?.title ?? 'Artefacto'} · SPELLBOOK</title></svelte:head>

<div class="canvas" style="max-width: 1100px">
	<a class="btn ghost cursor-star" style="margin-bottom: 18px; padding: 6px 10px; text-decoration: none" href="/explorar">
		<Icon name="chevron" s={16} style="transform: rotate(180deg)" /> El Grimorio
	</a>

	{#if loading}
		<p class="t-arcane" style="font-size: 22px; color: var(--gold); text-align: center; padding: 60px 0">
			Invocando artefacto…
		</p>
	{:else if !art}
		<div class="glass" style="padding: 40px; text-align: center; border-radius: var(--r-lg); color: var(--muted)">
			Ese artefacto no consta en el grimorio.
		</div>
	{:else}
		{#if art.status !== 'sellado'}
			<div
				class="glass"
				style="border-radius: var(--r-lg); padding: 14px 18px; margin-bottom: 20px; display: flex; gap: 12px; align-items: center; border-color: var(--ember)"
			>
				<Icon name="clock" s={20} style="color: var(--ember)" />
				<span style="font-size: 13.5px">
					{art.status === 'pendiente'
						? 'Propuesta pendiente del juicio del cónclave — aún no sellada en el grimorio.'
						: 'Propuesta rechazada por el cónclave.'}
				</span>
			</div>
		{/if}

		<div style="display: grid; grid-template-columns: 1.4fr 1fr; gap: 36px; align-items: start" class="art-grid">
			<!-- Columna principal -->
			<div>
				<div class="row gap-3" style="margin-bottom: 14px; flex-wrap: wrap">
					<ArtifactBadge type={art.type} />
					<a
						class="badge cursor-star"
						href="/escuelas/{school?.id}"
						style="color: {school?.hue}; border-color: {school?.hue}55; background: {school?.hue}14; text-decoration: none"
					>
						{school?.glyph} {school?.name}
					</a>
					{#if mother}
						<a
							class="badge cursor-star"
							href="/artefacto/{mother.id}"
							style="text-decoration: none"
							title="Plantilla madre"
						>
							<Icon name="variant" s={13} /> variante de {mother.title}
						</a>
					{/if}
				</div>
				<h1 class="t-display" style="font-size: clamp(34px, 5vw, 52px); font-weight: 700; margin: 0 0 6px; line-height: 1.05">
					{art.title}
				</h1>
				<p class="muted" style="margin: 0 0 14px; font-style: italic">{art.origin}</p>

				<!-- Visitas + reacciones -->
				<div class="row gap-3" style="margin-bottom: 22px; flex-wrap: wrap">
					<span class="row gap-1 muted" style="font-size: 12.5px; gap: 5px">
						<Icon name="eye" s={14} /> {(art.views ?? 0).toLocaleString()} visitas
					</span>
					<button
						class="row gap-1 btn ghost cursor-star"
						style="font-size: 12.5px; padding: 4px 10px; gap: 5px; {art.userReaction === 'like' ? 'color: var(--gold-bright); border-color: var(--gold)' : ''}"
						onclick={() => react('like')}
						disabled={reacting || !auth.user}
						title={auth.user ? 'Me gusta' : 'Identifícate para reaccionar'}
					>
						<Icon name="thumbup" s={14} /> {art.likes ?? 0}
					</button>
					<button
						class="row gap-1 btn ghost cursor-star"
						style="font-size: 12.5px; padding: 4px 10px; gap: 5px; {art.userReaction === 'dislike' ? 'color: var(--ember); border-color: var(--ember)' : ''}"
						onclick={() => react('dislike')}
						disabled={reacting || !auth.user}
						title={auth.user ? 'No me gusta' : 'Identifícate para reaccionar'}
					>
						<Icon name="thumbdown" s={14} /> {art.dislikes ?? 0}
					</button>
				</div>

				<div class="card flat" style="margin-bottom: 24px">
					<Corner cls="tl" /><Corner cls="tr" /><Corner cls="bl" /><Corner cls="br" />
					{#if art.media === 'image' && art.mediaUrl}
						<img src={art.mediaUrl} alt={art.title} style="width: 100%; display: block; border-radius: var(--r-md)" />
					{:else if art.media === 'video' && art.mediaUrl && !videoError}
						<video
							src={art.mediaUrl}
							controls
							loop
							style="width: 100%; display: block; border-radius: var(--r-md); background: #000"
							onerror={() => { videoError = true; }}
						></video>
					{:else if (art.media === 'video' || art.media === 'audio') && !art.mediaUrl}
						{#if ytId}
							<!-- sourceUrl de YouTube — embed directo, el archivo se puede preservar aparte -->
							<div style="position: relative; padding-bottom: 56.25%; height: 0; border-radius: var(--r-md); overflow: hidden; background: #000">
								<iframe
									src="https://www.youtube.com/embed/{ytId}"
									title={art.title}
									frameborder="0"
									allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
									allowfullscreen
									style="position: absolute; inset: 0; width: 100%; height: 100%; border: 0"
								></iframe>
							</div>
							{#if auth.isArchimago}
								<div style="margin-top: 10px; display: flex; gap: 8px; align-items: center; justify-content: flex-end">
									<span class="muted" style="font-size: 11.5px">
										{ingesting ? 'Preservando en el grimorio…' : 'Aún no preservado en el grimorio'}
									</span>
									{#if !ingesting}
										<button class="btn cursor-star" onclick={retryIngest} disabled={ingestRetrying} style="font-size: 12px; padding: 5px 10px">
											<Icon name="upload" s={13} /> {ingestRetrying ? 'Relanzando…' : 'Preservar'}
										</button>
									{/if}
								</div>
							{/if}
						{:else}
							<!-- Sin YouTube y sin archivo — mostrar estado -->
							<div style="padding: 40px 24px; text-align: center; color: var(--muted)">
								<div class="t-arcane" style="font-size: 18px; color: var(--gold); margin-bottom: 10px">
									{ingesting ? 'Preservando artefacto…' : 'Artefacto sin preservar'}
								</div>
								<p style="font-size: 13px; margin: 0 0 16px">
									{ingesting ? 'El grimorio está descargando el archivo. Aparecerá en unos momentos.' : 'El archivo aún no ha sido preservado en el grimorio.'}
								</p>
								{#if auth.isArchimago && art.sourceUrl && !ingesting}
									<button class="btn cursor-star" onclick={retryIngest} disabled={ingestRetrying} style="font-size: 12.5px">
										<Icon name="upload" s={14} /> {ingestRetrying ? 'Relanzando…' : 'Reintentar preservación'}
									</button>
								{/if}
							</div>
						{/if}
					{:else if videoError}
						<div style="padding: 40px 24px; text-align: center; color: var(--muted)">
							<div class="t-arcane" style="font-size: 18px; color: var(--ember); margin-bottom: 10px">El artefacto no pudo invocarse</div>
							<p style="font-size: 13px; margin: 0 0 14px">El formato del archivo no es compatible con el navegador.</p>
							{#if art.sourceUrl}
								<a href={art.sourceUrl} target="_blank" rel="noopener noreferrer" class="btn cursor-star" style="font-size: 12.5px">
									<Icon name="link" s={14} /> Ver fuente original
								</a>
							{/if}
						</div>
					{:else}
						<Plate {art} big />
					{/if}
					{#if playable}
						<div
							class="row"
							style="justify-content: space-between; padding: 14px 18px; border-top: 1px solid rgba(201,168,76,.14)"
						>
							<div class="row gap-3">
								<div
									class="pp cursor-star"
									role="button"
									tabindex="0"
									style="width: 44px; height: 44px"
									onclick={() => player.play(art!, catalog.playable)}
									onkeydown={(e) => e.key === 'Enter' && player.play(art!, catalog.playable)}
								>
									{#if isCurrent && player.playing}<Icon name="pause" s={19} />{:else}<Icon name="play" s={19} />{/if}
								</div>
								<div>
									<div style="font-size: 13.5px; font-weight: 650">
										{isCurrent && player.playing ? 'Resonando…' : 'Invocar sonido'}
									</div>
									<div class="muted" style="font-size: 11.5px">
										{art.media === 'audio' ? 'artefacto encantado · loop' : 'visión en bucle'}
									</div>
								</div>
							</div>
							<Viz active={isCurrent && player.playing} bars={22} />
						</div>
					{/if}
				</div>

				<h3 class="t-arcane" style="font-size: 21px; margin: 0 0 10px">Del códice</h3>
				<p class="lede illuminate" style="font-size: 16.5px">{@html arcaneHtml(art.desc)}</p>

				{#if variants.length > 0}
					<div style="margin-top: 36px">
						<div class="row gap-3" style="margin-bottom: 4px">
							<Icon name="variant" s={20} style="color: var(--gold-bright)" />
							<h3 class="t-arcane" style="font-size: 21px; margin: 0">Variantes del sello</h3>
						</div>
						<p class="muted" style="font-size: 12.5px; margin: 0 0 14px">
							Derivados que mutaron de esta plantilla madre.
						</p>
						<div class="grid-cards">
							{#each variants as v (v.id)}
								<SpellCard art={v} />
							{/each}
						</div>
					</div>
				{/if}

				<!-- Pergamino de notas -->
				<div style="margin-top: 36px">
					<div class="row gap-3" style="margin-bottom: 4px">
						<Icon name="quill" s={20} style="color: var(--gold-bright)" />
						<h3 class="t-arcane" style="font-size: 21px; margin: 0">Pergamino de notas</h3>
					</div>
					<p class="muted" style="font-size: 12.5px; margin: 0 0 14px">
						Los aprendices anotan al margen. {notes.length} anotación{notes.length !== 1 ? 'es' : ''}.
					</p>
					{#if auth.user}
						<div
							class="glass"
							style="border-radius: var(--r-md); padding: 10px 14px; margin-bottom: 18px; display: flex; gap: 10px; align-items: flex-end"
						>
							<textarea
								class="textarea"
								style="min-height: 52px; border: 0; background: transparent; padding: 6px"
								placeholder="Anota tu glosa en el margen…"
								bind:value={draft}
							></textarea>
							<button class="btn cursor-star" onclick={addNote} style="flex: 0 0 auto">
								<Icon name="quill" s={15} /> Anotar
							</button>
						</div>
						{#if noteError}<p style="color: var(--ember); font-size: 12.5px">{noteError}</p>{/if}
					{:else}
						<div class="glass" style="border-radius: var(--r-md); padding: 14px 18px; margin-bottom: 18px">
							<span class="muted" style="font-size: 13px">
								Solo los iniciados anotan en el margen. <a href="/auth" style="color: var(--gold-bright)">Identifícate</a>
								para mojar la pluma.
							</span>
						</div>
					{/if}
					{#each notes as n (n.id)}
						<div class="note">
							<div class="av">{n.glyph}</div>
							<div style="flex: 1">
								<div class="row gap-2">
									<a class="nwho cursor-star" href="/mago/{n.who}" style="text-decoration: none; color: inherit">{n.who}</a><span class="nwhen">· {arcaneTime(n.when)}</span>
								</div>
								<div class="ntext">{@html arcaneHtml(n.text)}</div>
							</div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Columna lateral -->
			<aside style="position: sticky; top: 84px">
				{#if playable && auth.user}
					<div style="position: relative; margin-bottom: 10px">
						<button
							class="btn cursor-star"
							style="width: 100%; box-sizing: border-box"
							onclick={() => (spellPickerOpen = !spellPickerOpen)}
						>
							<Icon name="spell" s={15} /> Añadir a hechizo
						</button>
						{#if spellPickerOpen}
							<div class="glass popup" style="position: absolute; top: calc(100% + 6px); left: 0; right: 0; border-radius: var(--r-md); padding: 6px; z-index: 20">
								{#if catalog.spells.length === 0}
									<p class="muted" style="font-size: 12px; padding: 8px; margin: 0">No hay hechizos creados.</p>
								{/if}
								{#each catalog.spells as s (s.id)}
									<button
										class="btn ghost cursor-star"
										style="width: 100%; margin-bottom: 4px; justify-content: flex-start; gap: 8px; font-size: 12.5px; {s.tracks.includes(art.id) ? 'opacity:.45; pointer-events:none' : ''}"
										onclick={() => addToSpell(s.id)}
										disabled={!!addingToSpell || s.tracks.includes(art.id)}
									>
										<span style="color: {s.hue}">{s.glyph}</span>
										{s.name}
										{#if s.tracks.includes(art.id)}<Icon name="check" s={13} />{/if}
									</button>
								{/each}
								<button class="btn ghost cursor-star" style="width: 100%; font-size: 11.5px; color: var(--muted)" onclick={() => (spellPickerOpen = false)}>
									Cancelar
								</button>
							</div>
						{/if}
					</div>
				{/if}
				{#if auth.isArchimago}
					<a
						class="btn cursor-star"
						style="width: 100%; margin-bottom: 10px; border-color: var(--gold); color: var(--gold-bright); text-decoration: none; box-sizing: border-box"
						href="/invocar?edit={art.id}"
					>
						<Icon name="edit" s={16} /> Editar sello
					</a>
					{#if art.sourceUrl && art.media !== 'text'}
						<button
							class="btn cursor-star"
							style="width: 100%; margin-bottom: 10px; box-sizing: border-box"
							onclick={retryIngest}
							disabled={ingestRetrying || ingesting}
						>
							<Icon name="upload" s={15} />
							{ingesting ? 'Descargando…' : ingestRetrying ? 'Relanzando…' : art?.mediaUrl ? 'Redescargar archivo' : 'Descargar archivo'}
						</button>
					{/if}
					{#if confirmDelete}
						<div class="glass" style="border-radius: var(--r-md); padding: 12px 14px; margin-bottom: 10px; border-color: var(--ember)">
							<p style="font-size: 12.5px; margin: 0 0 10px; color: var(--parchment)">¿Borrar «{art.title}» del grimorio para siempre?</p>
							<div class="row gap-2">
								<button class="btn cursor-star" style="flex:1; border-color: var(--ember); color: var(--ember)" onclick={deleteArt} disabled={deleting}>
									{deleting ? 'Borrando…' : 'Sí, borrar'}
								</button>
								<button class="btn cursor-star" style="flex:1" onclick={() => confirmDelete = false}>Cancelar</button>
							</div>
						</div>
					{:else}
						<button
							class="btn cursor-star"
							style="width: 100%; margin-bottom: 16px; box-sizing: border-box; border-color: rgba(181,85,47,.4); color: var(--ember)"
							onclick={() => confirmDelete = true}
						>
							<Icon name="close" s={15} /> Borrar artefacto
						</button>
					{/if}
				{/if}
				<div class="glass" style="border-radius: var(--r-lg); padding: 20px; margin-bottom: 22px">
					<div class="eyebrow" style="margin-bottom: 14px">Inscripción</div>
					{#each [['Época', String(art.era)], ['Escuela', school?.name ?? art.school], ['Naturaleza', TYPE_META[art.type]?.label ?? art.type]] as [k, v] (k + v)}
						<div
							class="row"
							style="justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed rgba(201,168,76,.12)"
						>
							<span class="muted" style="font-size: 12.5px">{k}</span>
							<span style="font-size: 13.5px; font-weight: 600; color: var(--parchment)">{@html arcaneHtml(v)}</span>
						</div>
					{/each}
					<div class="row" style="justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed rgba(201,168,76,.12)">
						<span class="muted" style="font-size: 12.5px">Sellado por</span>
						<a href="/mago/{art.sealedBy}" class="cursor-star" style="font-size: 13.5px; font-weight: 600; color: var(--parchment); text-decoration: none">{art.sealedBy}</a>
					</div>
					<div style="padding-top: 14px">
						<span class="muted" style="font-size: 12.5px; display: block; margin-bottom: 8px">Runas</span>
						<RuneCloud runes={art.runes} />
					</div>
				</div>

				<div class="row gap-2" style="margin-bottom: 12px">
					<Icon name="link" s={18} style="color: var(--gold-bright)" />
					<h3 class="t-arcane" style="font-size: 20px; margin: 0">Artefactos vinculados</h3>
				</div>
				<p class="muted" style="font-size: 12px; margin: 0 0 12px">Círculo de invocación. Toca un nodo para viajar a él.</p>
				<RelicGraph {art} />
			</aside>
		</div>
	{/if}
</div>
