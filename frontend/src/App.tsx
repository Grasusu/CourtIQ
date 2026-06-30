import { Activity, Database, LogOut, RefreshCw, RotateCcw, Sparkles, Upload, Users } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  API_BASE_URL,
  createTeam,
  getMe,
  getPlayerAnalytics,
  getTeamAnalytics,
  getUploadJob,
  listPlayers,
  listTeams,
  listUploadJobs,
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
import type { Player, PlayerAnalytics, Team, TeamAnalytics, UploadJob, UploadResult, User } from "./types/api";

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
  const [uploadJob, setUploadJob] = useState<UploadJob | null>(null);
  const [uploadJobs, setUploadJobs] = useState<UploadJob[]>([]);
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
      setUploadResult(null);
      setUploadJob(null);
      setUploadJobs([]);
      return;
    }

    setUploadResult(null);
    setUploadJob(null);
    setUploadJobs([]);
    void refreshDashboard(selectedTeamId);
    void loadUploadJobs(selectedTeamId);
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

  async function loadUploadJobs(teamId = selectedTeamId) {
    if (teamId === null || !authToken) {
      return;
    }

    setError(null);
    try {
      const jobs = await listUploadJobs(teamId, authToken);
      setUploadJobs(jobs);
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
      const job = await uploadBoxScore(selectedTeamId, selectedFile, authToken);
      setUploadJob(job);
      upsertUploadJob(job);
      setUploadResult(null);
      setSelectedFile(null);
      setStatusMessage(`Upload job #${job.id} queued.`);

      const finishedJob = await waitForUploadJob(job.id);
      if (!finishedJob) {
        setStatusMessage(`Upload job #${job.id} is still processing.`);
        return;
      }

      if (finishedJob.status === "completed") {
        setUploadResult({
          team_id: finishedJob.team_id,
          rows_processed: finishedJob.rows_processed,
          games_created: finishedJob.games_created,
          players_created: finishedJob.players_created,
          stats_created: finishedJob.stats_created,
          stats_updated: finishedJob.stats_updated
        });
        setStatusMessage(`${finishedJob.rows_processed} rows imported.`);
        await refreshDashboard(selectedTeamId);
      } else {
        setError(finishedJob.error_message ?? "Upload failed.");
      }
      await loadUploadJobs(selectedTeamId);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsUploading(false);
    }
  }

  async function waitForUploadJob(jobId: number) {
    if (!authToken) {
      return null;
    }

    for (let attempt = 0; attempt < 20; attempt += 1) {
      const job = await getUploadJob(jobId, authToken);
      setUploadJob(job);
      upsertUploadJob(job);

      if (job.status === "completed" || job.status === "failed") {
        return job;
      }

      await sleep(700);
    }

    return null;
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
      setUploadJob(null);
      setUploadJobs([]);
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
      setUploadJob(null);
      setUploadJobs([]);
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
    setUploadJob(null);
    setUploadJobs([]);
    setStatusMessage("Signed out.");
  }

  function upsertUploadJob(job: UploadJob) {
    setUploadJobs((currentJobs) => {
      const otherJobs = currentJobs.filter((currentJob) => currentJob.id !== job.id);
      return [job, ...otherJobs].slice(0, 8);
    });
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
            {uploadJob ? (
              <div className="upload-job">
                <div className="upload-job-heading">
                  <span className={`job-status ${uploadJob.status}`}>
                    <span className="status-dot" />
                    {formatJobStatus(uploadJob.status)}
                  </span>
                  <strong>{uploadJob.filename}</strong>
                  <small>Job #{uploadJob.id}</small>
                </div>
                <div className="upload-result">
                  <span>{uploadJob.rows_processed} rows</span>
                  <span>{uploadJob.players_created} players</span>
                  <span>{uploadJob.games_created} games</span>
                  <span>{uploadJob.stats_updated} updates</span>
                </div>
                {uploadJob.error_message ? <p className="job-error">{uploadJob.error_message}</p> : null}
              </div>
            ) : uploadResult ? (
              <div className="upload-result">
                <span>{uploadResult.rows_processed} rows</span>
                <span>{uploadResult.players_created} players</span>
                <span>{uploadResult.games_created} games</span>
              </div>
            ) : null}
            <div className="upload-history">
              <div className="upload-history-heading">
                <div>
                  <p className="eyebrow">Upload history</p>
                  <h3>Recent jobs</h3>
                </div>
                <button
                  className="icon-button"
                  type="button"
                  onClick={() => void loadUploadJobs()}
                  disabled={selectedTeamId === null}
                  aria-label="Refresh upload jobs"
                >
                  <RefreshCw size={16} />
                </button>
              </div>
              <div className="upload-history-list">
                {uploadJobs.slice(0, 5).map((job) => (
                  <button
                    className={uploadJob?.id === job.id ? "upload-history-item active" : "upload-history-item"}
                    key={job.id}
                    type="button"
                    onClick={() => setUploadJob(job)}
                  >
                    <span className={`job-status ${job.status}`}>
                      <span className="status-dot" />
                      {formatJobStatus(job.status)}
                    </span>
                    <span className="upload-history-name">{job.filename}</span>
                    <span className="upload-history-meta">
                      {job.rows_processed} rows - {formatJobTime(job.created_at)}
                    </span>
                  </button>
                ))}
                {uploadJobs.length === 0 ? <div className="empty-state compact">No upload jobs yet.</div> : null}
              </div>
            </div>
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

function sleep(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function formatJobStatus(status: string) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatJobTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

export default App;
