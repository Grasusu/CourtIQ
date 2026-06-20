import type { TeamTrendPoint } from "../../types/api";

type TeamTrendChartProps = {
  trends: TeamTrendPoint[];
};

export function TeamTrendChart({ trends }: TeamTrendChartProps) {
  if (trends.length === 0) {
    return <div className="empty-state compact">No games recorded.</div>;
  }

  const width = 720;
  const height = 240;
  const padding = 34;
  const maxPoints = Math.max(...trends.map((trend) => trend.points), 1);
  const minPoints = Math.min(...trends.map((trend) => trend.points), 0);
  const range = Math.max(maxPoints - minPoints, 1);

  const points = trends.map((trend, index) => {
    const x = padding + (index / Math.max(trends.length - 1, 1)) * (width - padding * 2);
    const y = height - padding - ((trend.points - minPoints) / range) * (height - padding * 2);
    return { ...trend, x, y };
  });

  const path = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`)
    .join(" ");

  return (
    <div className="chart-shell" aria-label="Team scoring trend">
      <svg viewBox={`0 0 ${width} ${height}`} role="img">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} className="chart-axis" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} className="chart-axis" />
        <path d={path} className="chart-line" />
        {points.map((point) => (
          <g key={point.game_id}>
            <circle cx={point.x} cy={point.y} r="5" className="chart-dot" />
            <text x={point.x} y={point.y - 12} textAnchor="middle" className="chart-value">
              {point.points}
            </text>
          </g>
        ))}
      </svg>
      <div className="chart-label-row">
        {trends.map((trend) => (
          <span key={trend.game_id}>{trend.opponent}</span>
        ))}
      </div>
    </div>
  );
}
