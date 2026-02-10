import { KpiCard } from "../../components/KpiCard";
import { Nav } from "../../components/Nav";

const metrics = [
  ["Checked-in Now", 182],
  ["Pending Approvals", 26],
  ["Peak Hour", "11:00 - 12:00"],
  ["No-show Rate", "12.4%"],
  ["Event Footfall", 2480],
  ["Overstays", 7]
] as const;

export default function AdminPage() {
  return (
    <main className="container">
      <Nav />
      <h1>Admin Dashboard</h1>
      <div className="grid grid-3">
        {metrics.map(([label, value]) => (
          <KpiCard key={label} label={label} value={value} />
        ))}
      </div>

      <section className="card" style={{ marginTop: "1rem" }}>
        <h3>Emergency Controls</h3>
        <p className="muted">Emergency lockdown disables new check-ins instantly.</p>
        <button className="btn btn-danger">Activate Lockdown</button>
      </section>
    </main>
  );
}
