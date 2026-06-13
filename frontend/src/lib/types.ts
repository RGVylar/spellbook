export type ArtifactType = 'pergamino' | 'reliquia' | 'hechizo' | 'visión';
export type MediaKind = 'text' | 'image' | 'audio' | 'video';
export type ArtifactStatus = 'sellado' | 'pendiente' | 'rechazado';
export type Role = 'archimago' | 'mago' | 'aprendiz';

export interface Artifact {
	id: string;
	title: string;
	type: ArtifactType;
	school: string;
	era: number;
	glyph: string;
	media: MediaKind;
	runes: string[];
	sealedBy: string;
	origin: string;
	desc: string;
	links: string[];
	variantOf?: string | null;
	mediaUrl?: string | null;
	sourceUrl?: string | null;
	thumbnailUrl?: string | null;
	status: ArtifactStatus;
	createdAt?: string;
	views?: number;
	likes?: number;
	dislikes?: number;
	noteCount?: number;
	userReaction?: string | null;
}

export interface School {
	id: string;
	name: string;
	glyph: string;
	hue: string;
	desc: string;
	count: number;
}

export interface Spell {
	id: string;
	name: string;
	glyph: string;
	hue: string;
	desc: string;
	tracks: string[];
}

export interface UserProfile {
	username: string;
	role: Role;
	glyph: string;
	createdAt: string;
	artifactCount: number;
	adeptCount: number;
	artifacts: Artifact[];
}

export interface Note {
	id: number;
	who: string;
	glyph: string;
	when: string;
	text: string;
}

export interface User {
	id: number;
	username: string;
	email: string;
	role: Role;
	glyph: string;
	invitesLeft: number;
	createdAt: string;
}

export interface TokenResponse {
	accessToken: string;
	user: User;
}

export interface Invite {
	code: string;
	createdAt: string;
	usedBy: string | null;
	usedAt: string | null;
}

export interface Stats {
	artifacts: number;
	connections: number;
	schools: number;
	since: number;
}

export interface ArtifactDraft {
	title: string;
	type: ArtifactType | '';
	school: string;
	era: number | '';
	glyph?: string;
	media?: MediaKind;
	runes: string[];
	origin: string;
	desc: string;
	links: string[];
	variantOf?: string | null;
	sourceUrl?: string | null;
}

export const TYPE_META: Record<ArtifactType, { label: string; sub: string }> = {
	pergamino: { label: 'Pergamino', sub: 'texto · copypasta' },
	reliquia: { label: 'Reliquia', sub: 'imagen clásica' },
	hechizo: { label: 'Hechizo', sub: 'audio · música' },
	visión: { label: 'Visión', sub: 'vídeo en bucle' }
};

export const ARTIFACT_TYPES: ArtifactType[] = ['pergamino', 'reliquia', 'hechizo', 'visión'];
