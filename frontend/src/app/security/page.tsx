"use client";

import { useState } from "react";
import { Nav } from "../../components/Nav";

export default function SecurityPage() {
  const [visitorId, setVisitorId] = useState("");

  return (
    <main className="container">
      <Nav />
      <h1>Security Gate Console</h1>
      <p className="muted">Offline-first friendly design with large buttons.</p>

      <div className="card" style={{ maxWidth: 600 }}>
        <label>Scan QR / Enter Visitor ID</label>
        <input
          className="input"
          value={visitorId}
          onChange={(e) => setVisitorId(e.target.value)}
          placeholder="VIS-2026-0001"
        />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: ".75rem" }}>
          <button className="btn btn-success big-action">✔ Check-In</button>
          <button className="btn btn-warning big-action">🚪 Check-Out</button>
          <button className="btn btn-danger big-action">❌ Reject</button>
        </div>
      </div>
    </main>
  );
}
