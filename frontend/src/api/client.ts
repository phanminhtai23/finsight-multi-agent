// Thin REST client for the FinSight backend.
const BASE = "/api/v1";

export interface Health {
  status: string;
  app: string;
  environment: string;
  version: string;
}

export async function getHealth(): Promise<Health> {
  const res = await fetch(`${BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}
