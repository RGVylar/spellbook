<script lang="ts">
	let { s = 34 }: { s?: number } = $props();
</script>

<svg class="sigil" width={s} height={s} viewBox="0 0 48 48" fill="none" aria-hidden="true">
	<circle cx="24" cy="24" r="21" stroke="var(--gold)" stroke-width="1" opacity=".5" />
	<circle cx="24" cy="24" r="16.5" stroke="var(--gold-bright)" stroke-width="1.4" />
	<path
		d="M24 6l4.6 13.2L42 24l-13.4 4.8L24 42l-4.6-13.2L6 24l13.4-4.8z"
		stroke="var(--gold-bright)"
		stroke-width="1.2"
		fill="rgba(201,168,76,.10)"
		stroke-linejoin="round"
	/>
	<path d="M24 14l2.4 7.6L34 24l-7.6 2.4L24 34l-2.4-7.6L14 24l7.6-2.4z" fill="var(--gold-bright)" opacity=".9" />
	<circle cx="24" cy="24" r="2.4" fill="var(--void)" />
</svg>
