<script lang="ts">
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import Icon from '$lib/components/Icon.svelte';
	import RuneCloud from '$lib/components/RuneCloud.svelte';
	import SealButton from '$lib/components/SealButton.svelte';
	import Sigil from '$lib/components/Sigil.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { ARTIFACT_TYPES, TYPE_META, type Artifact, type ArtifactType, type MediaKind } from '$lib/types';

	const ICON_BY_TYPE: Record<ArtifactType, string> = {
		pergamino: 'scroll',
		reliquia: 'relic',
		hechizo: 'spell',
		visión: 'vision'
	};
	const MEDIA_BY_TYPE: Record<ArtifactType, MediaKind> = {
		pergamino: 'text',
		reliquia: 'image',
		hechizo: 'audio',
		visión: 'video'
	};

	const editId = $derived(page.url.searchParams.get('edit'));

	let type = $state<ArtifactType | ''>('');
	let name = $state('');
	let desc = $state('');
	let origin = $state('');
	let school = $state('');
	let era = $state<number | ''>('');
	let sourceUrl = $state('');
	let runes = $state<string[]>([]);
	let links = $state<string[]>([]);
	let variantOf = $state<string | null>(null);
	let linkQ = $state('');
	let variantQ = $state('');
	let sealed = $state(false);
	let done = $state<Artifact | null>(null);
	let submitting = $state(false);
	let error = $state('');

	// Modo edición (solo Archimago): carga el artefacto existente
	$effect(() => {
		const target = editId;
		if (!target || !auth.isArchimago) return;
		void api.get<Artifact>(`/artifacts/${target}`).then((a) => {
			type = a.type;
			name = a.title;
			desc = a.desc;
			origin = a.origin;
			school = a.school;
			era = a.era;
			sourceUrl = a.sourceUrl ?? '';
			runes = [...a.runes];
			links = [...a.links];
			variantOf = a.variantOf ?? null;
		});
	});

	function toggleRune(r: string) {
		runes = runes.includes(r) ? runes.filter((x) => x !== r) : [...runes, r];
	}

	const linkMatches = $derived(
		linkQ.trim()
			? catalog.artifacts
					.filter(
						(a) =>
							a.title.toLowerCase().includes(linkQ.toLowerCase()) && !links.includes(a.id) && a.id !== editId
					)
					.slice(0, 4)
			: []
	);
	const variantMatches = $derived(
		variantQ.trim()
			? catalog.artifacts
					.filter((a) => a.title.toLowerCase().includes(variantQ.toLowerCase()) && a.id !== editId)
					.slice(0, 4)
			: []
	);
	const variantMother = $derived(variantOf ? catalog.findArt(variantOf) : undefined);

	const ready = $derived(Boolean(type && name.trim() && desc.trim() && school));
	const canSeal = $derived(auth.isModerator);
	const isEditing = $derived(Boolean(editId && auth.isArchimago));

	async function seal() {
		if (!ready || !auth.user || submitting) return;
		submitting = true;
		error = '';
		sealed = true;
		try {
			const payload = {
				title: name.trim(),
				type,
				school,
				era: era === '' ? new Date().getFullYear() : Number(era),
				media: MEDIA_BY_TYPE[type as ArtifactType],
				runes,
				origin: origin.trim(),
				desc: desc.trim(),
				links,
				variantOf,
				sourceUrl: sourceUrl.trim() || null
			};
			const art = isEditing
				? await api.patch<Artifact>(`/artifacts/${editId}`, payload)
				: await api.post<Artifact>('/artifacts', payload);
			await catalog.load(true);
			setTimeout(() => (done = art), 650);
		} catch (e) {
			sealed = false;
			error = e instanceof Error ? e.message : 'El sello se resistió';
		} finally {
			submitting = false;
		}
	}

	function reset() {
		done = null;
		sealed = false;
		type = '';
		name = '';
		desc = '';
		origin = '';
		school = '';
		era = '';
		sourceUrl = '';
		runes = [];
		links = [];
		variantOf = null;
	}
</script>

<svelte:head><title>Invocar · SPELLBOOK</title></svelte:head>

