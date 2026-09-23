import { CalendarPlus, Check, X } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import type { ManualGamePayload, ManualPlayerGameStats, Player } from "../../types/api";

type ManualGameFormProps = {
  isOpen: boolean;
  players: Player[];
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (payload: ManualGamePayload) => Promise<void>;
};

type EditableStat = Exclude<keyof ManualPlayerGameStats, "player_id" | "points">;
type StatRow = Omit<ManualPlayerGameStats, "points"> & { included: boolean };

const statColumns: Array<{ key: EditableStat; label: string; max?: number }> = [
  { key: "minutes", label: "MIN", max: 80 },
  { key: "rebounds", label: "REB" },
  { key: "assists", label: "AST" },
  { key: "steals", label: "STL" },
  { key: "blocks", label: "BLK" },
  { key: "turnovers", label: "TO" },
  { key: "fgm", label: "FGM" },
  { key: "fga", label: "FGA" },
  { key: "three_pm", label: "3PM" },
  { key: "three_pa", label: "3PA" },
  { key: "ftm", label: "FTM" },
  { key: "fta", label: "FTA" }
];

export function ManualGameForm({
  isOpen,
  players,
  isSubmitting,
  onClose,
  onSubmit
}: ManualGameFormProps) {
  const [gameDate, setGameDate] = useState(todayValue());
  const [opponent, setOpponent] = useState("");
  const [rows, setRows] = useState<StatRow[]>(() => buildRows(players));

  useEffect(() => {
    if (!isOpen) return;
    setRows(buildRows(players));
  }, [isOpen, players]);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !isSubmitting) onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isSubmitting, onClose]);

  const selectedRows = useMemo(() => rows.filter((row) => row.included), [rows]);
  const teamPoints = selectedRows.reduce((total, row) => total + calculatePoints(row), 0);

  if (!isOpen) return null;

  function updateRow(playerId: number, key: EditableStat, value: number) {
    setRows((currentRows) => currentRows.map((row) => {
      if (row.player_id !== playerId) return row;

      const next = { ...row, [key]: Math.max(0, value || 0) };
      if (key === "fgm") {
        next.three_pm = Math.min(next.three_pm, next.fgm);
        next.fga = Math.max(next.fga, next.fgm);
      } else if (key === "fga") {
        next.fgm = Math.min(next.fgm, next.fga);
        next.three_pa = Math.min(next.three_pa, next.fga);
        next.three_pm = Math.min(next.three_pm, next.fgm, next.three_pa);
      } else if (key === "three_pm") {
        next.three_pm = Math.min(next.three_pm, next.fgm);
        next.three_pa = Math.max(next.three_pa, next.three_pm);
      } else if (key === "three_pa") {
        next.three_pa = Math.min(next.three_pa, next.fga);
        next.three_pm = Math.min(next.three_pm, next.three_pa);
      } else if (key === "ftm") {
        next.fta = Math.max(next.fta, next.ftm);
      } else if (key === "fta") {
        next.ftm = Math.min(next.ftm, next.fta);
      }
      return next;
    }));
  }

  function togglePlayer(playerId: number) {
    setRows((currentRows) => currentRows.map((row) => (
      row.player_id === playerId ? { ...row, included: !row.included } : row
    )));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const playerStats = selectedRows.map(({ included: _included, ...row }) => ({
      ...row,
      points: calculatePoints(row)
    }));

    try {
      await onSubmit({ game_date: gameDate, opponent: opponent.trim(), player_stats: playerStats });
      setOpponent("");
      setGameDate(todayValue());
      onClose();
    } catch {
      // The parent displays the API error while the form remains open for correction.
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="manual-game-dialog" role="dialog" aria-modal="true" aria-labelledby="manual-game-title">
        <header className="manual-game-header">
          <div>
            <p className="eyebrow">Direct data entry</p>
            <h2 id="manual-game-title">Add game manually</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose} disabled={isSubmitting} aria-label="Close manual game form">
            <X size={18} />
          </button>
        </header>

        <form className="manual-game-form" onSubmit={handleSubmit}>
          <div className="manual-game-meta">
            <label>
              <span>Game date</span>
              <input type="date" value={gameDate} onChange={(event) => setGameDate(event.target.value)} required />
            </label>
            <label>
              <span>Opponent</span>
              <input value={opponent} onChange={(event) => setOpponent(event.target.value)} placeholder="Opponent name" required />
            </label>
          </div>

          <div className="manual-entry-note">
            Select players who appeared in the game. Points are calculated automatically from FGM, 3PM, and FTM.
          </div>

          <div className="manual-stats-wrap">
            <table className="manual-stats-table">
              <thead>
                <tr>
                  <th>Player</th>
                  <th>PTS</th>
                  {statColumns.map((column) => <th key={column.key}>{column.label}</th>)}
                </tr>
              </thead>
              <tbody>
                {players.map((player) => {
                  const row = rows.find((candidate) => candidate.player_id === player.id);
                  if (!row) return null;
                  return (
                    <tr className={row.included ? "manual-player-row selected" : "manual-player-row"} key={player.id}>
                      <td>
                        <button className="manual-player-toggle" type="button" onClick={() => togglePlayer(player.id)} aria-pressed={row.included}>
                          <span className="choice-check">{row.included ? <Check size={14} /> : null}</span>
                          <span>{player.name}</span>
                        </button>
                      </td>
                      <td><strong className="calculated-points">{calculatePoints(row)}</strong></td>
                      {statColumns.map((column) => (
                        <td key={column.key}>
                          <input
                            aria-label={`${player.name} ${column.label}`}
                            type="number"
                            min="0"
                            max={column.max}
                            step={column.key === "minutes" ? "0.1" : "1"}
                            value={row[column.key]}
                            disabled={!row.included}
                            onChange={(event) => updateRow(player.id, column.key, Number(event.target.value))}
                          />
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <footer className="manual-game-footer">
            <div>
              <strong>{selectedRows.length} players</strong>
              <span>{teamPoints} calculated team points</span>
            </div>
            <div>
              <button className="ghost-button" type="button" onClick={onClose} disabled={isSubmitting}>Cancel</button>
              <button className="primary-button" type="submit" disabled={isSubmitting || !opponent.trim() || selectedRows.length === 0}>
                <CalendarPlus size={17} />
                {isSubmitting ? "Saving game" : "Save game"}
              </button>
            </div>
          </footer>
        </form>
      </section>
    </div>
  );
}

function buildRows(players: Player[]): StatRow[] {
  return players.map((player) => ({
    player_id: player.id,
    included: false,
    minutes: 0,
    rebounds: 0,
    assists: 0,
    steals: 0,
    blocks: 0,
    turnovers: 0,
    fgm: 0,
    fga: 0,
    three_pm: 0,
    three_pa: 0,
    ftm: 0,
    fta: 0
  }));
}

function calculatePoints(row: Pick<StatRow, "fgm" | "three_pm" | "ftm">): number {
  return 2 * (row.fgm - row.three_pm) + 3 * row.three_pm + row.ftm;
}

function todayValue(): string {
  const today = new Date();
  const timezoneOffset = today.getTimezoneOffset() * 60_000;
  return new Date(today.getTime() - timezoneOffset).toISOString().slice(0, 10);
}
