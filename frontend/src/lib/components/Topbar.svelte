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
	{#if auth.user}
		<a class="profile-pill cursor-star" href="/mago/{auth.user.username}" aria-label="Tu perfil">
			<span class="pglyph">{auth.user.glyph}</span>
			<span class="pname mobile-only-hide">{auth.user.username}</span>
		</a>
	{:else}
		<a class="btn ghost cursor-star" style="padding: 8px" href="/auth" aria-label="Identifícate">
			<Icon name="wizard" s={20} style="color: var(--parchment-2)" />
		</a>
	{/if}
</div>

<style>
	.profile-pill {
		display: flex;
		align-items: center;
		gap: 7px;
		padding: 5px 12px 5px 6px;
		border-radius: var(--r-pill);
		border: 1px solid var(--glass-border-hi);
		background: rgba(201, 168, 76, 0.06);
		text-decoration: none;
		transition: background 0.15s, border-color 0.15s;
		flex-shrink: 0;
	}
	.profile-pill:hover {
		background: rgba(201, 168, 76, 0.13);
		border-color: rgba(201, 168, 76, 0.4);
	}
	.pglyph {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		display: grid;
		place-items: center;
		font-family: var(--font-arcane);
		font-size: 15px;
		color: var(--gold-bright);
		background: rgba(201, 168, 76, 0.12);
	}
	.pname {
		font-size: 13px;
		font-weight: 600;
		color: var(--gold-bright);
	}
</style>
