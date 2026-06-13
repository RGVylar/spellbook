<script lang="ts">
	import { goto } from '$app/navigation';
	import { attachAnalyser, resume } from '$lib/audio';
	import Icon from '$lib/components/Icon.svelte';
	import Viz from '$lib/components/Viz.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { player } from '$lib/stores/player.svelte';
	import { fmtTime } from '$lib/utils';
	import type { Artifact } from '$lib/types';

	let audioEl: HTMLAudioElement | undefined = $state();
	let barEl: HTMLDivElement | undefined = $state();
	let unavailable = $state(false);
	let volume = $state(1);
	let showQueue = $state(false);
	let cacofoniaOnly = $state(false);
	let savedQueue = $state<Artifact[]>([]);

	const track = $derived(player.current);
	const school = $derived(track ? catalog.school(track.school) : undefined);
	const src = $derived(track ? (track.mediaUrl ?? `/api/media/${track.id}`) : '');
	const pct = $derived(player.duration > 0 ? (player.currentTime / player.duration) * 100 : 0);

	const currentIdx = $derived(player.queue.findIndex((a) => a.id === track?.id));
	const upNext = $derived(
		currentIdx >= 0 ? player.queue.slice(currentIdx + 1) : player.queue
	);

	function toggleCacofonia() {
		if (!cacofoniaOnly) {
			savedQueue = player.queue.slice();
			const source = player.queue.length > 0 ? player.queue : catalog.playable;
			player.queue = source.filter((a) => a.school === 'cacofonia');
			cacofoniaOnly = true;
		} else {
			player.queue = savedQueue.length > 0 ? savedQueue : catalog.playable;
			savedQueue = [];
			cacofoniaOnly = false;
		}
	}

	function playFromQueue(art: Artifact) {
		player.play(art);
	}

	// Consume las peticiones play/pause del store sobre el <audio> real
	$effect(() => {
		const intent = player.intent;
		if (!intent || !audioEl) return;
		player.intent = null;
		if (intent.action === 'play') {
			unavailable = false;
			attachAnalyser(audioEl);
			resume();
			void audioEl.play().catch(() => {
				player.playing = false;
				unavailable = true;
			});
		} else {
			audioEl.pause();
		}
	});

	function step(dir: 1 | -1) {
		if (player.queue.length === 0) player.queue = catalog.playable;
		player.step(dir);
	}

	function seek(e: MouseEvent) {
		if (!audioEl || !barEl || player.duration <= 0) return;
		const r = barEl.getBoundingClientRect();
		audioEl.currentTime = ((e.clientX - r.left) / r.width) * player.duration;
	}

	function setVolume(e: Event) {
		volume = Number((e.target as HTMLInputElement).value);
		if (audioEl) audioEl.volume = volume;
	}
</script>

