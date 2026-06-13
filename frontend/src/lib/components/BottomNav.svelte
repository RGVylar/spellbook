<script lang="ts">
	import { page } from '$app/state';
	import Icon from '$lib/components/Icon.svelte';
	import { oracle } from '$lib/stores/oracle.svelte';
	import { player } from '$lib/stores/player.svelte';

	function isActive(href: string): boolean {
		const p = page.url.pathname;
		return href === '/' ? p === '/' : p.startsWith(href);
	}
</script>

<nav class="botnav" class:with-player={player.current !== null}>
	<a class="cursor-star" class:active={isActive('/')} href="/">
		<Icon name="grimoire" s={22} /><span class="bl">Grimorio</span>
	</a>
	<a class="cursor-star" class:active={isActive('/explorar')} href="/explorar">
		<Icon name="explore" s={22} /><span class="bl">Explorar</span>
	</a>
	<a
		class="cursor-star"
		href="/"
		role="button"
		onclick={(e) => {
			e.preventDefault();
			oracle.show();
		}}
	>
		<Icon name="oracle" s={22} /><span class="bl">Oráculo</span>
	</a>
	<a class="cursor-star" class:active={isActive('/invocar')} href="/invocar">
		<Icon name="invoke" s={22} /><span class="bl">Invocar</span>
	</a>
</nav>
