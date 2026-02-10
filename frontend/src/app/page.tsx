import { Nav } from "../components/Nav";

export default function HomePage() {
  return (
    <main className="container">
      <Nav />
      <section className="card">
        <h1>Enterprise QR Visitor Management</h1>
        <p className="muted">
          Frontend starter with role-focused dashboards for Admin, Security, and Staff.
        </p>
      </section>
    </main>
  );
}