{#if done}
	<div class="canvas" style="max-width: 620px; text-align: center; padding-top: 80px">
		<div style="display: flex; justify-content: center; margin-bottom: 22px"><Sigil s={84} /></div>
		<h1 class="t-display" style="font-size: 40px; margin: 0 0 10px">
			{done.status === 'sellado' ? 'Sellado.' : 'Propuesto.'}
		</h1>
		<p class="lede" style="margin: 0 auto 28px; max-width: 440px">
			{#if done.status === 'sellado'}
				«{done.title}» ha sido inscrito en el Grimorio bajo la escuela de {catalog.school(done.school)?.name}. Que
				perdure mil años.
			{:else}
				«{done.title}» aguarda el juicio del cónclave. Un mago o el Archimago decidirá si merece el sello.
			{/if}
		</p>
		<div class="row gap-3" style="justify-content: center">
			<button class="btn cursor-star" onclick={reset}>
				{done.status === 'sellado' ? 'Sellar otro' : 'Proponer otro'}
			</button>
			<a class="btn cursor-star" href="/explorar" style="border-color: var(--gold); color: var(--gold-bright); text-decoration: none">
				Ver el Grimorio
			</a>
		</div>
	</div>
{:else}
	<div class="canvas" style="max-width: 760px">
		<div style="text-align: center; margin-bottom: 8px">
			<div class="eyebrow" style="margin-bottom: 10px">{isEditing ? 'Reescritura del sello' : 'Rito de inscripción'}</div>
			<h1 class="t-arcane" style="font-size: 40px; margin: 0; color: var(--gold-bright)">
				{isEditing ? 'Editar el sello' : 'Invocar artefacto'}
			</h1>
			<p class="muted" style="max-width: 480px; margin: 10px auto 0; line-height: 1.6">
				Toda inscripción es permanente. Procede con la solemnidad que el grimorio merece.
			</p>
		</div>

		<!-- gates por rol -->
		{#if !auth.user}
			<div
				class="glass"
				style="border-radius: var(--r-lg); padding: 16px 20px; margin: 24px 0; display: flex; gap: 14px; align-items: center; border-color: var(--ember)"
			>
				<Icon name="wizard" s={26} style="color: var(--ember); flex: 0 0 auto" />
				<div style="flex: 1">
					<div style="font-weight: 650; font-size: 14px">Solo los iniciados pueden añadir conocimiento</div>
					<div class="muted" style="font-size: 12.5px">
						Los profanos contemplan el rito, pero no lo consuman. Hace falta una invitación.
					</div>
				</div>
				<a
					class="btn cursor-star"
					href="/auth"
					style="flex: 0 0 auto; border-color: var(--gold); color: var(--gold-bright); text-decoration: none"
				>
					Identifícate
				</a>
			</div>
		{:else if !canSeal}
			<div
				class="glass"
				style="border-radius: var(--r-lg); padding: 16px 20px; margin: 24px 0; display: flex; gap: 14px; align-items: center"
			>
				<Icon name="clock" s={26} style="color: var(--gold); flex: 0 0 auto" />
				<div style="flex: 1">
					<div style="font-weight: 650; font-size: 14px">Tu propuesta pasará por el juicio del cónclave</div>
					<div class="muted" style="font-size: 12.5px">
						Como aprendiz propones artefactos; un mago o el Archimago los aprueba. Con la edad y las obras llegará tu
						ascenso.
					</div>
				</div>
			</div>
		{/if}

		<div class="glass" style="border-radius: var(--r-xl); padding: 30px; margin-top: {auth.user && canSeal ? '28px' : '0'}">
			<!-- Naturaleza -->
			<div class="field">
				<label for="invoke-type">Naturaleza del artefacto</label>
				<div class="type-grid" id="invoke-type">
					{#each ARTIFACT_TYPES as t (t)}
						<div
							class="type-tile cursor-star"
							class:on={type === t}
							role="radio"
							aria-checked={type === t}
							tabindex="0"
							onclick={() => (type = t)}
							onkeydown={(e) => e.key === 'Enter' && (type = t)}
						>
							<Icon name={ICON_BY_TYPE[t]} s={24} />
							<span class="lbl">{TYPE_META[t].label}</span>
							<span class="sub">{TYPE_META[t].sub}</span>
						</div>
					{/each}
				</div>
			</div>

			<div class="field">
				<label for="f-name">Nomina el artefacto</label>
				<input id="f-name" class="input" placeholder="p. ej. Never Gonna Give You Up" bind:value={name} />
			</div>

			<div class="field">
				<label for="f-desc">Describe su naturaleza</label>
				<textarea
					id="f-desc"
					class="textarea"
					placeholder="Una entrada de enciclopedia. Qué es, de dónde viene, qué poder ejerce sobre los mortales…"
					bind:value={desc}
				></textarea>
			</div>

			<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 18px" class="invoke-cols">
				<div class="field">
					<label for="f-origin">Sella su origen</label>
					<input id="f-origin" class="input" placeholder="De dónde fue arrancado" bind:value={origin} />
				</div>
				<div class="field">
					<label for="f-era">Época</label>
					<input id="f-era" class="input" type="number" placeholder="MMXX → 2020" bind:value={era} />
				</div>
			</div>

			<div class="field">
				<label for="f-url">URL de origen <span class="muted" style="font-size: 12px">(opcional · YouTube, TikTok…)</span></label>
				<input id="f-url" class="input" placeholder="https:// — será preservado por el escriba mecánico" bind:value={sourceUrl} />
				<div class="hint">La preservación automática (yt-dlp) llegará en una futura luna; la URL queda sellada ya.</div>
			</div>

			<div class="field">
				<label for="f-school">Escuela de magia</label>
				<select id="f-school" class="select" bind:value={school}>
					<option value="">— elige una disciplina —</option>
					{#each catalog.schools as s (s.id)}
						<option value={s.id}>{s.glyph} {s.name}</option>
					{/each}
				</select>
			</div>

			<div class="field">
				<label for="f-runes">Marca sus runas</label>
				<div id="f-runes"><RuneCloud runes={catalog.runes} active={runes} onToggle={toggleRune} /></div>
				<div class="hint">{runes.length} runa{runes.length !== 1 ? 's' : ''} marcada{runes.length !== 1 ? 's' : ''}</div>
			</div>

			<div class="field">
				<label for="f-links">Traza vínculos</label>
				<input id="f-links" class="input" placeholder="Busca artefactos existentes para enlazarlos…" bind:value={linkQ} />
				{#if linkMatches.length > 0}
					<div class="glass" style="border-radius: var(--r-md); margin-top: 6px; padding: 6px">
						{#each linkMatches as a (a.id)}
							<div
								class="ores cursor-star"
								role="button"
								tabindex="0"
								onclick={() => {
									links = [...links, a.id];
									linkQ = '';
								}}
								onkeydown={(e) => {
									if (e.key === 'Enter') {
										links = [...links, a.id];
										linkQ = '';
									}
								}}
							>
								<div class="oic">{a.glyph}</div>
								<div style="flex: 1">
									<div class="otitle">{a.title}</div>
									<div class="osub">{TYPE_META[a.type]?.label}</div>
								</div>
								<Icon name="link" s={16} style="color: var(--gold)" />
							</div>
						{/each}
					</div>
				{/if}
				{#if links.length > 0}
					<div class="runecloud" style="margin-top: 10px">
						{#each links as lid (lid)}
							{@const a = catalog.findArt(lid)}
							<button
								type="button"
								class="rune on cursor-star"
								style="padding-right: 8px"
								onclick={() => (links = links.filter((x) => x !== lid))}
							>
								{a?.title ?? lid} <Icon name="close" s={12} />
							</button>
						{/each}
					</div>
				{/if}
			</div>

			<div class="field">
				<label for="f-variant">Variante de <span class="muted" style="font-size: 12px">(opcional · plantilla madre)</span></label>
				{#if variantMother}
					<div class="runecloud">
						<button type="button" class="rune on cursor-star" style="padding-right: 8px" onclick={() => (variantOf = null)}>
							{variantMother.title} <Icon name="close" s={12} />
						</button>
					</div>
				{:else}
					<input
						id="f-variant"
						class="input"
						placeholder="¿Este artefacto mutó de otro? Busca su plantilla madre…"
						bind:value={variantQ}
					/>
					{#if variantMatches.length > 0}
						<div class="glass" style="border-radius: var(--r-md); margin-top: 6px; padding: 6px">
							{#each variantMatches as a (a.id)}
								<div
									class="ores cursor-star"
									role="button"
									tabindex="0"
									onclick={() => {
										variantOf = a.id;
										variantQ = '';
									}}
									onkeydown={(e) => {
										if (e.key === 'Enter') {
											variantOf = a.id;
											variantQ = '';
										}
									}}
								>
									<div class="oic">{a.glyph}</div>
									<div style="flex: 1">
										<div class="otitle">{a.title}</div>
										<div class="osub">{TYPE_META[a.type]?.label}</div>
									</div>
									<Icon name="variant" s={16} style="color: var(--gold)" />
								</div>
							{/each}
						</div>
					{/if}
				{/if}
			</div>

			<hr class="hairline" style="margin: 10px 0 22px" />
			{#if error}<p style="color: var(--ember); font-size: 13px; margin: 0 0 14px">{error}</p>{/if}
			<div class="row" style="justify-content: space-between; flex-wrap: wrap; gap: 14px">
				<span class="muted" style="font-size: 12.5px; max-width: 280px">
					{ready
						? canSeal
							? 'El artefacto está listo para el sello.'
							: 'La propuesta está lista para el cónclave.'
						: 'Completa naturaleza, nombre, descripción y escuela.'}
				</span>
				<SealButton onclick={seal} {sealed} disabled={!ready || !auth.user || submitting}>
					{canSeal ? (isEditing ? 'Reescribir el sello' : 'Sellar en el Grimorio') : 'Proponer al cónclave'}
				</SealButton>
			</div>
		</div>
	</div>
{/if}
