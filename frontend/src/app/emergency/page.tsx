"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function EmergencyPage() {
  const router = useRouter();
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const fmt = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div className="flex flex-col min-h-full bg-red-600 text-white">
      <div className="flex items-center justify-center py-5 border-b border-red-500">
        <span className="w-2 h-2 bg-white rounded-full animate-pulse mr-2" />
        <h1 className="text-sm font-bold uppercase tracking-widest">Live Emergency</h1>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-5 gap-8">
        {/* Radar timer */}
        <div className="relative flex items-center justify-center w-48 h-48">
          <div className="absolute w-48 h-48 rounded-full bg-white/20 animate-ping" />
          <div className="absolute w-40 h-40 rounded-full bg-white/10 animate-ping" style={{ animationDelay: "0.5s" }} />
          <div className="relative z-10 bg-white text-red-600 rounded-full w-36 h-36 flex flex-col items-center justify-center shadow-2xl">
            <span className="text-xs font-bold uppercase tracking-wider text-red-400">Elapsed</span>
            <span className="text-4xl font-extrabold">{fmt(elapsed)}</span>
          </div>
        </div>

        {/* Status Card */}
        <div className="w-full bg-white rounded-2xl p-5 text-gray-800 shadow-xl">
          <h3 className="font-bold text-red-600 border-b border-gray-100 pb-2 mb-3">Broadcast Status</h3>
          {[
            { icon: "🔴", label: "Streaming Audio", sub: "Microphone live", color: "bg-red-100 text-red-600" },
            { icon: "📍", label: "Live Location", sub: "GPS tracking active", color: "bg-blue-100 text-blue-600" },
            { icon: "✅", label: "Contacts Notified (3)", sub: "SMS & Push sent", color: "bg-emerald-100 text-emerald-600" },
            { icon: "⏳", label: "Responder Connection", sub: "Waiting for responder…", color: "bg-yellow-100 text-yellow-600" },
          ].map((s) => (
            <div key={s.label} className="flex items-center gap-3 mb-3">
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-base ${s.color}`}>{s.icon}</div>
              <div>
                <p className="text-sm font-semibold text-gray-800">{s.label}</p>
                <p className="text-xs text-gray-400">{s.sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* End button */}
        <button
          onClick={() => router.push("/")}
          className="w-full bg-white/20 border border-white/30 text-white font-bold py-4 rounded-xl text-sm tracking-wide hover:bg-white/30 active:scale-95 transition-all"
        >
          SLIDE TO END EMERGENCY →
        </button>
      </div>
    </div>
  );
}
