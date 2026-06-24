import type {
  DemoResetResult,
  DemoSeedResult,
  Player,
  PlayerAnalytics,
  Team,
  TeamAnalytics,
  UploadResult
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...options?.headers
    }
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message = errorBody?.detail ?? `Request failed with ${response.status}`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function listTeams(): Promise<Team[]> {
  return request<Team[]>("/teams");
}

export function createTeam(payload: { name: string; season?: string }): Promise<Team> {
  return request<Team>("/teams", {
    method: "POST",
    body: JSON.stringify({
      name: payload.name,
      season: payload.season || null
    })
  });
}

export function listPlayers(teamId: number): Promise<Player[]> {
  return request<Player[]>(`/teams/${teamId}/players`);
}

export function uploadBoxScore(teamId: number, file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  return request<UploadResult>(`/teams/${teamId}/uploads/box-score`, {
    method: "POST",
    body: formData
  });
}

export function getTeamAnalytics(teamId: number): Promise<TeamAnalytics> {
  return request<TeamAnalytics>(`/teams/${teamId}/analytics`);
}

export function getPlayerAnalytics(playerId: number): Promise<PlayerAnalytics> {
  return request<PlayerAnalytics>(`/players/${playerId}/analytics`);
}

export function seedDemoData(reset = false): Promise<DemoSeedResult> {
  return request<DemoSeedResult>(`/demo/seed?reset=${String(reset)}`, {
    method: "POST"
  });
}

export function resetDemoData(): Promise<DemoResetResult> {
  return request<DemoResetResult>("/demo/reset", {
    method: "DELETE"
  });
}

export { API_BASE_URL };
