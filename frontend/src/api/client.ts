import type {
  DemoResetResult,
  DemoSeedResult,
  Player,
  PlayerAnalytics,
  Team,
  TeamAnalytics,
  TokenResponse,
  UploadResult
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type RequestOptions = RequestInit & {
  authToken?: string | null;
};

async function request<T>(path: string, options?: RequestOptions): Promise<T> {
  const headers = new Headers(options?.headers);
  if (!(options?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (options?.authToken) {
    headers.set("Authorization", `Bearer ${options.authToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.detail ?? `Request failed with ${response.status}`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function register(payload: { email: string; password: string }): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function login(payload: { email: string; password: string }): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getMe(authToken: string): Promise<TokenResponse["user"]> {
  return request<TokenResponse["user"]>("/auth/me", { authToken });
}

export function listTeams(authToken: string): Promise<Team[]> {
  return request<Team[]>("/teams", { authToken });
}

export function createTeam(payload: { name: string; season?: string }, authToken: string): Promise<Team> {
  return request<Team>("/teams", {
    method: "POST",
    authToken,
    body: JSON.stringify({
      name: payload.name,
      season: payload.season || null
    })
  });
}

export function listPlayers(teamId: number, authToken: string): Promise<Player[]> {
  return request<Player[]>(`/teams/${teamId}/players`, { authToken });
}

export function uploadBoxScore(teamId: number, file: File, authToken: string): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  return request<UploadResult>(`/teams/${teamId}/uploads/box-score`, {
    method: "POST",
    authToken,
    body: formData
  });
}

export function getTeamAnalytics(teamId: number, authToken: string): Promise<TeamAnalytics> {
  return request<TeamAnalytics>(`/teams/${teamId}/analytics`, { authToken });
}

export function getPlayerAnalytics(playerId: number, authToken: string): Promise<PlayerAnalytics> {
  return request<PlayerAnalytics>(`/players/${playerId}/analytics`, { authToken });
}

export function seedDemoData(reset = false, authToken?: string | null): Promise<DemoSeedResult> {
  return request<DemoSeedResult>(`/demo/seed?reset=${String(reset)}`, {
    method: "POST",
    authToken
  });
}

export function resetDemoData(authToken?: string | null): Promise<DemoResetResult> {
  return request<DemoResetResult>("/demo/reset", {
    method: "DELETE",
    authToken
  });
}

export { API_BASE_URL };
