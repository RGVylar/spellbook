<script lang="ts">
	import { goto } from '$app/navigation';
	import Icon from '$lib/components/Icon.svelte';
	import Starfield from '$lib/components/Starfield.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { oracle } from '$lib/stores/oracle.svelte';
	import { TYPE_META, type Artifact, type School, type Spell } from '$lib/types';

	type Result =
		| { kind: 'art'; a: Artifact }
		| { kind: 'school'; sc: School }
		| { kind: 'spell'; sp: Spell };

	let q = $state('');
	let sel = $state(0);
	let inputEl: HTMLInputElement | undefined = $state();

	$effect(() => {
		if (oracle.open) {
			q = '';
			sel = 0;
			setTimeout(() => inputEl?.focus(), 30);
		}
	});

	const results = $derived.by<Result[]>(() => {
		const s = q.trim().toLowerCase();
		const pool: Result[] = catalog.artifacts.map((a) => ({ kind: 'art', a }));
		for (const sc of catalog.schools) pool.push({ kind: 'school', sc });
		for (const sp of catalog.spells) pool.push({ kind: 'spell', sp });
		if (!s) return pool.filter((p) => p.kind === 'art').slice(0, 6);
		return pool
			.filter((p) => {
				const hay =
					p.kind === 'art'
						? p.a.title + ' ' + p.a.runes.join(' ') + ' ' + p.a.type
						: p.kind === 'school'
							? p.sc.name + ' escuela'
							: p.sp.name + ' hechizo';
				return hay.toLowerCase().includes(s);
			})
			.slice(0, 8);
	});

	$effect(() => {
		if (sel >= results.length) sel = 0;
	});

	function choose(r: Result | undefined) {
		if (!r) return;
		oracle.hide();
		if (r.kind === 'art') void goto(`/artefacto/${r.a.id}`);
		else if (r.kind === 'school') void goto(`/escuelas/${r.sc.id}`);
		else void goto(`/hechizos?id=${r.sp.id}`);
	}

	function onKey(e: KeyboardEvent) {
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			sel = Math.min(sel + 1, results.length - 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			sel = Math.max(sel - 1, 0);
		} else if (e.key === 'Enter') {
			e.preventDefault();
			choose(results[sel]);
		} else if (e.key === 'Escape') {
			oracle.hide();
		}
	}

	function meta(r: Result): { title: string; glyph: string; sub: string } {
		if (r.kind === 'art')
			return { title: r.a.title, glyph: r.a.glyph, sub: (TYPE_META[r.a.type]?.label ?? r.a.type) + ' · ' + r.a.era };
		if (r.kind === 'school') return { title: r.sc.name, glyph: r.sc.glyph, sub: 'Escuela de magia' };
		return { title: r.sp.name, glyph: r.sp.glyph, sub: 'Hechizo · ' + r.sp.tracks.length + ' pistas' };
	}
</script>

{#if oracle.open}
	<div class="oracle-scrim" onclick={() => oracle.hide()} role="presentation">
		<div
			class="oracle"
			onclick={(e) => e.stopPropagation()}
			onkeydown={(e) => e.stopPropagation()}
			role="dialog"
			aria-label="El Oráculo"
			tabindex="-1"
		>
			<Starfield />
			<div class="oracle-input-row">
				<Icon name="oracle" s={24} style="color: var(--gold-bright)" />
				<input
					bind:this={inputEl}
					bind:value={q}
					onkeydown={onKey}
					placeholder="Invoca un artefacto, hechizo o reliquia…"
				/>
				<span class="kbd">esc</span>
			</div>
			<div class="oracle-results">
				{#if results.length === 0}
					<div style="padding: 26px 16px; text-align: center; color: var(--muted)">
						El oráculo no halla nada con ese nombre…
					</div>
				{/if}
				{#each results as r, i (meta(r).title + i)}
					{@const m = meta(r)}
					<div
						class="ores cursor-star"
						class:sel={i === sel}
						role="option"
						aria-selected={i === sel}
						tabindex="-1"
						onmouseenter={() => (sel = i)}
						onclick={() => choose(r)}
						onkeydown={(e) => e.key === 'Enter' && choose(r)}
					>
						<div class="oic">{m.glyph}</div>
						<div style="flex: 1; min-width: 0">
							<div class="otitle">{m.title}</div>
							<div class="osub">{m.sub}</div>
						</div>
						<Icon name="chevron" s={16} style="color: var(--faint)" />
					</div>
				{/each}
			</div>
			<div class="oracle-foot">
				<span><span class="kbd">↑</span> <span class="kbd">↓</span> navegar</span>
				<span><span class="kbd">↵</span> invocar</span>
				<span style="margin-left: auto" class="t-arcane">El oráculo medita…</span>
			</div>
		</div>
	</div>
{/if}
