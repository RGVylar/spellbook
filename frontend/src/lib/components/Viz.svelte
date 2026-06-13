<script lang="ts">
	import { getFrequencyData } from '$lib/audio';

	let { active = false, bars = 18 }: { active?: boolean; bars?: number } = $props();

	let el: HTMLDivElement | undefined = $state();

	$effect(() => {
		let raf = 0;
		const tick = (t: number) => {
			if (el) {
				const lv = active ? getFrequencyData() : null;
				const kids = el.children;
				for (let i = 0; i < kids.length; i++) {
					let h = 8;
					if (lv) {
						const v = lv[(i * 2) % lv.length] / 255;
						h = 8 + v * 92;
					} else {
						// idle: oleaje suave y estático
						h = 10 + Math.abs(Math.sin(i * 0.9 + t / 1600)) * 14;
					}
					(kids[i] as HTMLElement).style.height = h + '%';
					(kids[i] as HTMLElement).style.opacity = active ? '0.85' : '0.3';
				}
			}
			raf = requestAnimationFrame(tick);
		};
		raf = requestAnimationFrame(tick);
		return () => cancelAnimationFrame(raf);
	});
</script>

<div class="viz" bind:this={el}>
	{#each Array(bars) as _, i (i)}
		<i></i>
	{/each}
</div>
