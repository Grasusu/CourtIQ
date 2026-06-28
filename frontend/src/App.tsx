import { Activity, Database, LogOut, RefreshCw, RotateCcw, Sparkles, Upload, Users } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  API_BASE_URL,
  createTeam,
  getMe,
  getPlayerAnalytics,
  getTeamAnalytics,
  listPlayers,
  listTeams,
  login,
  register,
  resetDemoData,
  seedDemoData,
  uploadBoxScore
} from "./api/client";
import { TeamTrendChart } from "./components/charts/TeamTrendChart";
import { MetricCard } from "./components/layout/MetricCard";
import { PlayerAnalyticsPanel } from "./components/layout/PlayerAnalyticsPanel";
import { PlayerTable } from "./components/tables/PlayerTable";
import type { Player, PlayerAnalytics, Team, TeamAnalytics, UploadResult, User } from "./types/api";

const TOKEN_STORAGE_KEY = "courtiq_access_token";

function App() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [teamAnalytics, setTeamAnalytics] = useState<TeamAnalytics | null>(null);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  const [playerAnalytics, setPlayerAnalytics] = useState<PlayerAnalytics | null>(null);
  const [teamName, setTeamName] = useState("");
  const [season, setSeason] = useState("2025-26");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("coach@example.com");
  const [password, setPassword] = useState("strong-password");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isDemoAction, setIsDemoAction] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const selectedTeam = useMemo(
    () => teams.find((team) => team.id === selectedTeamId) ?? null,
    [teams, selectedTeamId]
  );

  useEffect(() => {
    if (!authToken) {
      return;
    }

    void restoreSession(authToken);
  }, []);

  useEffect(() => {
    if (selectedTeamId === null) {
      setPlayers([]);
      setTeamAnalytics(null);
      setPlayerAnalytics(null);
      return;
    }

    void refreshDashboard(selectedTeamId);
  }, [selectedTeamId]);

  useEffect(() => {
    if (selectedPlayerId === null) {
      setPlayerAnalytics(null);
      return;
    }

    void loadPlayerAnalytics(selectedPlayerId);
  }, [selectedPlayerId]);

  async function loadTeams() {
    if (!authToken) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await listTeams(authToken);
      setTeams(data);
      setSelectedTeamId((currentTeamId) => {
        if (currentTeamId && data.some((team) => team.id === currentTeamId)) {
          return currentTeamId;
        }

        return data[0]?.id ?? null;
      });
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsLoading(false);
    }
  }

  async function refreshDashboard(teamId = selectedTeamId) {
    if (teamId === null || !authToken) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const [playersData, analyticsData] = await Promise.all([
        listPlayers(teamId, authToken),
        getTeamAnalytics(teamId, authToken)
      ]);

      setPlayers(playersData);
      setTeamAnalytics(analyticsData);
      setSelectedPlayerId((currentPlayerId) => {
        if (currentPlayerId && playersData.some((player) => player.id === currentPlayerId)) {
          return currentPlayerId;
        }

        return playersData[0]?.id ?? null;
      });
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadPlayerAnalytics(playerId: number) {
    if (!authToken) {
      return;
    }

    setError(null);
    try {
      const analytics = await getPlayerAnalytics(playerId, authToken);
      setPlayerAnalytics(analytics);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    }
  }

  async function handleCreateTeam(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!teamName.trim() || !authToken) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const team = await createTeam({ name: teamName.trim(), season }, authToken);
      setTeams((currentTeams) => [...currentTeams, team].sort((a, b) => a.name.localeCompare(b.name)));
      setSelectedTeamId(team.id);
      setTeamName("");
      setStatusMessage(`${team.name} created.`);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile || selectedTeamId === null || !authToken) {
      return;
    }

    setIsUploading(true);
    setError(null);
    try {
      const result = await uploadBoxScore(selectedTeamId, selectedFile, authToken);
      setUploadResult(result);
      setSelectedFile(null);
      setStatusMessage(`${result.rows_processed} rows imported.`);
      await refreshDashboard(selectedTeamId);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsUploading(false);
    }
  }

  async function handleSeedDemo(reset = false) {
    if (!authToken) {
      return;
    }

    setIsDemoAction(true);
    setError(null);
    try {
      const result = await seedDemoData(reset, authToken);
      const updatedTeams = await listTeams(authToken);
      setTeams(updatedTeams);
      setSelectedTeamId(result.team_id);
      setUploadResult(result.upload);
      setStatusMessage(
        `${result.team_name} ready: ${result.upload.rows_processed} rows, ${result.player_count} players.`
      );
      await refreshDashboard(result.team_id);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsDemoAction(false);
    }
  }

  async function handleResetDemo() {
    if (!authToken) {
      return;
    }

    setIsDemoAction(true);
    setError(null);
    try {
      const result = await resetDemoData(authToken);
      setUploadResult(null);
      setPlayerAnalytics(null);
      setStatusMessage(`${result.deleted_teams} demo team reset.`);
      const updatedTeams = await listTeams(authToken);
      setTeams(updatedTeams);
      setSelectedTeamId(updatedTeams[0]?.id ?? null);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsDemoAction(false);
    }
  }

  async function restoreSession(token: string) {
    setIsAuthLoading(true);
    setError(null);
    try {
      const user = await getMe(token);
      setCurrentUser(user);
      await loadTeamsWithToken(token);
    } catch {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      setAuthToken(null);
      setCurrentUser(null);
    } finally {
      setIsAuthLoading(false);
    }
  }

  async function loadTeamsWithToken(token: string) {
    const data = await listTeams(token);
    setTeams(data);
    setSelectedTeamId((currentTeamId) => {
      if (currentTeamId && data.some((team) => team.id === currentTeamId)) {
        return currentTeamId;
      }

      return data[0]?.id ?? null;
    });
  }

  async function handleAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsAuthLoading(true);
    setError(null);
    try {
      const response = authMode === "login"
        ? await login({ email, password })
        : await register({ email, password });

      localStorage.setItem(TOKEN_STORAGE_KEY, response.access_token);
      setAuthToken(response.access_token);
      setCurrentUser(response.user);
      setStatusMessage(`Signed in as ${response.user.email}.`);
      await loadTeamsWithToken(response.access_token);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsAuthLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setAuthToken(null);
    setCurrentUser(null);
    setTeams([]);
    setSelectedTeamId(null);
    setPlayers([]);
    setTeamAnalytics(null);
    setPlayerAnalytics(null);
    setUploadResult(null);
    setStatusMessage("Signed out.");
  }

  return (
    <main className="app-shell">
      <header className="top-bar">
        <div>
          <p className="eyebrow">CourtIQ</p>
          <h1>Basketball performance workspace</h1>
        </div>
        <div className="api-chip">
          <Database size={16} />
          <span>{API_BASE_URL}</span>
        </div>
      </header>

      {error ? <div className="alert">{error}</div> : null}
      {statusMessage ? <div className="success-banner">{statusMessage}</div> : null}

      {!currentUser ? (
        <section className="auth-shell panel">
          <div>
            <p className="eyebrow">Coach workspace</p>
            <h2>{authMode === "login" ? "Sign in to CourtIQ" : "Create your coach account"}</h2>
            <p className="auth-copy">
              Teams, uploads, and analytics are now tied to your account. Use the demo credentials or register a new coach.
            </p>
          </div>
          <form className="auth-form" onSubmit={handleAuth}>
            <label>
              <span>Email</span>
              <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
            </label>
            <label>
              <span>Password</span>
              <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" />
            </label>
            <button className="primary-button" type="submit" disabled={isAuthLoading}>
              {isAuthLoading ? "Working" : authMode === "login" ? "Sign in" : "Register"}
            </button>
            <button
              className="ghost-button"
              type="button"
              onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}
            >
              {authMode === "login" ? "Create account" : "Use existing account"}
            </button>
          </form>
        </section>
      ) : (
        <>
          <div className="session-bar">
            <span>{currentUser.email}</span>
            <button className="secondary-button" type="button" onClick={handleLogout}>
              <LogOut size={16} />
              Sign out
            </button>
          </div>

          <section className="workspace-grid">
        <aside className="panel sidebar-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Teams</p>
              <h2>Workspace</h2>
            </div>
            <button className="icon-button" type="button" onClick={() => void loadTeams()} aria-label="Refresh teams">
              <RefreshCw size={17} />
            </button>
          </div>

          <div className="team-list">
            {teams.map((team) => (
              <button
                className={team.id === selectedTeamId ? "team-button active" : "team-button"}
                key={team.id}
                type="button"
                onClick={() => setSelectedTeamId(team.id)}
              >
                <span>{team.name}</span>
                <small>{team.season ?? "No season"}</small>
              </button>
            ))}
            {teams.length === 0 ? <div className="empty-state compact">No teams yet.</div> : null}
          </div>

          <form className="stack-form" onSubmit={handleCreateTeam}>
            <label>
              <span>Team name</span>
              <input value={teamName} onChange={(event) => setTeamName(event.target.value)} placeholder="Amsterdam Lions" />
            </label>
            <label>
              <span>Season</span>
              <input value={season} onChange={(event) => setSeason(event.target.value)} placeholder="2025-26" />
            </label>
            <button className="primary-button" type="submit" disabled={isLoading || !teamName.trim()}>
              <Users size={17} />
              Create team
            </button>
          </form>

          <div className="demo-actions">
            <button className="secondary-button" type="button" onClick={() => void handleSeedDemo(false)} disabled={isDemoAction}>
              <Sparkles size={16} />
              Load demo
            </button>
            <button className="secondary-button" type="button" onClick={() => void handleSeedDemo(true)} disabled={isDemoAction}>
              <RefreshCw size={16} />
              Reload demo
            </button>
            <button className="ghost-button" type="button" onClick={() => void handleResetDemo()} disabled={isDemoAction}>
              <RotateCcw size={16} />
              Reset demo
            </button>
          </div>
        </aside>

        <section className="main-column">
          <div className="panel upload-panel">
            <div>
              <p className="eyebrow">Selected team</p>
              <h2>{selectedTeam?.name ?? "No team selected"}</h2>
            </div>
            <form className="upload-form" onSubmit={handleUpload}>
              <label className="file-input">
                <Upload size={18} />
                <span>{selectedFile?.name ?? "Choose CSV"}</span>
                <input
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                />
              </label>
              <button className="primary-button" type="submit" disabled={!selectedFile || selectedTeamId === null || isUploading}>
                <Upload size={17} />
                {isUploading ? "Uploading" : "Upload stats"}
              </button>
            </form>
            {uploadResult ? (
              <div className="upload-result">
                <span>{uploadResult.rows_processed} rows</span>
                <span>{uploadResult.players_created} players</span>
                <span>{uploadResult.games_created} games</span>
              </div>
            ) : null}
          </div>

          <section className="metric-grid">
            <MetricCard label="Games" value={teamAnalytics?.games_played ?? 0} icon={<Activity size={18} />} />
            <MetricCard label="Roster" value={teamAnalytics?.roster_size ?? 0} icon={<Users size={18} />} />
            <MetricCard label="Team PPG" value={teamAnalytics?.average_team_points ?? 0} detail="box score total" />
            <MetricCard
              label="Team TS%"
              value={teamAnalytics ? `${Math.round(teamAnalytics.true_shooting_percentage * 100)}%` : "0%"}
              detail="shot efficiency"
            />
          </section>

          <section className="panel chart-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Team trend</p>
                <h2>Scoring by game</h2>
              </div>
              <button
                className="secondary-button"
                type="button"
                onClick={() => void refreshDashboard()}
                disabled={isLoading || selectedTeamId === null}
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>
            <TeamTrendChart trends={teamAnalytics?.game_trends ?? []} />
          </section>
        </section>

        <aside className="right-column">
          <section className="panel roster-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Roster</p>
                <h2>Players</h2>
              </div>
              <span className="status-pill">{players.length}</span>
            </div>
            <PlayerTable
              players={players}
              teamAnalytics={teamAnalytics}
              selectedPlayerId={selectedPlayerId}
              onSelectPlayer={setSelectedPlayerId}
            />
          </section>
          <PlayerAnalyticsPanel analytics={playerAnalytics} />
        </aside>
          </section>
        </>
      )}
    </main>
  );
}

function toErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong";
}

export default App;
