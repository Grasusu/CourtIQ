import type { Player, TeamAnalytics } from "../../types/api";

type PlayerTableProps = {
  players: Player[];
  teamAnalytics: TeamAnalytics | null;
  selectedPlayerId: number | null;
  onSelectPlayer: (playerId: number) => void;
};

export function PlayerTable({ players, teamAnalytics, selectedPlayerId, onSelectPlayer }: PlayerTableProps) {
  const summaries = new Map(teamAnalytics?.top_scorers.map((summary) => [summary.player_id, summary]));

  if (players.length === 0) {
    return <div className="empty-state">No players loaded.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Player</th>
            <th>Position</th>
            <th>Games</th>
            <th>PPG</th>
            <th>TS%</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player) => {
            const summary = summaries.get(player.id);
            return (
              <tr
                key={player.id}
                className={selectedPlayerId === player.id ? "selected-row" : ""}
                onClick={() => onSelectPlayer(player.id)}
              >
                <td>
                  <button className="table-link" type="button">
                    {player.name}
                  </button>
                </td>
                <td>{player.position ?? "-"}</td>
                <td>{summary?.games_played ?? 0}</td>
                <td>{summary?.average_points ?? "-"}</td>
                <td>{summary ? `${Math.round(summary.true_shooting_percentage * 100)}%` : "-"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
