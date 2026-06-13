<script lang="ts">
	import Icon from '$lib/components/Icon.svelte';
	import Sigil from '$lib/components/Sigil.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { oracle } from '$lib/stores/oracle.svelte';
</script>

<div class="topbar">
	<a class="wordmark mobile-only" href="/" style="flex: 1; text-decoration: none">
		<Sigil s={26} /><span class="name" style="font-size: 18px">SPELLBOOK</span>
	</a>
	<div
		class="glass cursor-star"
		role="button"
		tabindex="0"
		onclick={() => oracle.show()}
		onkeydown={(e) => e.key === 'Enter' && oracle.show()}
		style="flex: 1; max-width: 520px; border-radius: var(--r-pill); padding: 9px 16px; display: flex; align-items: center; gap: 10px"
	>
		<Icon name="oracle" s={18} style="color: var(--gold-bright)" />
		<span style="flex: 1; color: var(--faint); font-size: 13.5px" class="mobile-hide-ph">
			El Oráculo · invoca cualquier cosa
		</span>
		<span class="kbd mobile-only-hide">⌘K</span>
	</div>
	<a class="btn ghost mobile-only cursor-star" style="padding: 8px" href="/auth" aria-label="Tu cuenta">
		<Icon name="wizard" s={20} style="color: {auth.user ? 'var(--gold-bright)' : 'var(--parchment-2)'}" />
	</a>
</div>