{#if track}
	<div class="player" style="position: relative">
		{#if showQueue}
			<div class="queue-panel popup">
				<div class="queue-header">
					<span class="queue-title">Cola de reproducción</span>
					<button
						class="btn ghost cursor-star cacofonia-btn"
						class:active={cacofoniaOnly}
						onclick={toggleCacofonia}
						title={cacofoniaOnly ? 'Mostrar todo' : 'Solo Cacofonía'}
					>
						♫ Cacofonía
					</button>
				</div>
				{#if upNext.length === 0}
					<div class="queue-empty">No hay más canciones en cola</div>
				{:else}
					<div class="queue-list">
						{#each upNext as art}
							{@const artSchool = catalog.school(art.school)}
							<button
								class="queue-item cursor-star"
								class:queue-current={art.id === track.id}
								onclick={() => playFromQueue(art)}
							>
								<span class="queue-glyph">{artSchool?.glyph ?? '♪'}</span>
								<span class="queue-info">
									<span class="queue-name">{art.title}</span>
									<span class="queue-school">{artSchool?.name ?? art.school}</span>
								</span>
							</button>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
		<audio
			bind:this={audioEl}
			{src}
			preload="metadata"
			loop={player.loop}
			onplay={() => (player.playing = true)}
			onpause={() => (player.playing = false)}
			onended={() => step(1)}
			ontimeupdate={() => (player.currentTime = audioEl?.currentTime ?? 0)}
			ondurationchange={() => (player.duration = audioEl?.duration ?? 0)}
			onerror={() => {
				player.playing = false;
				unavailable = true;
			}}
		></audio>
		<div
			class="pp cursor-star"
			role="button"
			tabindex="0"
			title={player.playing ? 'Silenciar' : 'Invocar sonido'}
			onclick={() => player.toggle()}
			onkeydown={(e) => e.key === 'Enter' && player.toggle()}
		>
			{#if player.playing}<Icon name="pause" s={20} />{:else}<Icon name="play" s={20} />{/if}
		</div>
		<div class="row gap-2" style="flex: 0 0 auto">
			<button class="btn ghost cursor-star" style="padding: 6px" onclick={() => step(-1)} aria-label="Anterior">
				<Icon name="prev" s={18} />
			</button>
			<button class="btn ghost cursor-star" style="padding: 6px" onclick={() => step(1)} aria-label="Siguiente">
				<Icon name="next" s={18} />
			</button>
		</div>
		<div
			class="pmeta cursor-star"
			role="button"
			tabindex="0"
			onclick={() => goto(`/artefacto/${track.id}`)}
			onkeydown={(e) => e.key === 'Enter' && goto(`/artefacto/${track.id}`)}
		>
			<div class="ptitle">{track.title}</div>
			<div class="psub">
				{#if unavailable}
					este artefacto aún no fue preservado…
				{:else}
					{school?.glyph} {school?.name} · sellado por {track.sealedBy}
				{/if}
			</div>
		</div>
		<Viz active={player.playing} />
		<div class="ptime">
			{#if player.duration > 0}{fmtTime(player.currentTime)} / {fmtTime(player.duration)}{:else if track.media === 'audio'}♾ loop{:else}visión{/if}
		</div>
		<div class="pbar" bind:this={barEl} onclick={seek} role="presentation">
			<i style="width: {pct}%"></i>
		</div>
		<div class="pcontrols">
			<button
				class="btn ghost cursor-star"
				style="padding: 6px; color: {player.loop ? 'var(--gold-bright)' : 'var(--muted)'}"
				onclick={() => (player.loop = !player.loop)}
				aria-label="Bucle"
				title={player.loop ? 'Bucle activo' : 'Bucle'}
			>
				<Icon name="loop" s={16} />
			</button>
			<button
				class="btn ghost cursor-star"
				style="padding: 6px; color: {player.shuffle ? 'var(--gold-bright)' : 'var(--muted)'}"
				onclick={() => (player.shuffle = !player.shuffle)}
				aria-label="Mix aleatorio"
				title={player.shuffle ? 'Mix activo' : 'Mix'}
			>
				<Icon name="shuffle" s={16} />
			</button>
			<Icon name="volume" s={14} style="color: var(--muted); flex: 0 0 auto" />
			<input class="pvol" type="range" min="0" max="1" step="0.05" value={volume} oninput={setVolume} aria-label="Volumen" />
			<button
				class="btn ghost cursor-star"
				style="padding: 6px; color: {showQueue ? 'var(--gold-bright)' : 'var(--muted)'}"
				onclick={() => (showQueue = !showQueue)}
				aria-label="Cola de reproducción"
				title="Cola de reproducción"
			>
				<Icon name="queue" s={16} />
			</button>
		</div>
	</div>
{/if}

<style>
	.queue-panel {
		position: absolute;
		bottom: calc(100% + 8px);
		right: 0;
		width: 320px;
		max-height: 400px;
		border-radius: var(--r-md);
		display: flex;
		flex-direction: column;
		z-index: 50;
		overflow: hidden;
	}

	.queue-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 14px 10px;
		border-bottom: 1px solid rgba(201, 168, 76, 0.15);
		flex: 0 0 auto;
	}

	.queue-title {
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--muted);
	}

	.cacofonia-btn {
		font-size: 11px;
		padding: 3px 8px;
		border-radius: 20px;
		border: 1px solid rgba(201, 168, 76, 0.3);
		color: var(--muted);
		transition: all 0.15s;
	}

	.cacofonia-btn.active {
		color: var(--gold-bright);
		border-color: var(--gold-bright);
		background: rgba(201, 168, 76, 0.12);
	}

	.queue-list {
		overflow-y: auto;
		flex: 1;
		padding: 6px;
	}

	.queue-empty {
		padding: 24px 16px;
		text-align: center;
		font-size: 12px;
		color: var(--muted);
	}

	.queue-item {
		display: flex;
		align-items: center;
		gap: 10px;
		width: 100%;
		padding: 7px 10px;
		border-radius: var(--r-sm);
		background: none;
		border: none;
		text-align: left;
		cursor: pointer;
		transition: background 0.12s;
	}

	.queue-item:hover {
		background: rgba(255, 255, 255, 0.06);
	}

	.queue-glyph {
		font-size: 16px;
		flex: 0 0 auto;
		width: 22px;
		text-align: center;
	}

	.queue-info {
		display: flex;
		flex-direction: column;
		gap: 1px;
		min-width: 0;
	}

	.queue-name {
		font-size: 12.5px;
		color: var(--fg);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.queue-school {
		font-size: 10.5px;
		color: var(--muted);
	}
</style>
