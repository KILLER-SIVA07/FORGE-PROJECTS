export function KpiCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card">
      <div className="muted">{label}</div>
      <h2 style={{ marginBottom: 0 }}>{value}</h2>
    </div>
  );
}
