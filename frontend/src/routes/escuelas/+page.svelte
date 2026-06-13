<script lang="ts">
	import SealRing from '$lib/components/SealRing.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
</script>

<svelte:head><title>Escuelas de magia · SPELLBOOK</title></svelte:head>

<div class="canvas">
	<SectionHead
		eyebrow="Las ocho disciplinas"
		title="Escuelas de magia"
		sub="Todo artefacto pertenece a una escuela. Cada sello circular guarda su dominio."
	/>
	<div class="schools">
		{#each catalog.schools as s (s.id)}
			<a class="school cursor-star" href="/escuelas/{s.id}" style="text-decoration: none">
				<div style="background: radial-gradient(circle, {s.hue}14, transparent 70%); border-radius: 50%">
					<SealRing glyph={s.glyph} hue={s.hue} />
				</div>
				<div class="sname" style="color: {s.hue}">{s.name}</div>
				<div class="sdesc">{s.desc}</div>
				<div class="scount">{s.count} artefacto{s.count !== 1 ? 's' : ''} sellado{s.count !== 1 ? 's' : ''}</div>
			</a>
		{/each}
	</div>
</div>
