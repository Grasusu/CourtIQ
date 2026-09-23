import { Award, BrainCircuit, Gauge, Lightbulb, LineChart, Radar, Target, TrendingDown, TrendingUp } from "lucide-react";

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

  const { forecast, impact_profile: impactProfile, recommendation, signals } = analytics.intelligence;
  const profileMetrics = [
    ["Scoring", impactProfile.scoring],
    ["Playmaking", impactProfile.playmaking],
    ["Rebounding", impactProfile.rebounding],
    ["Defense", impactProfile.defense],
    ["Efficiency", impactProfile.efficiency]
  ] as const;

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

      <section className="intelligence-brief">
        <div className="intelligence-heading">
          <div>
            <p className="eyebrow">Predictive analytics</p>
            <h3><BrainCircuit size={18} /> Intelligence brief</h3>
          </div>
          <span className={`confidence-badge ${forecast.confidence}`}>{forecast.confidence} confidence</span>
        </div>

        <div className="intelligence-layout">
          <div className="forecast-block">
            <span>Next-game scoring forecast</span>
            {forecast.projected_points === null ? (
              <strong className="forecast-pending">Need {Math.max(0, 3 - forecast.sample_size)} more games</strong>
            ) : (
              <>
                <strong>{forecast.projected_points}</strong>
                <small>{forecast.interval_low}-{forecast.interval_high} expected range</small>
                <div className={forecast.trend_per_game >= 0 ? "trend-direction positive" : "trend-direction negative"}>
                  {forecast.trend_per_game >= 0 ? <TrendingUp size={15} /> : <TrendingDown size={15} />}
                  {formatSigned(forecast.trend_per_game)} points per game
                </div>
              </>
            )}
            <p>{forecast.model_description}</p>
          </div>

          <div className="impact-profile">
            <div className="impact-profile-title">
              <Radar size={17} />
              <div><span>Team-relative role</span><strong>{impactProfile.archetype}</strong></div>
            </div>
            <div className="profile-bars">
              {profileMetrics.map(([label, value]) => (
                <div className="profile-row" key={label}>
                  <span>{label}</span>
                  <div className="profile-track"><i style={{ width: `${value}%` }} /></div>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="intelligence-signals">
          {signals.map((signal) => (
            <div className={`intelligence-signal ${signal.level}`} key={signal.title}>
              <span className="signal-indicator" />
              <div><strong>{signal.title}</strong><p>{signal.detail}</p></div>
            </div>
          ))}
        </div>

        <div className="coach-recommendation">
          <Lightbulb size={18} />
          <div><span>Coach recommendation</span><p>{recommendation}</p></div>
        </div>
      </section>

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

function formatSigned(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}`;
}
