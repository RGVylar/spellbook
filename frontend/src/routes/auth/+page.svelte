<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import Icon from '$lib/components/Icon.svelte';
	import SealButton from '$lib/components/SealButton.svelte';
	import Sigil from '$lib/components/Sigil.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { moderation } from '$lib/stores/moderation.svelte';
	import type { Invite, TokenResponse } from '$lib/types';
	import { arcaneTime } from '$lib/utils';

	const urlInvite = $derived(page.url.searchParams.get('invite') ?? '');

	let mode = $state<'login' | 'register'>('login');
	let username = $state('');
	let email = $state('');
	let password = $state('');
	let inviteCode = $state('');

	$effect(() => {
		if (urlInvite) {
			inviteCode = urlInvite;
			mode = 'register';
		}
	});
	let error = $state('');
	let submitting = $state(false);

	let invites = $state<Invite[]>([]);
	let invitesLoaded = $state(false);

	const ROLE_LABEL: Record<string, string> = { archimago: 'Archimago', mago: 'Mago', aprendiz: 'Aprendiz' };
	const ROLE_DESC: Record<string, string> = {
		archimago: 'Dominio absoluto del grimorio: sella, edita, modera y reparte invitaciones sin límite.',
		mago: 'Sella conocimiento directamente, modera propuestas de aprendices y reparte invitaciones.',
		aprendiz: 'Propone artefactos al cónclave y anota en los márgenes. El ascenso a mago llega con la edad y las obras.'
	};

	$effect(() => {
		if (auth.user && !invitesLoaded) {
			invitesLoaded = true;
			void api.get<Invite[]>('/invites').then((list) => (invites = list)).catch(() => {});
		}
	});

	async function submit() {
		if (submitting) return;
		submitting = true;
		error = '';
		try {
			const res =
				mode === 'login'
					? await api.post<TokenResponse>('/auth/login', { username, password })
					: await api.post<TokenResponse>('/auth/register', { username, email, password, inviteCode });
			auth.apply(res);
			await moderation.refresh();
			void goto('/');
		} catch (e) {
			error = e instanceof Error ? e.message : 'El rito falló';
		} finally {
			submitting = false;
		}
	}

	async function createInvite() {
		try {
			const inv = await api.post<Invite>('/invites');
			invites = [inv, ...invites];
			if (auth.user && auth.user.role !== 'archimago') {
				auth.user.invitesLeft = Math.max(0, auth.user.invitesLeft - 1);
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'No fue posible forjar la invitación';
		}
	}

	function logout() {
		auth.logout();
		invites = [];
		invitesLoaded = false;
		moderation.pendingCount = 0;
	}
</script>

<svelte:head><title>Identidad · SPELLBOOK</title></svelte:head>

<div class="canvas" style="max-width: 560px">
	<div style="text-align: center; margin-bottom: 26px">
		<div style="display: flex; justify-content: center; margin-bottom: 16px"><Sigil s={56} /></div>
		<h1 class="t-arcane" style="font-size: 38px; margin: 0; color: var(--gold-bright)">
			{auth.user ? 'Tu sello' : 'El umbral'}
		</h1>
	</div>

	{#if auth.user}
		<!-- Cuenta -->
		<div class="glass" style="border-radius: var(--r-xl); padding: 28px; margin-bottom: 20px">
			<div class="row gap-4" style="margin-bottom: 18px">
				<div
					style="width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center; font-family: var(--font-arcane); font-size: 30px; color: var(--gold-bright); background: rgba(201,168,76,.1); border: 1px solid var(--glass-border-hi)"
				>
					{auth.user.glyph}
				</div>
				<div>
					<div style="font-size: 20px; font-weight: 650">{auth.user.username}</div>
					<div class="eyebrow" style="margin-top: 4px" class:archimago={auth.user.role === 'archimago'}>{ROLE_LABEL[auth.user.role]}</div>
				</div>
			</div>
			<p class="muted" style="font-size: 13px; line-height: 1.6; margin: 0 0 8px">{ROLE_DESC[auth.user.role]}</p>
			<p class="muted" style="font-size: 12px; margin: 0">
				Inscrito {arcaneTime(auth.user.createdAt)} · {auth.user.email}
			</p>
		</div>

		<!-- Invitaciones -->
		{#if auth.user.role !== 'aprendiz'}
			<div class="glass" style="border-radius: var(--r-xl); padding: 24px 28px; margin-bottom: 20px">
				<div class="row" style="justify-content: space-between; margin-bottom: 14px">
					<h3 class="t-arcane" style="font-size: 20px; margin: 0">Invitaciones</h3>
					<button class="btn cursor-star" onclick={createInvite}>
						<Icon name="key" s={15} /> Forjar
						{#if auth.user.role !== 'archimago'}({auth.user.invitesLeft}){/if}
					</button>
				</div>
				{#if invites.length === 0}
					<p class="muted" style="font-size: 12.5px; margin: 0">Aún no has forjado ninguna invitación.</p>
				{/if}
				{#each invites as inv (inv.code)}
					<div
						class="row"
						style="justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed rgba(201,168,76,.12); gap: 10px"
					>
						<code style="font-size: 13px; color: {inv.usedBy ? 'var(--faint)' : 'var(--gold-bright)'}">{inv.code}</code>
						<span class="muted" style="font-size: 11.5px">
							{inv.usedBy ? `consumida por ${inv.usedBy}` : 'sin consumir'}
						</span>
					</div>
				{/each}
			</div>
		{:else}
			<div class="glass" style="border-radius: var(--r-lg); padding: 16px 20px; margin-bottom: 20px">
				<span class="muted" style="font-size: 12.5px">
					Los aprendices no reparten invitaciones. Al ascender a mago recibirás diez.
				</span>
			</div>
		{/if}

		{#if error}<p style="color: var(--ember); font-size: 13px">{error}</p>{/if}
		<button class="btn cursor-star" style="width: 100%" onclick={logout}>
			<Icon name="logout" s={16} /> Abandonar la sesión
		</button>
	{:else}
		<!-- Login / Registro -->
		<div class="seg" style="display: flex; margin-bottom: 22px">
			<button class="cursor-star" class:on={mode === 'login'} style="flex: 1; justify-content: center" onclick={() => (mode = 'login')}>
				Identifícate
			</button>
			<button class="cursor-star" class:on={mode === 'register'} style="flex: 1; justify-content: center" onclick={() => (mode = 'register')}>
				Iníciate
			</button>
		</div>

		<form
			class="glass"
			style="border-radius: var(--r-xl); padding: 28px"
			onsubmit={(e) => {
				e.preventDefault();
				void submit();
			}}
		>
			{#if mode === 'register'}
				<div class="field">
					<label for="a-invite">Código de invitación</label>
					<input id="a-invite" class="input" placeholder="Solo se entra por invitación" bind:value={inviteCode} />
					<div class="hint">Sin invitación no hay iniciación. Pídesela a un mago o al Archimago.</div>
				</div>
			{/if}
			<div class="field">
				<label for="a-user">{mode === 'login' ? 'Nombre o correo' : 'Nombre de iniciado'}</label>
				<input id="a-user" class="input" placeholder="p. ej. mordecai" bind:value={username} />
			</div>
			{#if mode === 'register'}
				<div class="field">
					<label for="a-email">Correo</label>
					<input id="a-email" class="input" type="email" placeholder="cuervo@mensajero.com" bind:value={email} />
				</div>
			{/if}
			<div class="field">
				<label for="a-pass">Palabra de paso</label>
				<input id="a-pass" class="input" type="password" placeholder="mínimo 8 caracteres" bind:value={password} />
			</div>
			{#if error}<p style="color: var(--ember); font-size: 13px; margin: 0 0 14px">{error}</p>{/if}
			<SealButton disabled={submitting} onclick={() => void submit()}>
				{mode === 'login' ? 'Cruzar el umbral' : 'Iniciarse'}
			</SealButton>
		</form>
	{/if}
</div>
