type RecentPointsBarsProps = {
  values: Array<number | null>;
};

export function RecentPointsBars({ values }: RecentPointsBarsProps) {
  const numericValues = values.filter((value): value is number => value !== null);
  const maxValue = Math.max(...numericValues, 1);

  if (values.length === 0) {
    return <div className="empty-state compact">No recent games.</div>;
  }

  return (
    <div className="mini-bars" aria-label="Recent scoring average">
      {values.map((value, index) => (
        <div className="mini-bar-slot" key={`${value}-${index}`}>
          <div className="mini-bar-track">
            <span
              className="mini-bar-fill"
              style={{ height: value === null ? 0 : `${Math.max((value / maxValue) * 100, 8)}%` }}
            />
          </div>
          <span className="mini-bar-label">{value === null ? "-" : value.toFixed(1)}</span>
        </div>
      ))}
    </div>
  );
}
