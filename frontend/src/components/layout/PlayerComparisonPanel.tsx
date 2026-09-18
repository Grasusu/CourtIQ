import { Check, GitCompareArrows } from "lucide-react";

import type { Player, PlayerAnalytics, PlayerComparison } from "../../types/api";

type PlayerComparisonPanelProps = {
  players: Player[];
  comparison: PlayerComparison | null;
  selectedPlayerIds: number[];
  isLoading: boolean;
  onTogglePlayer: (playerId: number) => void;
};

type ComparisonMetric = {
  label: string;
  value: (player: PlayerAnalytics) => number;
  format: (value: number) => string;
};

const metrics: ComparisonMetric[] = [
  { label: "Games", value: (player) => player.games_played, format: String },
  { label: "Points / game", value: (player) => player.average_points, format: formatDecimal },
  { label: "Rebounds / game", value: (player) => player.average_rebounds, format: formatDecimal },
  { label: "Assists / game", value: (player) => player.average_assists, format: formatDecimal },
  { label: "Points / minute", value: (player) => player.points_per_minute, format: formatDecimal },
  {
    label: "Assist / turnover",
    value: (player) => typeof player.assist_to_turnover_ratio === "string"
      ? Number.POSITIVE_INFINITY
      : player.assist_to_turnover_ratio,
    format: (value) => value === Number.POSITIVE_INFINITY ? "No turnovers" : formatDecimal(value)
  },
  { label: "True shooting", value: (player) => player.true_shooting_percentage, format: formatPercent },
  { label: "Effective FG", value: (player) => player.effective_field_goal_percentage, format: formatPercent },
  { label: "Consistency", value: (player) => player.consistency_score, format: formatPercent }
];

export function PlayerComparisonPanel({
  players,
  comparison,
  selectedPlayerIds,
  isLoading,
  onTogglePlayer
}: PlayerComparisonPanelProps) {
  return (
    <section className="panel comparison-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Head-to-head</p>
          <h2>Player comparison</h2>
        </div>
        <span className="status-pill">{selectedPlayerIds.length} selected</span>
      </div>

      <div className="player-selector" aria-label="Select two to four players">
        {players.map((player) => {
          const selected = selectedPlayerIds.includes(player.id);
          const disabled = !selected && selectedPlayerIds.length >= 4;
          return (
            <button
              className={selected ? "player-choice selected" : "player-choice"}
              type="button"
              key={player.id}
              onClick={() => onTogglePlayer(player.id)}
              disabled={disabled}
              aria-pressed={selected}
            >
              <span className="choice-check">{selected ? <Check size={15} /> : null}</span>
              <span>
                <strong>{player.name}</strong>
                <small>{player.position ?? "Position not set"}</small>
              </span>
            </button>
          );
        })}
      </div>

      {players.length < 2 ? (
        <div className="empty-state">Add or upload at least two players to compare performance.</div>
      ) : selectedPlayerIds.length < 2 ? (
        <div className="empty-state">Select at least two players.</div>
      ) : isLoading || !comparison ? (
        <div className="empty-state">Loading comparison...</div>
      ) : (
        <>
          <div className="comparison-table-wrap">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  {comparison.players.map((player) => <th key={player.player_id}>{player.player_name}</th>)}
                </tr>
              </thead>
              <tbody>
                {metrics.map((metric) => {
                  const values = comparison.players.map(metric.value);
                  const best = Math.max(...values);
                  return (
                    <tr key={metric.label}>
                      <th>{metric.label}</th>
                      {comparison.players.map((player, index) => (
                        <td className={values[index] === best ? "metric-leader" : ""} key={player.player_id}>
                          {metric.format(values[index])}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="comparison-summaries">
            {comparison.players.map((player) => (
              <div key={player.player_id}>
                <GitCompareArrows size={17} />
                <p><strong>{player.player_name}</strong> {player.summary}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}

function formatDecimal(value: number) {
  return value.toFixed(2).replace(/\.00$/, "");
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}
