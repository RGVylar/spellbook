<script lang="ts">
	import { page } from '$app/state';
	import Icon from '$lib/components/Icon.svelte';
	import Sigil from '$lib/components/Sigil.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { moderation } from '$lib/stores/moderation.svelte';

	const NAV: { sect?: string; href?: string; label?: string; icon?: string }[] = [
		{ sect: 'El Grimorio' },
		{ href: '/', label: 'Grimorio', icon: 'grimoire' },
		{ href: '/explorar', label: 'Explorar', icon: 'explore' },
		{ href: '/hechizos', label: 'Hechizos', icon: 'spell' },
		{ href: '/escuelas', label: 'Escuelas', icon: 'school' },
		{ sect: 'El Rito' },
		{ href: '/invocar', label: 'Invocar', icon: 'invoke' }
	];

	const ROLE_LABEL: Record<string, string> = {
		archimago: 'Archimago',
		mago: 'Mago',
		aprendiz: 'Aprendiz'
	};
	const ROLE_SUB: Record<string, string> = {
		archimago: 'puede sellar',
		mago: 'sella y modera',
		aprendiz: 'propone al cónclave'
	};

	function isActive(href: string): boolean {
		const p = page.url.pathname;
		return href === '/' ? p === '/' : p.startsWith(href);
	}
</script>

<aside class="railL">
	<a class="wordmark" href="/" style="margin-bottom: 26px; text-decoration: none">
		<Sigil s={34} /><span class="name">SPELLBOOK</span>
	</a>
	<nav style="flex: 1">
		{#each NAV as n, i (i)}
			{#if n.sect}
				<div class="nav-sect">{n.sect}</div>
			{:else if n.href}
				<a class="navlink cursor-star" class:active={isActive(n.href)} href={n.href}>
					<Icon name={n.icon ?? 'sparkle'} s={19} />{n.label}
				</a>
			{/if}
		{/each}
		{#if auth.isModerator}
			<a class="navlink cursor-star" class:active={isActive('/moderar')} href="/moderar">
				<Icon name="seal" s={19} />Propuestas
				{#if moderation.pendingCount > 0}
					<span class="pending-badge">{moderation.pendingCount}</span>
				{/if}
			</a>
		{/if}
	</nav>
	<div style="margin-top: 16px">
		<hr class="hairline" style="margin: 0 0 14px" />
		<a class="navlink cursor-star" href="/auth" title={auth.user ? 'Tu cuenta' : 'Identifícate'}>
			<Icon name="wizard" s={19} style={auth.user ? 'color: var(--gold-bright)' : ''} />
			<div style="line-height: 1.2">
				<div style="font-size: 13.5px; color: {auth.user ? 'var(--gold-bright)' : 'var(--parchment-2)'}">
					{auth.user ? auth.user.username : 'Profano'}
				</div>
				<div style="font-size: 10.5px; color: var(--faint)">
					{#if auth.user}
						<span class:archimago={auth.user.role === 'archimago'}>{ROLE_LABEL[auth.user.role]}</span>
						· {ROLE_SUB[auth.user.role]}
					{:else}
						solo contempla
					{/if}
				</div>
			</div>
		</a>
	</div>
</aside>

<style>
	.pending-badge {
		margin-left: auto;
		min-width: 20px;
		height: 20px;
		padding: 0 6px;
		border-radius: 999px;
		display: grid;
		place-items: center;
		font-size: 11px;
		font-weight: 700;
		color: #221a07;
		background: linear-gradient(var(--gold-bright), var(--gold));
		box-shadow: 0 0 12px rgba(201, 168, 76, 0.5);
	}
</style>
