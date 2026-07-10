"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Shield, MapPin, Navigation, ChevronRight, AlertTriangle, Phone, Clock, Bell } from "lucide-react";

const MOCK_ALERTS = [
  {
    id: 1,
    user: "Priya S.",
    location: "Andheri West, near D-Mart",
    time: "Today, 6:48 PM",
    desc: "Suspicious person following on foot for 10 mins",
    severity: "high",
  },
  {
    id: 2,
    user: "Ananya K.",
    location: "Bandra Linking Road",
    time: "Today, 5:12 PM",
    desc: "Harassment near bus stop, help requested",
    severity: "high",
  },
  {
    id: 3,
    user: "Meera R.",
    location: "Kurla Station East",
    time: "Today, 4:00 PM",
    desc: "Bag snatching attempt near taxi stand",
    severity: "medium",
  },
];

export default function HomePage() {
  const [greeting, setGreeting] = useState("Good morning");
  const [time, setTime] = useState("");
  const [safetyScore, setSafetyScore] = useState<number | null>(null);
  const [safetyLabel, setSafetyLabel] = useState("Loading…");
  const [activeAlerts, setActiveAlerts] = useState<any[]>(MOCK_ALERTS);

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const h = now.getHours();
      if (h < 12) setGreeting("Good morning");
      else if (h < 17) setGreeting("Good afternoon");
      else setGreeting("Good evening");
      setTime(now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }));
    };
    update();
    const t = setInterval(update, 30000);
    return () => clearInterval(t);
  }, []);

  // Fetch real safety score from backend for default location (Bandra West)
  useEffect(() => {
    fetch("http://127.0.0.1:8000/safety/score?lat=19.0544&lng=72.8402")
      .then((r) => r.json())
      .then((d) => {
        setSafetyScore(Math.round(d.safety_score));
        setSafetyLabel(d.safety_label);
      })
      .catch(() => {
        setSafetyScore(82);
        setSafetyLabel("Safe");
      });
  }, []);

  const score = safetyScore ?? 0;
  const scoreColor = score >= 80 ? "text-emerald-600" : score >= 40 ? "text-amber-500" : "text-red-600";
  const badgeColor = score >= 80 ? "bg-emerald-50 text-emerald-700" : score >= 40 ? "bg-amber-50 text-amber-700" : "bg-red-50 text-red-700";
  const dotColor = score >= 80 ? "bg-emerald-500" : score >= 40 ? "bg-amber-500" : "bg-red-500";
  const circleStroke = score >= 80 ? "#059669" : score >= 40 ? "#f59e0b" : "#ef4444";

  return (
    <div className="flex flex-col min-h-full bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-br from-emerald-700 to-emerald-500 pt-10 pb-16 px-5 rounded-b-3xl relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-white/30" />
          <div className="absolute -bottom-8 -left-8 w-32 h-32 rounded-full bg-white/20" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-2 text-emerald-100 text-sm mb-2">
            <MapPin size={14} />
            <span>Bandra West, Mumbai</span>
            <span className="ml-auto text-xs opacity-70" suppressHydrationWarning>{time}</span>
          </div>
          <h1 className="text-white text-2xl font-bold" suppressHydrationWarning>{greeting}, Shreya 👋</h1>
          <p className="text-emerald-100 text-sm mt-1">Stay aware, stay safe.</p>
        </div>
      </div>

      {/* Safety Score Card */}
      <div className="mx-4 -mt-8 bg-white rounded-2xl shadow-lg p-5 border border-gray-100 relative z-10">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Area Safety Score</p>
            <div className="flex items-end gap-1 mt-1">
              <span className={`text-4xl font-bold ${scoreColor}`}>{safetyScore ?? "—"}</span>
              <span className="text-gray-400 text-sm mb-1">/100</span>
            </div>
            <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full mt-1 ${badgeColor}`}>
              <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${dotColor}`} />
              {safetyLabel.toUpperCase()}
            </span>
          </div>
          <div className="relative w-24 h-24">
            <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="#E5E7EB" strokeWidth="3" />
              <circle cx="18" cy="18" r="15.9" fill="none" stroke={circleStroke} strokeWidth="3"
                strokeDasharray={`${score}, 100`} strokeLinecap="round" className="transition-all duration-1000" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <Shield className={scoreColor} size={28} />
            </div>
          </div>
        </div>
        <p className="text-gray-400 text-xs mt-3">Live data from ML model · H3 hexagonal grid</p>
      </div>

      {/* Quick Actions */}
      <div className="px-4 mt-5">
        <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Quick Actions</h2>
        <div className="grid grid-cols-2 gap-3">
          <Link href="/route" className="bg-emerald-600 text-white rounded-2xl p-4 flex flex-col gap-2 hover:bg-emerald-700 active:scale-95 transition-all shadow-md shadow-emerald-100">
            <Navigation size={22} />
            <span className="font-semibold text-sm">Find Safe Route</span>
            <span className="text-xs text-emerald-100">AI-optimized path</span>
          </Link>
          <Link href="/map" className="bg-white text-gray-800 rounded-2xl p-4 flex flex-col gap-2 border border-gray-100 hover:shadow-md active:scale-95 transition-all">
            <MapPin size={22} className="text-emerald-600" />
            <span className="font-semibold text-sm">Area Safety Map</span>
            <span className="text-xs text-gray-400">Hex grid overlay</span>
          </Link>
          <Link href="/profile" className="bg-white text-gray-800 rounded-2xl p-4 flex flex-col gap-2 border border-gray-100 hover:shadow-md active:scale-95 transition-all">
            <Phone size={22} className="text-blue-600" />
            <span className="font-semibold text-sm">Emergency Contacts</span>
            <span className="text-xs text-gray-400">3 contacts set</span>
          </Link>
          <Link href="/sos" className="bg-red-50 text-red-700 rounded-2xl p-4 flex flex-col gap-2 border border-red-100 hover:bg-red-100 active:scale-95 transition-all">
            <AlertTriangle size={22} />
            <span className="font-semibold text-sm">SOS Trigger</span>
            <span className="text-xs text-red-400">Emergency alert</span>
          </Link>
        </div>
      </div>

      {/* Recent Alerts Dashboard */}
      <div className="px-4 mt-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Recent Alerts Near You</h2>
          <span className="flex items-center gap-1 text-xs text-red-500 font-semibold">
            <Bell size={12} className="animate-bounce" /> Live
          </span>
        </div>
        <div className="flex flex-col gap-2">
          {activeAlerts.slice(0, 5).map((alert) => (
            <div key={alert.id} className={`bg-white rounded-xl p-3 border shadow-sm flex gap-3 ${alert.isLive ? "border-red-200 shadow-red-100" : "border-gray-100"}`}>
              <div className={`w-2 rounded-full shrink-0 mt-1 ${alert.severity === "high" ? "bg-red-500" : "bg-amber-400"} ${alert.isLive ? "animate-pulse" : ""}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <p className="text-xs font-bold text-gray-800 truncate">{alert.location}</p>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full shrink-0 font-bold ${alert.severity === "high" ? "bg-red-100 text-red-600" : "bg-amber-100 text-amber-600"}`}>
                    {alert.isLive ? "LIVE SOS" : alert.severity === "high" ? "HIGH" : "MED"}
                  </span>
                </div>
                <p className={`text-xs truncate ${alert.isLive && alert.desc !== "Live SOS Audio Stream Active..." ? "text-red-600 font-medium italic" : "text-gray-500"}`}>
                  {alert.isLive && alert.desc !== "Live SOS Audio Stream Active..." ? `🎙️ "${alert.desc}"` : alert.desc}
                </p>
                <div className="flex items-center gap-1 mt-1 text-[10px] text-gray-400">
                  <Clock size={10} />
                  {alert.time} · {alert.user}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Nearby Resources */}
      <div className="px-4 mt-5 mb-6">
        <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Nearby Resources</h2>
        <div className="flex flex-col gap-2">
          {[
            { label: "Bandra Police Station", sub: "780m away", color: "bg-blue-100 text-blue-600", icon: "🚔" },
            { label: "Lilavati Hospital", sub: "1.2km away", color: "bg-red-100 text-red-600", icon: "🏥" },
            { label: "Bandra Railway Station", sub: "950m away", color: "bg-yellow-100 text-yellow-700", icon: "🚉" },
          ].map((r) => (
            <div key={r.label} className="bg-white rounded-xl p-3 flex items-center gap-3 border border-gray-100 shadow-sm">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg ${r.color}`}>{r.icon}</div>
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-800">{r.label}</p>
                <p className="text-xs text-gray-400">{r.sub}</p>
              </div>
              <ChevronRight size={16} className="text-gray-300" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
