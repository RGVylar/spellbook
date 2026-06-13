class OracleStore {
	open = $state(false);

	show() {
		this.open = true;
	}
	hide() {
		this.open = false;
	}
	toggle() {
		this.open = !this.open;
	}
}

export const oracle = new OracleStore();
