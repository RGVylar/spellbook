<script lang="ts">
	import Icon from '$lib/components/Icon.svelte';
	import { TYPE_META, type ArtifactType } from '$lib/types';

	let { type, size = 13 }: { type: ArtifactType; size?: number } = $props();

	const ICON_BY_TYPE: Record<ArtifactType, string> = {
		pergamino: 'scroll',
		reliquia: 'relic',
		hechizo: 'spell',
		visión: 'vision'
	};
	const cls = $derived(type === 'visión' ? 'vision' : type);
</script>

<span class="badge {cls}"><Icon name={ICON_BY_TYPE[type] ?? 'relic'} s={size} /> {TYPE_META[type]?.label ?? type}</span>
