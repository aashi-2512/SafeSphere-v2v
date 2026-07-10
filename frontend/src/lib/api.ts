const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface RouteData {
  safest_route: RouteInfo;
  quickest_route: RouteInfo;
  time_bucket: string;
}

export interface RouteInfo {
  path_coords: [number, number][];
  mean_risk: number;
  max_risk: number;
  unsafe_count?: number;
  unsafe_hex_count?: number;
  distance_m: number;
  duration_s: number;
  source?: string;
}

export const api = {
  async fetchSafeRoute(start: string, end: string, timeBucket: string): Promise<RouteData> {
    const res = await fetch(`${API_BASE}/safety/route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start, end, time_bucket: timeBucket }),
    });
    if (!res.ok) throw new Error(`API Error ${res.status}: ${await res.text()}`);
    return res.json();
  },

  async fetchHexagons() {
    const res = await fetch(`${API_BASE}/safety/hexagons`);
    if (!res.ok) throw new Error(`API Error ${res.status}`);
    return res.json();
  },

  async fetchSafetyScore(lat: number, lng: number) {
    const res = await fetch(`${API_BASE}/safety/score?lat=${lat}&lng=${lng}`);
    if (!res.ok) throw new Error(`API Error ${res.status}`);
    return res.json();
  },

  async triggerSOS(userId: string, lat: number, lng: number, phone: string) {
    const res = await fetch(`${API_BASE}/sos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, lat, lng, phone }),
    });
    if (!res.ok) throw new Error(`API Error ${res.status}`);
    return res.json();
  },

  async fetchActiveSessions() {
    const res = await fetch(`${API_BASE}/sessions`);
    if (!res.ok) throw new Error(`API Error ${res.status}`);
    return res.json();
  },

  async updateTranscript(sessionId: string, transcript: string) {
    const res = await fetch(`${API_BASE}/session/${sessionId}/transcript`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript }),
    });
    if (!res.ok) throw new Error(`API Error ${res.status}`);
    return res.json();
  },
};
