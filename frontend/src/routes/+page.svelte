<script lang="ts">
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import Sigil from '$lib/components/Sigil.svelte';
	import SpellCard from '$lib/components/SpellCard.svelte';
	import StarSep from '$lib/components/StarSep.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { oracle } from '$lib/stores/oracle.svelte';
	import { romanize } from '$lib/utils';

	const recent = $derived(catalog.artifacts.slice(0, 6));
	const stats = $derived(catalog.stats);

	const quick = [
		{ id: 'pergamino', g: '☽', l: 'Pergaminos', s: 'texto', href: '/explorar?type=pergamino' },
		{ id: 'reliquia', g: '✶', l: 'Reliquias', s: 'imagen', href: '/explorar?type=reliquia' },
		{ id: 'hechizo', g: '♫', l: 'Hechizos', s: 'audio', href: '/hechizos' },
		{ id: 'escuela', g: '☥', l: 'Escuelas', s: 'géneros', href: '/escuelas' },
		{ id: 'runa', g: '✦', l: 'Runas', s: 'etiquetas', href: '/explorar' }
	];
</script>

<svelte:head><title>SPELLBOOK · omnia memes in unum</title></svelte:head>

<div class="canvas">
	<!-- Hero -->
	<div style="text-align: center; padding: 26px 0 8px">
		<div style="display: flex; justify-content: center; margin-bottom: 18px"><Sigil s={62} /></div>
		<h1
			class="t-display"
			style="font-size: clamp(52px, 9vw, 104px); font-weight: 900; margin: 0; background: linear-gradient(180deg, #f4e7c0, #c9a84c 58%, #7b6224); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 0.02em"
		>
			SPELLBOOK
		</h1>
		<p class="t-arcane" style="font-size: 22px; margin: 10px 0 4px; color: var(--gold)">omnia memes in unum</p>
		<p class="muted" style="max-width: 540px; margin: 10px auto 0; line-height: 1.6">
			La bóveda de preservación de la cultura de internet. Cada meme, canción viral y copypasta, documentado,
			vinculado y sellado para la posteridad.
		</p>
	</div>

	<div style="display: flex; justify-content: center; margin: 30px 0 18px"><StarSep w={260} /></div>

	<!-- El Oráculo -->
	<div
		class="glass cursor-star"
		role="button"
		tabindex="0"
		onclick={() => oracle.show()}
		onkeydown={(e) => e.key === 'Enter' && oracle.show()}
		style="max-width: 680px; margin: 0 auto 14px; border-radius: var(--r-xl); padding: 16px 20px; display: flex; align-items: center; gap: 14px; border-color: var(--glass-border-hi)"
	>
		<Icon name="oracle" s={24} style="color: var(--gold-bright)" />
		<span style="flex: 1; color: var(--faint); font-size: 16px">Invoca un artefacto, hechizo o reliquia…</span>
		<span class="kbd">⌘</span><span class="kbd">K</span>
	</div>

	<!-- Stats -->
	<div class="stats" style="justify-content: center; margin: 22px 0 40px">
		<div class="stat" style="text-align: center">
			<div class="n">{stats?.artifacts ?? '—'}</div>
			<div class="l">artefactos sellados</div>
		</div>
		<div class="stat" style="text-align: center">
			<div class="n">{stats?.connections ?? '—'}</div>
			<div class="l">conexiones trazadas</div>
		</div>
		<div class="stat" style="text-align: center">
			<div class="n">{romanize(stats?.schools ?? 8)}</div>
			<div class="l">escuelas de magia</div>
		</div>
		<div class="stat" style="text-align: center">
			<div class="n">{romanize(stats?.since ?? 2020)}</div>
			<div class="l">desde el primer sello</div>
		</div>
	</div>

	<!-- Accesos rápidos -->
	<div class="quick" style="margin-bottom: 48px">
		{#each quick as q (q.id)}
			<a class="cursor-star" href={q.href}>
				<span class="medal">{q.g}</span>
				<span class="qlbl">{q.l}</span>
				<span class="qsub">{q.s}</span>
			</a>
		{/each}
	</div>

	<!-- Feed reciente -->
	<SectionHead eyebrow="Recién sellados" title="Artefactos recientes">
		{#snippet right()}
			<a class="btn cursor-star" href="/explorar" style="text-decoration: none">
				Ver el Grimorio completo <Icon name="chevron" s={16} />
			</a>
		{/snippet}
	</SectionHead>
	<div class="grid-cards">
		{#each recent as a (a.id)}
			<SpellCard art={a} />
		{/each}
	</div>
</div>
