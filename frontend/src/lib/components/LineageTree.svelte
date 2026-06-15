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

	const nodes = $derived((() => {
		const leaves = Math.max(countLeaves(root), 1);
		const W = Math.max(leaves * 64, 240);
		return { items: layout(root, 0, 0, W), W };
	})());

	const depth = $derived((() => {
		let d = 0;
		function walk(n: LineageNode, level: number) {
			d = Math.max(d, level);
			n.children.forEach((c) => walk(c, level + 1));
		}
		walk(root, 0);
		return d;
	})());

	const H = $derived(depth * ROW_H + NODE_R * 2 + 40);
</script>

{#if root.children.length === 0 && depth === 0}
	<p class="muted" style="font-size: 12px; text-align: center; margin: 0">
		Sin adeptos invocados aún.
	</p>
{:else}
	<div class="tree-wrap">
		<svg viewBox="0 0 {nodes.W} {H}" width="100%" preserveAspectRatio="xMidYMid meet">
			<defs>
				<radialGradient id="ng-root">
					<stop offset="0" stop-color="#E6C868" />
					<stop offset="1" stop-color="#8A6D2A" />
				</radialGradient>
				<radialGradient id="ng-mago">
					<stop offset="0" stop-color="#9B72CB" />
					<stop offset="1" stop-color="#6B3FA0" />
				</radialGradient>
				<radialGradient id="ng-aprendiz">
					<stop offset="0" stop-color="#3a3050" />
					<stop offset="1" stop-color="#1c1525" />
				</radialGradient>
			</defs>

			<!-- Líneas de linaje -->
			{#each nodes.items as n}
				{#if n.parentX !== undefined && n.parentY !== undefined}
					{@const mx = (n.x + n.parentX) / 2}
					{@const my = (n.y + n.parentY) / 2}
					<path
						d="M {n.parentX} {n.parentY} C {n.parentX} {my}, {n.x} {my}, {n.x} {n.y}"
						fill="none"
						stroke="rgba(201,168,76,0.22)"
						stroke-width="1"
						stroke-dasharray="3 5"
					/>
				{/if}
			{/each}

			<!-- Nodos -->
			{#each nodes.items as n, i}
				{@const isRoot = i === 0}
				{@const fill = isRoot ? 'url(#ng-root)' : n.node.role === 'mago' ? 'url(#ng-mago)' : 'url(#ng-aprendiz)'}
				{@const border = isRoot ? 'var(--gold-bright)' : n.node.role === 'mago' ? 'var(--purple-soft)' : 'rgba(201,168,76,0.3)'}
				<g>
					<circle
						cx={n.x}
						cy={n.y}
						r={NODE_R}
						fill={fill}
						stroke={border}
						stroke-width="1.2"
					/>
					<text
						x={n.x}
						y={n.y + 6}
						text-anchor="middle"
						font-size="14"
						font-family="var(--font-arcane)"
						fill={isRoot ? '#1c1505' : 'var(--parchment)'}
					>{n.node.glyph}</text>
					<text
						x={n.x}
						y={n.y + NODE_R + 13}
						text-anchor="middle"
						font-size="8"
						font-family="var(--font-ui)"
						font-weight="600"
						letter-spacing="0.04em"
						fill="var(--gold)"
						opacity="0.85"
					>{n.node.username.length > 12 ? n.node.username.slice(0, 11) + '…' : n.node.username}</text>
					<text
						x={n.x}
						y={n.y + NODE_R + 23}
						text-anchor="middle"
						font-size="6.5"
						font-family="var(--font-ui)"
						fill="var(--muted)"
						opacity="0.7"
					>{ROLE_LABEL[n.node.role] ?? n.node.role}</text>
				</g>
			{/each}
		</svg>
	</div>
{/if}

<style>
	.tree-wrap {
		width: 100%;
		overflow-x: auto;
	}
</style>
