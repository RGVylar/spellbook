/** Tiempo relativo en lengua arcana: "hace 3 lunas", "hace 1 era"… */
export function arcaneTime(iso: string): string {
	const then = new Date(iso).getTime();
	if (Number.isNaN(then)) return iso;
	const mins = Math.max(0, Math.floor((Date.now() - then) / 60000));
	if (mins < 2) return 'ahora mismo';
	if (mins < 60) return `hace ${mins} velas`;
	const hours = Math.floor(mins / 60);
	if (hours < 24) return `hace ${hours} hora${hours !== 1 ? 's' : ''}`;
	const days = Math.floor(hours / 24);
	if (days < 30) return `hace ${days} día${days !== 1 ? 's' : ''}`;
	const moons = Math.floor(days / 30);
	if (moons < 12) return `hace ${moons} luna${moons !== 1 ? 's' : ''}`;
	const eras = Math.floor(moons / 12);
	return `hace ${eras} era${eras !== 1 ? 's' : ''}`;
}

export function fmtTime(seconds: number): string {
	if (!Number.isFinite(seconds) || seconds <= 0) return '0:00';
	const m = Math.floor(seconds / 60);
	const s = Math.floor(seconds % 60);
	return `${m}:${String(s).padStart(2, '0')}`;
}

export function fmtNum(n: number): string {
	if (n >= 1_000_000) return `${+(n / 1_000_000).toFixed(1)}M`;
	if (n >= 1_000) return `${+(n / 1_000).toFixed(1)}k`;
	return String(n);
}

export function romanize(n: number): string {
	const table: [number, string][] = [
		[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'], [100, 'C'], [90, 'XC'],
		[50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']
	];
	let out = '';
	for (const [v, sym] of table) {
		while (n >= v) {
			out += sym;
			n -= v;
		}
	}
	return out || 'N';
}
