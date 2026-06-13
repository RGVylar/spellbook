/* Visualizador arcano: AnalyserNode sobre el <audio>/<video> activo del dock.
   Sin síntesis — el sonido sale del archivo real preservado. */

let ctx: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let freqData: Uint8Array<ArrayBuffer> | null = null;
let attachedEl: HTMLMediaElement | null = null;

export function attachAnalyser(el: HTMLMediaElement): void {
	if (attachedEl === el) {
		resume();
		return;
	}
	if (attachedEl !== null) return; // un MediaElementSource por elemento y contexto
	const Ctx = window.AudioContext ?? (window as never)['webkitAudioContext'];
	if (!Ctx) return;
	ctx = new Ctx();
	analyser = ctx.createAnalyser();
	analyser.fftSize = 64;
	freqData = new Uint8Array(analyser.frequencyBinCount);
	const source = ctx.createMediaElementSource(el);
	source.connect(analyser);
	analyser.connect(ctx.destination);
	attachedEl = el;
}

export function resume(): void {
	if (ctx?.state === 'suspended') void ctx.resume();
}

/** Niveles de frecuencia del audio activo, o null si no hay nada sonando. */
export function getFrequencyData(): Uint8Array<ArrayBuffer> | null {
	if (!analyser || !freqData) return null;
	analyser.getByteFrequencyData(freqData);
	return freqData;
}
