import { Activity, Database, RefreshCw, Upload, Users } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  API_BASE_URL,
  createTeam,
  getPlayerAnalytics,
  getTeamAnalytics,
  listPlayers,
  listTeams,
  uploadBoxScore
} from "./api/client";
import { TeamTrendChart } from "./components/charts/TeamTrendChart";
import { MetricCard } from "./components/layout/MetricCard";
import { PlayerAnalyticsPanel } from "./components/layout/PlayerAnalyticsPanel";
import { PlayerTable } from "./components/tables/PlayerTable";
import type { Player, PlayerAnalytics, Team, TeamAnalytics, UploadResult } from "./types/api";

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
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedTeam = useMemo(
    () => teams.find((team) => team.id === selectedTeamId) ?? null,
    [teams, selectedTeamId]
  );

  useEffect(() => {
    void loadTeams();
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
    setIsLoading(true);
    setError(null);
    try {
      const data = await listTeams();
      setTeams(data);
      setSelectedTeamId((currentTeamId) => currentTeamId ?? data[0]?.id ?? null);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsLoading(false);
    }
  }

  async function refreshDashboard(teamId = selectedTeamId) {
    if (teamId === null) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const [playersData, analyticsData] = await Promise.all([
        listPlayers(teamId),
        getTeamAnalytics(teamId)
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
    setError(null);
    try {
      const analytics = await getPlayerAnalytics(playerId);
      setPlayerAnalytics(analytics);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    }
  }

  async function handleCreateTeam(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!teamName.trim()) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const team = await createTeam({ name: teamName.trim(), season });
      setTeams((currentTeams) => [...currentTeams, team].sort((a, b) => a.name.localeCompare(b.name)));
      setSelectedTeamId(team.id);
      setTeamName("");
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile || selectedTeamId === null) {
      return;
    }

    setIsUploading(true);
    setError(null);
    try {
      const result = await uploadBoxScore(selectedTeamId, selectedFile);
      setUploadResult(result);
      setSelectedFile(null);
      await refreshDashboard(selectedTeamId);
    } catch (caughtError) {
      setError(toErrorMessage(caughtError));
    } finally {
      setIsUploading(false);
    }
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
    </main>
  );
}

function toErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong";
}

export default App;
