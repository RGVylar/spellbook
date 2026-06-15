<script lang="ts">
	import type { LineageNode } from '$lib/types';

	let { root }: { root: LineageNode } = $props();

	const ROW_H = 72;
	const NODE_R = 20;

	interface LayoutNode {
		node: LineageNode;
		x: number;
		y: number;
		parentX?: number;
		parentY?: number;
	}

	function countLeaves(n: LineageNode): number {
		if (n.children.length === 0) return 1;
		return n.children.reduce((s, c) => s + countLeaves(c), 0);
	}

	function layout(
		node: LineageNode,
		depth: number,
		left: number,
		right: number,
		parentX?: number,
		parentY?: number,
	): LayoutNode[] {
		const x = (left + right) / 2;
		const y = depth * ROW_H + NODE_R + 16;
		const result: LayoutNode[] = [{ node, x, y, parentX, parentY }];
		if (node.children.length === 0) return result;
		const totalLeaves = node.children.reduce((s, c) => s + countLeaves(c), 0);
		let cursor = left;
		for (const child of node.children) {
			const leaves = countLeaves(child);
			const childRight = cursor + (right - left) * (leaves / totalLeaves);
			result.push(...layout(child, depth + 1, cursor, childRight, x, y));
			cursor = childRight;
		}
		return result;
	}

	const ROLE_LABEL: Record<string, string> = {
		archimago: 'Archimago',
		mago: 'Mago',
		aprendiz: 'Aprendiz',
	};

	const computed = $derived((() => {
		const leaves = Math.max(countLeaves(root), 1);
		const W = Math.max(leaves * 64, 240);
		let d = 0;
		function walkDepth(n: LineageNode, level: number) {
			d = Math.max(d, level);
			n.children.forEach((c) => walkDepth(c, level + 1));
		}
		walkDepth(root, 0);
		const H = d * ROW_H + NODE_R * 2 + 40;
		return { items: layout(root, 0, 0, W), W, H };
	})());

	// Zoom / pan — operamos sobre coordenadas del viewBox
	let scale = $state(1);
	let tx = $state(0);
	let ty = $state(0);
	let dragging = $state(false);
	let dragStart = $state({ x: 0, y: 0, tx: 0, ty: 0 });

	const MIN_SCALE = 0.25;
	const MAX_SCALE = 4;

	let wrap: HTMLDivElement;

	// Centra el árbol horizontalmente al montar
	$effect(() => {
		if (wrap) {
			tx = wrap.clientWidth / 2 - (computed.W / 2) * scale;
		}
	});

	function onWheel(e: WheelEvent) {
		e.preventDefault();
		const factor = e.deltaY > 0 ? 0.85 : 1.18;
		const next = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale * factor));
		// Zoom hacia el cursor
		const rect = wrap.getBoundingClientRect();
		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;
		tx = mx - (mx - tx) * (next / scale);
		ty = my - (my - ty) * (next / scale);
		scale = next;
	}

	function onMouseDown(e: MouseEvent) {
		dragging = true;
		dragStart = { x: e.clientX, y: e.clientY, tx, ty };
	}

	function onMouseMove(e: MouseEvent) {
		if (!dragging) return;
		tx = dragStart.tx + (e.clientX - dragStart.x);
		ty = dragStart.ty + (e.clientY - dragStart.y);
	}

	function onMouseUp() { dragging = false; }

	function resetView() { scale = 1; tx = 0; ty = 0; }
</script>

{#if root.children.length === 0}
	<p class="muted" style="font-size: 12px; text-align: center; margin: 0">
		Sin adeptos invocados aún.
	</p>
{:else}
	<div
		class="tree-wrap"
		bind:this={wrap}
		role="img"
		aria-label="Árbol de estirpe"
		onwheel={onWheel}
		onmousedown={onMouseDown}
		onmousemove={onMouseMove}
		onmouseup={onMouseUp}
		onmouseleave={onMouseUp}
		style="cursor: {dragging ? 'grabbing' : 'grab'}"
	>
		<button class="reset-btn" onclick={resetView} title="Restablecer vista">⊙</button>

		<!-- SVG ocupa todo el contenedor; el <g> interno aplica zoom/pan -->
		<svg width="100%" height="100%">
			<defs>
				<radialGradient id="ng-root-lt">
					<stop offset="0" stop-color="#E6C868" />
					<stop offset="1" stop-color="#8A6D2A" />
				</radialGradient>
				<radialGradient id="ng-mago-lt">
					<stop offset="0" stop-color="#9B72CB" />
					<stop offset="1" stop-color="#6B3FA0" />
				</radialGradient>
				<radialGradient id="ng-aprendiz-lt">
					<stop offset="0" stop-color="#3a3050" />
					<stop offset="1" stop-color="#1c1525" />
				</radialGradient>
			</defs>

			<g transform="translate({tx} {ty}) scale({scale})">
				<!-- Líneas de linaje -->
				{#each computed.items as n}
					{#if n.parentX !== undefined && n.parentY !== undefined}
						{@const my = (n.y + n.parentY) / 2}
						<path
							d="M {n.parentX} {n.parentY} C {n.parentX} {my}, {n.x} {my}, {n.x} {n.y}"
							fill="none"
							stroke="rgba(201,168,76,0.28)"
							stroke-width="1"
							stroke-dasharray="3 5"
						/>
					{/if}
				{/each}

				<!-- Nodos -->
				{#each computed.items as n, i}
					{@const isRoot = i === 0}
					{@const fill = isRoot ? 'url(#ng-root-lt)' : n.node.role === 'mago' ? 'url(#ng-mago-lt)' : 'url(#ng-aprendiz-lt)'}
					{@const border = isRoot ? 'var(--gold-bright)' : n.node.role === 'mago' ? 'var(--purple-soft)' : 'rgba(201,168,76,0.3)'}
					<g>
						<circle cx={n.x} cy={n.y} r={NODE_R} fill={fill} stroke={border} stroke-width="1.2" />
						<text x={n.x} y={n.y + 6} text-anchor="middle" font-size="14" font-family="var(--font-arcane)" fill={isRoot ? '#1c1505' : 'var(--parchment)'}>{n.node.glyph}</text>
						<text x={n.x} y={n.y + NODE_R + 13} text-anchor="middle" font-size="8" font-family="var(--font-ui)" font-weight="600" letter-spacing="0.04em" fill="var(--gold)" opacity="0.85">{n.node.username.length > 12 ? n.node.username.slice(0, 11) + '…' : n.node.username}</text>
						<text x={n.x} y={n.y + NODE_R + 23} text-anchor="middle" font-size="6.5" font-family="var(--font-ui)" fill="var(--muted)" opacity="0.7">{ROLE_LABEL[n.node.role] ?? n.node.role}</text>
					</g>
				{/each}
			</g>
		</svg>
	</div>
{/if}

<style>
	.tree-wrap {
		position: relative;
		overflow: hidden;
		height: 220px;
		user-select: none;
	}

	.reset-btn {
		position: absolute;
		top: 6px;
		right: 6px;
		z-index: 1;
		background: rgba(201,168,76,0.1);
		border: 1px solid rgba(201,168,76,0.25);
		color: var(--gold);
		border-radius: 50%;
		width: 24px;
		height: 24px;
		font-size: 14px;
		cursor: pointer;
		display: grid;
		place-items: center;
		padding: 0;
		transition: background 0.15s;
	}
	.reset-btn:hover { background: rgba(201,168,76,0.22); }
</style>
