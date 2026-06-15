<script lang="ts">
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import ArcaneRadar from '$lib/components/ArcaneRadar.svelte';
	import Icon from '$lib/components/Icon.svelte';
	import LineageTree from '$lib/components/LineageTree.svelte';
	import MiniCard from '$lib/components/MiniCard.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { moderation } from '$lib/stores/moderation.svelte';
	import type { Invite, LineageNode, UserProfile } from '$lib/types';
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

	let lineage = $state<LineageNode | null>(null);

	const isOwn = $derived(auth.user?.username === username);

	$effect(() => {
		const u = username;
		loading = true;
		notFound = false;
		profile = null;
		lineage = null;
		void api
			.get<UserProfile>(`/users/${u}`)
			.then((p) => (profile = p))
			.catch(() => (notFound = true))
			.finally(() => (loading = false));
		void api
			.get<LineageNode>(`/users/${u}/lineage`)
			.then((l) => (lineage = l))
			.catch(() => {});
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

<div class="canvas">
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
		<div class="profile-layout">
			<!-- Sidebar -->
			<aside class="profile-sidebar">
				<!-- Identidad -->
				<div class="glass sidebar-card">
					<div class="avatar">{profile.glyph}</div>
					<h1 class="profile-name">{profile.username}</h1>
					<div class="eyebrow" class:archimago={profile.role === 'archimago'}>
						{ROLE_LABEL[profile.role]}
					</div>
					{#if profile.arcaneTitle}
						<div class="arcane-title">{profile.arcaneTitle}</div>
					{/if}
					<div style="margin-bottom: 18px"></div>

					<div class="profile-stats">
						<div class="pstat">
							<span class="pstat-n">{profile.artifactCount}</span>
							<span class="pstat-l">artefacto{profile.artifactCount !== 1 ? 's' : ''}</span>
						</div>
						{#if profile.adeptCount > 0}
							<div class="pstat">
								<span class="pstat-n">{profile.adeptCount}</span>
								<span class="pstat-l">adepto{profile.adeptCount !== 1 ? 's' : ''}</span>
							</div>
						{/if}
					</div>
					<div class="muted" style="font-size: 12px; margin-top: 10px">inscrito {arcaneTime(profile.createdAt)}</div>

					{#if isOwn}
						<div class="sidebar-actions">
							<a class="btn cursor-star" href="/auth" style="text-decoration: none; font-size: 12.5px; justify-content: center">
								<Icon name="wizard" s={14} /> Cuenta
							</a>
							<button class="btn cursor-star" style="font-size: 12.5px; border-color: var(--ember); color: var(--ember); justify-content: center" onclick={logout}>
								<Icon name="logout" s={14} /> Salir
							</button>
						</div>
					{/if}
				</div>

				<!-- Perfil arcano (radar) -->
				<div class="glass sidebar-card" style="padding: 20px 16px 16px">
					<div class="eyebrow" style="margin-bottom: 14px">Perfil arcano</div>
					<ArcaneRadar stats={profile.arcaneStats} />
				</div>

			</aside>

			<!-- Artefactos (centro) -->
			<main class="profile-main">
				<div class="eyebrow" style="margin-bottom: 14px">Sus obras en el grimorio</div>
				{#if profile.artifacts.length > 0}
					<div class="mini-grid">
						{#each profile.artifacts as art (art.id)}
							<MiniCard {art} />
						{/each}
					</div>
				{:else}
					<div class="glass" style="border-radius: var(--r-lg); padding: 40px; text-align: center; color: var(--muted)">
						El pergamino está en blanco.
					</div>
				{/if}
			</main>

			<!-- Estirpe (derecha) -->
			{#if lineage}
				<aside class="profile-lineage">
					<!-- Invitaciones (solo perfil propio + moderador) -->
					{#if isOwn && auth.isModerator}
						<div class="glass lineage-card" style="margin-bottom: 16px">
							<div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 14px">
								<span class="t-arcane" style="font-size: 16px">Invitaciones</span>
								<button class="btn cursor-star" style="font-size: 11px; padding: 5px 10px" onclick={createInvite}>
									<Icon name="key" s={13} /> Forjar
									{#if auth.user?.role !== 'archimago'} ({auth.user?.invitesLeft ?? 0}){/if}
								</button>
							</div>
							{#if inviteError}<p style="color: var(--ember); font-size: 12px; margin: 0 0 8px">{inviteError}</p>{/if}
							{#if invites.length === 0}
								<p class="muted" style="font-size: 12px; margin: 0">Sin invitaciones forjadas.</p>
							{/if}
							{#each invites as inv (inv.code)}
								<div style="padding: 8px 0; border-bottom: 1px dashed rgba(201,168,76,.1)">
									<div class="row" style="justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 3px">
										<code style="font-size: 12px; color: {inv.usedBy ? 'var(--faint)' : 'var(--gold-bright)'}; overflow: hidden; text-overflow: ellipsis">{inv.code}</code>
										{#if !inv.usedBy}
											<button
												class="btn cursor-star"
												style="font-size: 10px; padding: 3px 8px; flex-shrink: 0; border-color: {copied === inv.code ? 'var(--gold)' : 'rgba(201,168,76,.3)'}; color: {copied === inv.code ? 'var(--gold-bright)' : 'var(--muted)'}"
												onclick={() => shareInvite(inv.code)}
											>
												<Icon name={copied === inv.code ? 'check' : 'link'} s={11} />
												{copied === inv.code ? 'OK' : 'Link'}
											</button>
										{/if}
									</div>
									<div class="muted" style="font-size: 10.5px">
										{inv.usedBy ? `→ ${inv.usedBy}` : 'sin consumir'}
									</div>
								</div>
							{/each}
						</div>
					{/if}

					<div class="eyebrow" style="margin-bottom: 14px">Árbol de estirpe</div>
					<div class="glass" style="border-radius: var(--r-lg); padding: 20px">
						<LineageTree root={lineage} />
					</div>
				</aside>
			{/if}
		</div>
	{/if}
</div>

<style>
	.profile-layout {
		display: grid;
		grid-template-columns: 240px 1fr 220px;
		gap: 24px;
		align-items: start;
	}

	.profile-lineage {
		position: sticky;
		top: 24px;
	}

	.lineage-card {
		border-radius: var(--r-xl);
		padding: 18px 18px 14px;
	}

	.profile-sidebar {
		display: flex;
		flex-direction: column;
		gap: 16px;
		position: sticky;
		top: 24px;
	}

	.sidebar-card {
		border-radius: var(--r-xl);
		padding: 28px 22px 22px;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
	}

	.avatar {
		width: 80px;
		height: 80px;
		border-radius: 50%;
		display: grid;
		place-items: center;
		font-family: var(--font-arcane);
		font-size: 38px;
		color: var(--gold-bright);
		background: rgba(201, 168, 76, 0.08);
		border: 2px solid rgba(201, 168, 76, 0.4);
		box-shadow: 0 0 24px rgba(201, 168, 76, 0.15);
		margin-bottom: 14px;
	}

	.profile-name {
		font-family: var(--font-display);
		font-size: 20px;
		font-weight: 700;
		color: var(--parchment);
		margin: 0 0 6px;
		letter-spacing: 0.02em;
	}

	.profile-stats {
		display: flex;
		gap: 18px;
		justify-content: center;
		margin-top: 16px;
		padding-top: 16px;
		border-top: 1px dashed rgba(201, 168, 76, 0.15);
		width: 100%;
	}

	.pstat {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
	}

	.pstat-n {
		font-family: var(--font-display);
		font-size: 22px;
		font-weight: 700;
		color: var(--gold-bright);
		line-height: 1;
	}

	.pstat-l {
		font-size: 10px;
		color: var(--muted);
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	.sidebar-actions {
		display: flex;
		flex-direction: column;
		gap: 8px;
		width: 100%;
		margin-top: 20px;
		padding-top: 16px;
		border-top: 1px dashed rgba(201, 168, 76, 0.15);
	}

	.profile-main {
		min-width: 0;
	}

	.mini-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(155px, 1fr));
		gap: 14px;
	}

	@media (max-width: 1024px) {
		.profile-layout {
			grid-template-columns: 240px 1fr;
		}
		.profile-lineage {
			grid-column: 2;
			position: static;
		}
	}

	@media (max-width: 720px) {
		.profile-layout {
			grid-template-columns: 1fr;
		}
		.profile-lineage {
			grid-column: 1;
		}
		.profile-sidebar {
			position: static;
		}
		.sidebar-card {
			flex-direction: row;
			text-align: left;
			align-items: flex-start;
			gap: 16px;
			flex-wrap: wrap;
		}
		.avatar {
			width: 60px;
			height: 60px;
			font-size: 28px;
			margin-bottom: 0;
			flex-shrink: 0;
		}
		.profile-stats {
			justify-content: flex-start;
			margin-top: 10px;
			padding-top: 10px;
		}
	}
</style>
