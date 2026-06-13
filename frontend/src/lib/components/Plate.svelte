<script lang="ts">
	import type { Artifact } from '$lib/types';

	let { art, big = false }: { art: Artifact; big?: boolean } = $props();
</script>

<div class="plate" class:big>
	<div class="frame"></div>
	<span class="glyph">{art.glyph}</span>
	<span class="seal-mark">{art.era}</span>
</div>
