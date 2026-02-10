import Link from "next/link";

export function Nav() {
  return (
    <div className="card" style={{ marginBottom: "1rem" }}>
      <strong>QR Visitor Management</strong>
      <div style={{ display: "flex", gap: "1rem", marginTop: ".5rem", flexWrap: "wrap" }}>
        <Link href="/">Home</Link>
        <Link href="/admin">Admin</Link>
        <Link href="/security">Security</Link>
        <Link href="/staff">Staff</Link>
        <Link href="/login">Login</Link>
      </div>
    </div>
  );
}
