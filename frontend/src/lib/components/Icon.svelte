<script lang="ts" module>
	/* Iconografía Tabler-ish del handoff (ornaments.jsx). solid = fill currentColor sin stroke */
	const ICONS: Record<string, { body: string; solid?: boolean }> = {
		oracle: { body: '<circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" /><path d="M11 8v6M8 11h6" />' },
		search: { body: '<circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" />' },
		grimoire: { body: '<path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H18a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1H6.5A1.5 1.5 0 0 1 5 18.5z" /><path d="M5 17.5A1.5 1.5 0 0 1 6.5 16H19" /><path d="M12 7l1 2 2 .3-1.4 1.4.3 2-1.9-1-1.9 1 .3-2L7 9.3 9 9z" />' },
		explore: { body: '<circle cx="12" cy="12" r="9" /><path d="M14.8 9.2l-1.6 4.4-4.4 1.6 1.6-4.4z" />' },
		grid: { body: '<rect x="4" y="4" width="7" height="7" rx="1.4" /><rect x="13" y="4" width="7" height="7" rx="1.4" /><rect x="4" y="13" width="7" height="7" rx="1.4" /><rect x="13" y="13" width="7" height="7" rx="1.4" />' },
		list: { body: '<path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01" />' },
		play: { body: '<path d="M7 5.5v13a1 1 0 0 0 1.5.87l11-6.5a1 1 0 0 0 0-1.74l-11-6.5A1 1 0 0 0 7 5.5z" />', solid: true },
		pause: { body: '<rect x="6.5" y="5" width="3.6" height="14" rx="1.2" /><rect x="13.9" y="5" width="3.6" height="14" rx="1.2" />', solid: true },
		next: { body: '<path d="M6 5.5v13a1 1 0 0 0 1.5.87L16 14v4.5a1 1 0 0 0 2 0v-13a1 1 0 0 0-2 0V10L7.5 4.63A1 1 0 0 0 6 5.5z" />', solid: true },
		prev: { body: '<path d="M18 5.5v13a1 1 0 0 1-1.5.87L8 14v4.5a1 1 0 0 1-2 0v-13a1 1 0 0 1 2 0V10l8.5-5.37A1 1 0 0 1 18 5.5z" />', solid: true },
		invoke: { body: '<path d="M12 4v16M4 12h16" />' },
		scroll: { body: '<path d="M8 4h9a2 2 0 0 1 2 2v1H9" /><path d="M6 4a2 2 0 0 0-2 2v0a2 2 0 0 0 2 2h1" /><path d="M9 7v11a2 2 0 0 1-2 2h10a2 2 0 0 0 2-2v-1H9" /><path d="M5 18a2 2 0 0 0 2 2" />' },
		relic: { body: '<path d="M12 3l2.2 4.6 5 .7-3.6 3.5.9 5L12 14.9 7.5 17l.9-5L4.8 8.3l5-.7z" />' },
		spell: { body: '<circle cx="7" cy="17" r="2.5" /><circle cx="18" cy="15" r="2.5" /><path d="M9.5 17V6l11-2v9" />' },
		vision: { body: '<rect x="3" y="6" width="13" height="12" rx="2" /><path d="M16 10l5-3v10l-5-3z" />' },
		school: { body: '<path d="M12 3l9 4-9 4-9-4z" /><path d="M5 9.5V14c0 1.5 3.1 3 7 3s7-1.5 7-3V9.5" />' },
		rune: { body: '<path d="M7 4h7l6 6v7a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3z" /><circle cx="8.5" cy="8.5" r="1.4" fill="currentColor" stroke-width="0" />' },
		link: { body: '<path d="M9 14a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1" /><path d="M15 10a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1" />' },
		edit: { body: '<path d="M4 20h4l10-10a2.1 2.1 0 0 0-3-3L5 17z" /><path d="M13.5 6.5l3 3" />' },
		close: { body: '<path d="M6 6l12 12M18 6L6 18" />' },
		check: { body: '<path d="M4 12.5l5 5L20 6.5" />' },
		chevron: { body: '<path d="M9 6l6 6-6 6" />' },
		wizard: { body: '<path d="M12 2L7 12h10z" /><path d="M5 12h14l-2 8H7z" /><circle cx="12" cy="9" r=".6" fill="currentColor" />' },
		clock: { body: '<circle cx="12" cy="12" r="8.5" /><path d="M12 7.5V12l3 2" />' },
		seal: { body: '<circle cx="12" cy="10" r="6" /><path d="M9 15.5L8 22l4-2 4 2-1-6.5" />' },
		quill: { body: '<path d="M4 20s2-7 8-12 8-5 8-5-1 6-5 9-9 5-9 5z" /><path d="M4 20l5-5" />' },
		sparkle: { body: '<path d="M12 3l1.6 5.4L19 10l-5.4 1.6L12 17l-1.6-5.4L5 10l5.4-1.6z" />' },
		key: { body: '<circle cx="8" cy="15" r="4" /><path d="M11 12l8-8M17 5l2 2M14 8l2 2" />' },
		user: { body: '<circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6" />' },
		logout: { body: '<path d="M14 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-2" /><path d="M9 12h12l-3-3M18 15l3-3" />' },
		variant: { body: '<circle cx="12" cy="5" r="2.5" /><circle cx="6" cy="18" r="2.5" /><circle cx="18" cy="18" r="2.5" /><path d="M12 7.5v3M12 10.5l-5 5M12 10.5l5 5" />' },
		upload: { body: '<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" /><path d="M12 15V3M8 7l4-4 4 4" />' },
		eye: { body: '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" /><circle cx="12" cy="12" r="3" />' },
		thumbup: { body: '<path d="M7 11V20H4a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1h3z" /><path d="M10 20h7.5a1.5 1.5 0 0 0 1.47-1.2l1-5A1.5 1.5 0 0 0 18.5 12H14V7a2 2 0 0 0-2-2h-.5a.5.5 0 0 0-.5.5V7l-1 4z" />' },
		thumbdown: { body: '<path d="M17 13V4H20a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1h-3z" /><path d="M14 4H6.5A1.5 1.5 0 0 0 5.03 5.2l-1 5A1.5 1.5 0 0 0 5.5 12H10v5a2 2 0 0 0 2 2h.5a.5.5 0 0 0 .5-.5V17l1-4z" />' }
	};

	export type IconName = keyof typeof ICONS;
</script>

<script lang="ts">
	let {
		name,
		s = 20,
		sw = 1.6,
		style = ''
	}: { name: string; s?: number; sw?: number; style?: string } = $props();

	const icon = $derived(ICONS[name] ?? ICONS.sparkle);
</script>

<svg
	class="ic"
	width={s}
	height={s}
	viewBox="0 0 24 24"
	fill={icon.solid ? 'currentColor' : 'none'}
	stroke="currentColor"
	stroke-width={icon.solid ? 0 : sw}
	stroke-linecap="round"
	stroke-linejoin="round"
	{style}
	aria-hidden="true"
>
	<!-- eslint-disable-next-line svelte/no-at-html-tags — catálogo estático local -->
	{@html icon.body}
</svg>
