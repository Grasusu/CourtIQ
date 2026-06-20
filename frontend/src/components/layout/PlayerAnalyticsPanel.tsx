import { Award, Gauge, LineChart, Target } from "lucide-react";

import { RecentPointsBars } from "../charts/RecentPointsBars";
import { MetricCard } from "./MetricCard";
import type { PlayerAnalytics } from "../../types/api";

type PlayerAnalyticsPanelProps = {
  analytics: PlayerAnalytics | null;
};

export function PlayerAnalyticsPanel({ analytics }: PlayerAnalyticsPanelProps) {
  if (!analytics) {
    return <div className="empty-state">Select a player.</div>;
  }

  return (
    <section className="panel player-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Player profile</p>
          <h2>{analytics.player_name}</h2>
        </div>
        <span className="status-pill">{analytics.games_played} games</span>
      </div>

      <div className="metric-grid compact-grid">
        <MetricCard label="PPG" value={analytics.average_points} icon={<Target size={18} />} />
        <MetricCard label="AST" value={analytics.average_assists} icon={<LineChart size={18} />} />
        <MetricCard label="TS%" value={`${Math.round(analytics.true_shooting_percentage * 100)}%`} icon={<Gauge size={18} />} />
        <MetricCard label="Consistency" value={`${Math.round(analytics.consistency_score * 100)}%`} icon={<Award size={18} />} />
      </div>

      <div className="summary-box">{analytics.summary}</div>

      <div className="split-detail">
        <div>
          <h3>Recent points</h3>
          <RecentPointsBars values={analytics.last_five_points} />
        </div>
        <div>
          <h3>Best game</h3>
          {analytics.best_game ? (
            <dl className="detail-list">
              <div>
                <dt>Opponent</dt>
                <dd>{analytics.best_game.opponent}</dd>
              </div>
              <div>
                <dt>Points</dt>
                <dd>{analytics.best_game.points}</dd>
              </div>
              <div>
                <dt>TS%</dt>
                <dd>{Math.round(analytics.best_game.true_shooting_percentage * 100)}%</dd>
              </div>
            </dl>
          ) : (
            <div className="empty-state compact">No games.</div>
          )}
        </div>
      </div>
    </section>
  );
}
