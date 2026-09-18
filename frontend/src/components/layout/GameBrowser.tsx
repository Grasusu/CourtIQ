import { CalendarDays, ChevronRight } from "lucide-react";

import type { Game, GameDetail } from "../../types/api";

type GameBrowserProps = {
  games: Game[];
  selectedGameId: number | null;
  gameDetail: GameDetail | null;
  isLoading: boolean;
  onSelectGame: (gameId: number) => void;
};

export function GameBrowser({ games, selectedGameId, gameDetail, isLoading, onSelectGame }: GameBrowserProps) {
  return (
    <section className="panel games-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Game log</p>
          <h2>Match details</h2>
        </div>
        <span className="status-pill">{games.length} games</span>
      </div>

      {games.length === 0 ? (
        <div className="empty-state">Upload box scores to build the game log.</div>
      ) : (
        <div className="games-layout">
          <div className="game-list">
            {games.map((game) => (
              <button
                className={selectedGameId === game.id ? "game-list-item selected" : "game-list-item"}
                type="button"
                key={game.id}
                onClick={() => onSelectGame(game.id)}
              >
                <CalendarDays size={17} />
                <span>
                  <strong>{game.opponent}</strong>
                  <small>{formatDate(game.game_date)}</small>
                </span>
                <ChevronRight size={17} />
              </button>
            ))}
          </div>

          <div className="game-detail">
            {isLoading || !gameDetail ? (
              <div className="empty-state">Loading game...</div>
            ) : (
              <>
                <div className="game-detail-heading">
                  <div>
                    <p className="eyebrow">{formatDate(gameDetail.game_date)}</p>
                    <h3>vs {gameDetail.opponent}</h3>
                  </div>
                  <strong className="game-score">{gameDetail.team_totals.points}</strong>
                </div>

                <div className="game-total-strip">
                  <GameTotal label="Rebounds" value={gameDetail.team_totals.rebounds} />
                  <GameTotal label="Assists" value={gameDetail.team_totals.assists} />
                  <GameTotal label="Turnovers" value={gameDetail.team_totals.turnovers} />
                  <GameTotal label="TS%" value={`${Math.round(gameDetail.team_totals.true_shooting_percentage * 100)}%`} />
                  <GameTotal label="eFG%" value={`${Math.round(gameDetail.team_totals.effective_field_goal_percentage * 100)}%`} />
                </div>

                <div className="table-wrap">
                  <table className="box-score-table">
                    <thead>
                      <tr>
                        <th>Player</th><th>MIN</th><th>PTS</th><th>REB</th><th>AST</th><th>STL</th><th>BLK</th><th>TO</th><th>FG</th><th>3PT</th><th>FT</th><th>TS%</th>
                      </tr>
                    </thead>
                    <tbody>
                      {gameDetail.player_stats.map((stat) => (
                        <tr key={stat.player_id}>
                          <td><strong>{stat.player_name}</strong></td>
                          <td>{stat.minutes}</td><td>{stat.points}</td><td>{stat.rebounds}</td><td>{stat.assists}</td>
                          <td>{stat.steals}</td><td>{stat.blocks}</td><td>{stat.turnovers}</td>
                          <td>{stat.fgm}/{stat.fga}</td><td>{stat.three_pm}/{stat.three_pa}</td><td>{stat.ftm}/{stat.fta}</td>
                          <td>{Math.round(stat.true_shooting_percentage * 100)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

function GameTotal({ label, value }: { label: string; value: string | number }) {
  return <div><span>{label}</span><strong>{value}</strong></div>;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(
    new Date(`${value}T00:00:00`)
  );
}
