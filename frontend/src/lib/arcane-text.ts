/**
 * Acción Svelte: envuelve la palabra "archimago" (insensitive) con glow dorado.
 * Uso: <p use:arcaneText>{texto}</p>
 * También exporta `arcaneHtml(str)` para usar con {@html}.
 */

const RE = /archimago/gi;

export function arcaneHtml(text: string): string {
	return text.replace(RE, '<span class="archimago">$&</span>');
}

export function arcaneText(node: HTMLElement) {
	function apply() {
		node.childNodes.forEach((child) => {
			if (child.nodeType === Node.TEXT_NODE && child.textContent) {
				if (RE.test(child.textContent)) {
					RE.lastIndex = 0;
					const span = document.createElement('span');
					span.innerHTML = arcaneHtml(child.textContent);
					child.replaceWith(...Array.from(span.childNodes));
				}
			}
		});
		RE.lastIndex = 0;
	}
	apply();
}
