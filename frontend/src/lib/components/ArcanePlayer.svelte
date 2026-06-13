<script lang="ts">
	import { goto } from '$app/navigation';
	import { attachAnalyser, resume } from '$lib/audio';
	import Icon from '$lib/components/Icon.svelte';
	import Viz from '$lib/components/Viz.svelte';
	import { catalog } from '$lib/stores/catalog.svelte';
	import { player } from '$lib/stores/player.svelte';
	import { fmtTime } from '$lib/utils';

	let audioEl: HTMLAudioElement | undefined = $state();
	let barEl: HTMLDivElement | undefined = $state();
	let unavailable = $state(false);
	let volume = $state(1);

	const track = $derived(player.current);
	const school = $derived(track ? catalog.school(track.school) : undefined);
	const src = $derived(track ? (track.mediaUrl ?? `/api/media/${track.id}`) : '');
	const pct = $derived(player.duration > 0 ? (player.currentTime / player.duration) * 100 : 0);

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
	<div class="player">
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
		</div>
	</div>
{/if}
