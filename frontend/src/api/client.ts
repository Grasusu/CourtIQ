import type {
  DemoResetResult,
  DemoSeedResult,
  Game,
  GameDetail,
  Player,
  PlayerAnalytics,
  PlayerComparison,
  Team,
  TeamAnalytics,
  TokenResponse,
  UploadJob
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const API_READY_WINDOW_MS = 10 * 60 * 1000;
const API_WAKE_RETRY_DELAYS_MS = [0, 1_500, 3_000, 5_000, 8_000];

let apiReadyUntil = 0;
let apiWakePromise: Promise<void> | null = null;

type RequestOptions = RequestInit & {
  authToken?: string | null;
};

async function request<T>(path: string, options?: RequestOptions): Promise<T> {
  await ensureApiReady();

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

async function ensureApiReady(): Promise<void> {
  if (Date.now() < apiReadyUntil) {
    return;
  }

  if (!apiWakePromise) {
    apiWakePromise = wakeApi().finally(() => {
      apiWakePromise = null;
    });
  }

  return apiWakePromise;
}

async function wakeApi(): Promise<void> {
  for (const delayMs of API_WAKE_RETRY_DELAYS_MS) {
    if (delayMs > 0) {
      await sleep(delayMs);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        headers: { Accept: "application/json" }
      });

      if (response.ok) {
        apiReadyUntil = Date.now() + API_READY_WINDOW_MS;
        return;
      }
    } catch {
      // A sleeping Render service can briefly reject cross-origin requests while starting.
    }
  }

  throw new Error("CourtIQ API is starting. Please try again in a few seconds.");
}

function sleep(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
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

export function createPlayer(
  teamId: number,
  payload: { name: string; position?: string; jersey_number?: number },
  authToken: string
): Promise<Player> {
  return request<Player>(`/teams/${teamId}/players`, {
    method: "POST",
    authToken,
    body: JSON.stringify({
      name: payload.name,
      position: payload.position || null,
      jersey_number: payload.jersey_number ?? null
    })
  });
}

export function uploadBoxScore(teamId: number, file: File, authToken: string): Promise<UploadJob> {
  const formData = new FormData();
  formData.append("file", file);

  return request<UploadJob>(`/teams/${teamId}/uploads/box-score`, {
    method: "POST",
    authToken,
    body: formData
  });
}

export function getUploadJob(jobId: number, authToken: string): Promise<UploadJob> {
  return request<UploadJob>(`/uploads/jobs/${jobId}`, { authToken });
}

export function listUploadJobs(teamId: number, authToken: string): Promise<UploadJob[]> {
  return request<UploadJob[]>(`/teams/${teamId}/uploads/jobs`, { authToken });
}

export function getTeamAnalytics(teamId: number, authToken: string): Promise<TeamAnalytics> {
  return request<TeamAnalytics>(`/teams/${teamId}/analytics`, { authToken });
}

export function getPlayerAnalytics(playerId: number, authToken: string): Promise<PlayerAnalytics> {
  return request<PlayerAnalytics>(`/players/${playerId}/analytics`, { authToken });
}

export function comparePlayers(teamId: number, playerIds: number[], authToken: string): Promise<PlayerComparison> {
  const query = new URLSearchParams();
  playerIds.forEach((playerId) => query.append("player_ids", String(playerId)));
  return request<PlayerComparison>(`/teams/${teamId}/player-comparison?${query.toString()}`, { authToken });
}

export function listGames(teamId: number, authToken: string): Promise<Game[]> {
  return request<Game[]>(`/teams/${teamId}/games`, { authToken });
}

export function getGame(gameId: number, authToken: string): Promise<GameDetail> {
  return request<GameDetail>(`/games/${gameId}`, { authToken });
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
