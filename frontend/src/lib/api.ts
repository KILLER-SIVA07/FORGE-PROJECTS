const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export type LoginResponse = { access_token: string; token_type: string };

export async function login(email: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) throw new Error("Invalid credentials");
  return res.json();
}

export async function listEvents(token?: string) {
  const res = await fetch(`${API_BASE}/events`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    cache: "no-store"
  });
  if (!res.ok) throw new Error("Failed to fetch events");
  return res.json();
}
