<script lang="ts">
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import Icon from '$lib/components/Icon.svelte';
	import SectionHead from '$lib/components/SectionHead.svelte';
	import SpellCard from '$lib/components/SpellCard.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { moderation } from '$lib/stores/moderation.svelte';
	import type { Invite, UserProfile } from '$lib/types';
	import { arcaneTime } from '$lib/utils';

	const ROLE_LABEL: Record<string, string> = { archimago: 'Archimago', mago: 'Mago', aprendiz: 'Aprendiz' };

	let username = $derived(page.params.username);
	let profile = $state<UserProfile | null>(null);
	let notFound = $state(false);
	let loading = $state(true);

	let invites = $state<Invite[]>([]);
	let invitesLoaded = $state(false);
	let inviteError = $state('');
	let copied = $state('');

	const isOwn = $derived(auth.user?.username === username);

	$effect(() => {
		const u = username;
		loading = true;
		notFound = false;
		profile = null;
		void api
			.get<UserProfile>(`/users/${u}`)
			.then((p) => (profile = p))
			.catch(() => (notFound = true))
			.finally(() => (loading = false));
	});

	$effect(() => {
		if (isOwn && auth.isModerator && !invitesLoaded) {
			invitesLoaded = true;
			void api.get<Invite[]>('/invites').then((list) => (invites = list)).catch(() => {});
		}
	});

	async function createInvite() {
		inviteError = '';
		try {
			const inv = await api.post<Invite>('/invites');
			invites = [inv, ...invites];
			if (auth.user && auth.user.role !== 'archimago') {
				auth.user.invitesLeft = Math.max(0, auth.user.invitesLeft - 1);
			}
		} catch (e) {
			inviteError = e instanceof Error ? e.message : 'No fue posible forjar la invitación';
		}
	}

	function shareInvite(code: string) {
		const url = `${window.location.origin}/auth?invite=${code}`;
		navigator.clipboard.writeText(url).then(() => {
			copied = code;
			setTimeout(() => (copied = ''), 2000);
		});
	}

	function logout() {
		auth.logout();
		invites = [];
		invitesLoaded = false;
		moderation.pendingCount = 0;
	}
</script>

<svelte:head><title>{profile ? `${profile.username} · SPELLBOOK` : 'Mago · SPELLBOOK'}</title></svelte:head>

<div class="canvas" style="max-width: 900px">
	{#if loading}
		<p class="t-arcane" style="font-size: 22px; color: var(--gold); text-align: center; padding: 80px 0">
			El oráculo medita…
		</p>
	{:else if notFound}
		<div style="text-align: center; padding: 80px 0">
			<div style="font-size: 48px; margin-bottom: 16px">⁂</div>
			<h2 class="t-arcane" style="color: var(--gold-bright); margin: 0 0 8px">Mago desconocido</h2>
			<p class="muted">Ese nombre no figura en el registro del grimorio.</p>
		</div>
	{:else if profile}
		<!-- Cabecera del perfil -->
		<div class="glass" style="border-radius: var(--r-xl); padding: 32px; margin-bottom: 28px; display: flex; align-items: center; gap: 24px; flex-wrap: wrap">
			<div style="width: 72px; height: 72px; border-radius: 50%; display: grid; place-items: center; font-family: var(--font-arcane); font-size: 34px; color: var(--gold-bright); background: rgba(201,168,76,.1); border: 1px solid var(--glass-border-hi); flex: 0 0 auto">
				{profile.glyph}
			</div>
			<div style="flex: 1; min-width: 0">
				<h1 style="font-size: 26px; font-weight: 700; margin: 0 0 4px; color: var(--parchment)">{profile.username}</h1>
				<div class="row gap-2" style="flex-wrap: wrap; align-items: center">
					<span class="eyebrow" class:archimago={profile.role === 'archimago'}>{ROLE_LABEL[profile.role]}</span>
					<span class="dot"></span>
					<span class="muted" style="font-size: 12.5px">inscrito {arcaneTime(profile.createdAt)}</span>
					<span class="dot"></span>
					<span class="muted" style="font-size: 12.5px">{profile.artifactCount} artefacto{profile.artifactCount !== 1 ? 's' : ''}</span>
				</div>
			</div>
			{#if isOwn}
				<div class="row gap-2">
					<a class="btn cursor-star" href="/auth" style="font-size: 12px; padding: 7px 14px; text-decoration: none">
						<Icon name="wizard" s={14} /> Cuenta
					</a>
					<button class="btn cursor-star" style="font-size: 12px; padding: 7px 14px; border-color: var(--ember); color: var(--ember)" onclick={logout}>
						<Icon name="logout" s={14} /> Salir
					</button>
				</div>
			{/if}
		</div>

		<!-- Invitaciones (solo perfil propio, solo magos+) -->
		{#if isOwn && auth.isModerator}
			<div class="glass" style="border-radius: var(--r-xl); padding: 24px 28px; margin-bottom: 28px">
				<div class="row" style="justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 10px">
					<h3 class="t-arcane" style="font-size: 20px; margin: 0">Invitaciones forjadas</h3>
					<button class="btn cursor-star" onclick={createInvite}>
						<Icon name="key" s={15} /> Forjar nueva
						{#if auth.user?.role !== 'archimago'} ({auth.user?.invitesLeft ?? 0}){/if}
					</button>
				</div>
				{#if inviteError}<p style="color: var(--ember); font-size: 13px; margin: 0 0 10px">{inviteError}</p>{/if}
				{#if invites.length === 0}
					<p class="muted" style="font-size: 12.5px; margin: 0">Aún no has forjado ninguna invitación.</p>
				{/if}
				{#each invites as inv (inv.code)}
					<div class="row" style="justify-content: space-between; padding: 9px 0; border-bottom: 1px dashed rgba(201,168,76,.12); gap: 12px; flex-wrap: wrap">
						<code style="font-size: 13px; color: {inv.usedBy ? 'var(--faint)' : 'var(--gold-bright)'}">{inv.code}</code>
						<div class="row gap-3" style="align-items: center">
							<span class="muted" style="font-size: 11.5px">
								{inv.usedBy ? `consumida por ${inv.usedBy}` : 'sin consumir'}
							</span>
							{#if !inv.usedBy}
								<button
									class="btn cursor-star"
									style="font-size: 11px; padding: 4px 10px; border-color: {copied === inv.code ? 'var(--gold)' : 'rgba(201,168,76,.3)'}; color: {copied === inv.code ? 'var(--gold-bright)' : 'var(--muted)'}"
									onclick={() => shareInvite(inv.code)}
								>
									<Icon name={copied === inv.code ? 'check' : 'link'} s={12} />
									{copied === inv.code ? 'Copiado' : 'Compartir'}
								</button>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}

		<!-- Contribuciones -->
		<SectionHead
			eyebrow="Sus obras en el grimorio"
			title="Artefactos sellados"
			sub={profile.artifacts.length === 0 ? 'Este mago aún no ha inscrito conocimiento.' : ''}
		/>
		{#if profile.artifacts.length > 0}
			<div class="card-grid" style="margin-top: 20px">
				{#each profile.artifacts as art (art.id)}
					<SpellCard {art} />
				{/each}
			</div>
		{:else}
			<div class="glass" style="border-radius: var(--r-lg); padding: 32px; text-align: center; color: var(--muted); margin-top: 16px">
				El pergamino está en blanco.
			</div>
		{/if}
	{/if}
</div>
