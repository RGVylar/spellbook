<script lang="ts">
	import '$lib/styles/tokens.css';
	import '$lib/styles/components.css';

	import { api } from '$lib/api';
	import ArcanePlayer from '$lib/components/ArcanePlayer.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';
	import NavRail from '$lib/components/NavRail.svelte';
	import OracleSearch from '$lib/components/OracleSearch.svelte';
	import Topbar from '$lib/components/TopBar.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { moderation } from '$lib/stores/moderation.svelte';
	import { oracle } from '$lib/stores/oracle.svelte';
	import type { User } from '$lib/types';

	let { children } = $props();

	let booting = $state(true);

	$effect(() => {
		void (async () => {
			if (auth.token) {
				try {
					auth.setUser(await api.get<User>('/auth/me'));
					await moderation.refresh();
				} catch {
					/* token caducado: auth.logout ya aplicado por api */
				}
			}
			auth.loaded = true;
			try {
				await catalog.load();
			} finally {
				booting = false;
			}
		})();
	});

	function onKeydown(e: KeyboardEvent) {
		if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
			e.preventDefault();
			oracle.toggle();
		}
	}
</script>

<svelte:window onkeydown={onKeydown} />

<div class="sky"><div class="vignette"></div></div>

<div class="app">
	<NavRail />
	<main class="main">
		<Topbar />
		{#if booting}
			<div class="canvas" style="text-align: center; padding-top: 120px">
				<p class="t-arcane" style="font-size: 24px; color: var(--gold)">Consultando el grimorio…</p>
			</div>
		{:else}
			{@render children()}
		{/if}
	</main>
</div>

<ArcanePlayer />
<BottomNav />
<OracleSearch />
