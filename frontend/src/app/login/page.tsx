"use client";

import { FormEvent, useState } from "react";
import { Nav } from "../../components/Nav";
import { login } from "../../lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("password123");
  const [message, setMessage] = useState("");

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const token = await login(email, password);
      localStorage.setItem("access_token", token.access_token);
      setMessage("Login successful. Token saved to localStorage.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <main className="container">
      <Nav />
      <div className="card" style={{ maxWidth: 500 }}>
        <h2>Login</h2>
        <form onSubmit={onSubmit}>
          <label>Email</label>
          <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
          <label>Password</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className="btn btn-primary" type="submit">
            Sign In
          </button>
        </form>
        {message && <p className="muted">{message}</p>}
      </div>
    </main>
  );
}
