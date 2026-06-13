<script lang="ts">
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import Viz from '$lib/components/Viz.svelte';
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
</script>

<svelte:head><title>Hechizos · SPELLBOOK</title></svelte:head>

<div class="canvas">
	<SectionHead
		eyebrow="Cánticos sellados"
		title="Hechizos"
		sub="Colecciones de melodías virales encantadas. Invócalas y resonarán en el dock arcano."
	/>
	<div style="display: grid; grid-template-columns: 300px 1fr; gap: 30px; align-items: start" class="spells-grid">
		<!-- Lista de hechizos -->
		<div style="display: flex; flex-direction: column; gap: 12px">
			{#each catalog.spells as s (s.id)}
				<div
					class="card flat cursor-star"
					role="button"
					tabindex="0"
					onclick={() => (sel = s.id)}
					onkeydown={(e) => e.key === 'Enter' && (sel = s.id)}
					style="padding: 16px; display: flex; gap: 14px; align-items: center; cursor: pointer; border-color: {s.id === spell?.id
						? 'var(--glass-border-hi)'
						: 'var(--glass-border)'}; box-shadow: {s.id === spell?.id ? 'var(--glow-amber)' : 'var(--inner-vellum)'}"
				>
					<div
						style="width: 54px; height: 54px; border-radius: 12px; display: grid; place-items: center; flex: 0 0 auto; font-family: var(--font-arcane); font-size: 26px; color: {s.hue}; background: radial-gradient(circle at 38% 32%, {s.hue}26, rgba(0,0,0,.3)); border: 1px solid var(--glass-border)"
					>
						{s.glyph}
					</div>
					<div style="min-width: 0">
						<div class="card-title" style="margin: 0 0 3px; font-size: 15px">{s.name}</div>
						<div class="muted" style="font-size: 12px">{s.tracks.length} pistas</div>
					</div>
				</div>
			{/each}
		</div>

		<!-- Detalle del hechizo -->
		{#if spell}
			<div class="glass" style="border-radius: var(--r-xl); overflow: hidden">
				<div
					style="padding: 28px 28px 22px; display: flex; gap: 22px; align-items: center; background: linear-gradient(135deg, {spell.hue}1f, transparent 70%); border-bottom: 1px solid rgba(201,168,76,.14)"
				>
					<div
						style="width: 96px; height: 96px; border-radius: 18px; display: grid; place-items: center; flex: 0 0 auto; font-family: var(--font-arcane); font-size: 48px; color: {spell.hue}; background: radial-gradient(circle at 38% 32%, {spell.hue}33, rgba(0,0,0,.35)); border: 1px solid var(--glass-border-hi); box-shadow: var(--glow-amber)"
					>
						{spell.glyph}
					</div>
					<div>
						<div class="eyebrow" style="margin-bottom: 6px">Hechizo · {tracks.length} cánticos</div>
						<h2 class="t-arcane" style="font-size: 32px; margin: 0 0 6px; color: {spell.hue}">{spell.name}</h2>
						<p class="muted" style="margin: 0; max-width: 460px; line-height: 1.5">{spell.desc}</p>
					</div>
				</div>
				<div style="padding: 10px 14px 16px">
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
							<span class="muted" style="width: 22px; text-align: center; font-variant-numeric: tabular-nums">
								{isCur && player.playing ? '♪' : i + 1}
							</span>
							<div class="lglyph" style="width: 44px; height: 44px">{t.glyph}</div>
							<div style="flex: 1; min-width: 0">
								<div
									class="card-title"
									style="margin: 0 0 2px; font-size: 14.5px; color: {isCur ? 'var(--gold-bright)' : 'var(--parchment)'}"
								>
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
								<Icon name="play" s={17} style="color: var(--muted)" />
							{/if}
							<a
								class="btn ghost cursor-star"
								style="padding: 6px"
								href="/artefacto/{t.id}"
								onclick={(e) => e.stopPropagation()}
								aria-label="Ver artefacto"
							>
								<Icon name="chevron" s={16} />
							</a>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>
