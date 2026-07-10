"use client";

import dynamic from "next/dynamic";
import { useEffect, useState, useCallback } from "react";
import { RefreshCw, AlertTriangle, CheckCircle2, Users, Activity, MapPin, Wifi } from "lucide-react";

const SafetyMapView = dynamic(() => import("@/components/SafetyMapView"), { ssr: false });

interface Session {
  session_id: string;
  user_id: string;
  lat: number;
  lng: number;
  created_at: string;
  status?: string;
  transcript?: string;
}

export default function AdminDashboard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selected, setSelected] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [hexCount, setHexCount] = useState<number | null>(null);

  // MOCK DATA for Hackathon Demo
  const MOCK_SESSIONS: Session[] = [
    {
      session_id: "demo-session-9871",
      user_id: "Priya S.",
      lat: 19.119,
      lng: 72.847,
      created_at: new Date(Date.now() - 5 * 60000).toISOString(), // 5 mins ago
      transcript: "Suspicious person following on foot for 10 mins",
    },
    {
      session_id: "demo-session-9872",
      user_id: "Ananya K.",
      lat: 19.060,
      lng: 72.836,
      created_at: new Date(Date.now() - 15 * 60000).toISOString(), // 15 mins ago
      transcript: "Harassment near bus stop, help requested",
    }
  ];

  const fetchSessions = useCallback(() => {
    setLoading(true);
    setTimeout(() => {
      setSessions(MOCK_SESSIONS);
      setLoading(false);
      setLastRefresh(new Date());
    }, 400);
  }, []);

  // Load hex count (for stats)
  useEffect(() => {
    fetch("http://127.0.0.1:8000/safety/hexagons")
      .then((r) => r.json())
      .then((d) => setHexCount(d.total_hexagons))
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchSessions();
    const t = setInterval(fetchSessions, 10000); // Auto-refresh every 10s
    return () => clearInterval(t);
  }, [fetchSessions]);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Top Bar */}
      <header className="border-b border-gray-800 px-8 py-4 flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-emerald-500 rounded-lg flex items-center justify-center text-gray-900 font-bold">S²</div>
          <div>
            <h1 className="text-lg font-bold text-white">SafeSphere Admin</h1>
            <p className="text-xs text-gray-500">Real-time Emergency Response Dashboard</p>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-emerald-400 text-xs">
            <Wifi size={12} className="animate-pulse" />
            Live
          </div>
          <button onClick={fetchSessions} className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white bg-gray-800 px-3 py-1.5 rounded-lg transition-colors">
            <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
          <span className="text-xs text-gray-600" suppressHydrationWarning>Last: {lastRefresh.toLocaleTimeString()}</span>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="border-b border-gray-800 px-8 py-4 grid grid-cols-4 gap-6">
        {[
          { label: "Active SOS", value: sessions.length, icon: AlertTriangle, color: sessions.length > 0 ? "text-red-400" : "text-gray-500", bg: sessions.length > 0 ? "bg-red-950" : "bg-gray-900" },
          { label: "Hexagons Mapped", value: hexCount ?? "—", icon: Activity, color: "text-emerald-400", bg: "bg-emerald-950" },
          { label: "Active Users", value: "1", icon: Users, color: "text-blue-400", bg: "bg-blue-950" },
          { label: "Backend", value: "Online", icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-950" },
        ].map((stat) => (
          <div key={stat.label} className={`${stat.bg} rounded-xl p-4 flex items-center gap-3`}>
            <stat.icon size={20} className={stat.color} />
            <div>
              <div className={`text-xl font-bold ${stat.color}`}>{stat.value}</div>
              <div className="text-xs text-gray-500">{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-180px)]">
        {/* Left: Sessions Table */}
        <div className="w-96 border-r border-gray-800 flex flex-col">
          <div className="px-6 py-4 border-b border-gray-800">
            <h2 className="text-sm font-bold text-gray-300">Active SOS Sessions</h2>
          </div>
          <div className="flex-1 overflow-y-auto">
            {sessions.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-3 text-gray-600">
                <CheckCircle2 size={40} />
                <p className="text-sm">No active emergencies</p>
                <p className="text-xs">All clear</p>
              </div>
            ) : (
              sessions.map((s) => (
                <button key={s.session_id} onClick={() => setSelected(s)}
                  className={`w-full text-left px-6 py-4 border-b border-gray-800 hover:bg-gray-900 transition-colors ${selected?.session_id === s.session_id ? "bg-gray-900 border-l-2 border-l-red-500" : ""}`}>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 mt-1.5 bg-red-500 rounded-full animate-pulse shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-white truncate">User: {s.user_id}</span>
                        <span className="text-xs text-red-400 ml-2 shrink-0 font-bold">ACTIVE</span>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-gray-500 mt-0.5">
                        <MapPin size={10} />
                        {s.lat.toFixed(4)}, {s.lng.toFixed(4)}
                      </div>
                      <div className="text-xs text-gray-600 mt-0.5">
                        {new Date(s.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Right: Map + Detail */}
        <div className="flex-1 flex flex-col">
          {/* Map */}
          <div className="flex-1 relative">
            <SafetyMapView
              center={selected ? [selected.lat, selected.lng] : [19.0544, 72.8402]}
              zoom={selected ? 15 : 12}
              focusPoint={selected ? [selected.lat, selected.lng] : null}
            />
          </div>

          {/* Session Detail */}
          {selected && (
            <div className="border-t border-gray-800 bg-gray-900 px-6 py-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-white">Session Detail</h3>
                <button onClick={() => setSelected(null)} className="text-xs text-gray-500 hover:text-white">Close</button>
              </div>
              <div className="grid grid-cols-4 gap-4 text-xs">
                <div><div className="text-gray-500 mb-1">Session ID</div><div className="text-white font-mono truncate">{selected.session_id.slice(0, 12)}…</div></div>
                <div><div className="text-gray-500 mb-1">User ID</div><div className="text-white">{selected.user_id}</div></div>
                <div><div className="text-gray-500 mb-1">Latitude</div><div className="text-white">{selected.lat.toFixed(5)}</div></div>
                <div><div className="text-gray-500 mb-1">Longitude</div><div className="text-white">{selected.lng.toFixed(5)}</div></div>
              </div>
              {/* Voice Transcript Section */}
              <div className="mt-4 bg-gray-950 rounded-lg p-3 border border-gray-800">
                <div className="text-gray-500 text-[10px] uppercase font-bold tracking-wider mb-1">Live Audio Transcript</div>
                {selected.transcript ? (
                  <p className="text-sm text-red-400 italic">"{selected.transcript}"</p>
                ) : (
                  <p className="text-xs text-gray-600">No voice data received...</p>
                )}
              </div>
              <div className="mt-4 flex gap-2">
                <button className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors">
                  Mark Resolved
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors">
                  View Audio Stream
                </button>
                <button className="bg-red-800 hover:bg-red-700 text-white text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors">
                  Dispatch Responder
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
