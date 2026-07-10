"use client";

import dynamic from "next/dynamic";
import { useState, useRef, useEffect } from "react";
import { Navigation, Search, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { api, type RouteData } from "@/lib/api";

const SafetyMapView = dynamic<any>(() => import("@/components/SafetyMapView") as any, {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-200 animate-pulse" />,
});

async function geocodeAddress(addr: string): Promise<{ lat: number; lng: number; name: string } | null> {
  // If it's already lat,lng format
  const parts = addr.split(",").map((s) => s.trim());
  if (parts.length === 2 && !isNaN(parseFloat(parts[0])) && !isNaN(parseFloat(parts[1]))) {
    return { lat: parseFloat(parts[0]), lng: parseFloat(parts[1]), name: addr };
  }
  // Geocode via Nominatim
  const res = await fetch(
    `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(addr + ", Mumbai")}&format=json&limit=1`,
    { headers: { "Accept-Language": "en" } }
  );
  const data = await res.json();
  if (!data.length) return null;
  return {
    lat: parseFloat(data[0].lat),
    lng: parseFloat(data[0].lon),
    name: data[0].display_name.split(",")[0],
  };
}

export default function RoutePage() {
  const [start, setStart] = useState("Bandra West, Mumbai");
  const [end, setEnd] = useState("Linking Road, Bandra");
  const [timeBucket, setTimeBucket] = useState("evening");
  const [routeData, setRouteData] = useState<RouteData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"safest" | "quickest">("safest");
  const [showSheet, setShowSheet] = useState(false);

  // Navigation state
  const [isNavigating, setIsNavigating] = useState(false);
  const [navIndex, setNavIndex] = useState(0);
  const [navFocus, setNavFocus] = useState<[number, number] | null>(null);
  const navIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const activeRoute = routeData
    ? activeTab === "safest"
      ? routeData.safest_route
      : routeData.quickest_route
    : null;

  const secondaryRoute =
    routeData && activeTab === "safest" ? routeData.quickest_route?.path_coords : undefined;

  const routesAreDifferent =
    routeData &&
    JSON.stringify(routeData.safest_route?.path_coords?.[0]) !==
      JSON.stringify(routeData.quickest_route?.path_coords?.[0]);

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setRouteData(null);
    setIsNavigating(false);
    stopNavigation();

    try {
      // Resolve addresses
      const [startGeo, endGeo] = await Promise.all([
        geocodeAddress(start),
        geocodeAddress(end),
      ]);
      if (!startGeo) throw new Error("Could not find start location.");
      if (!endGeo) throw new Error("Could not find destination.");

      const startStr = `${startGeo.lat},${startGeo.lng}`;
      const endStr = `${endGeo.lat},${endGeo.lng}`;

      const data = await api.fetchSafeRoute(startStr, endStr, timeBucket);
      setRouteData(data);
      setShowSheet(true);
      setActiveTab("safest");
    } catch (e: any) {
      setError(e.message || "Could not fetch route. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const stopNavigation = () => {
    if (navIntervalRef.current) clearInterval(navIntervalRef.current);
    navIntervalRef.current = null;
    setIsNavigating(false);
    setNavFocus(null);
  };

  const startNavigation = () => {
    if (!activeRoute?.path_coords?.length) return;
    setIsNavigating(true);
    setNavIndex(0);
    let idx = 0;
    const coords = activeRoute.path_coords;
    setNavFocus([coords[0][0], coords[0][1]]);

    navIntervalRef.current = setInterval(() => {
      idx++;
      if (idx >= coords.length) {
        stopNavigation();
        return;
      }
      setNavIndex(idx);
      setNavFocus([coords[idx][0], coords[idx][1]]);
    }, 700);
  };

  useEffect(() => () => stopNavigation(), []);

  return (
    <div className="relative flex flex-col h-full">
      {/* Map full screen */}
      <div className="absolute inset-0 z-0">
        <SafetyMapView
          center={[19.0544, 72.8402]}
          zoom={13}
          route={activeRoute?.path_coords}
          routeColor={activeTab === "safest" ? "#10b981" : "#3b82f6"}
          secondaryRoute={activeTab === "safest" ? secondaryRoute : undefined}
          focusPoint={navFocus}
        />
      </div>

      {/* Navigation Overlay — shown when navigating */}
      {isNavigating && activeRoute && (
        <div className="absolute top-10 left-3 right-3 z-30 bg-emerald-700 text-white rounded-2xl shadow-2xl p-4 flex items-center gap-3">
          <div className="bg-white/20 rounded-xl p-2">
            <Navigation size={24} className="animate-pulse" />
          </div>
          <div className="flex-1">
            <p className="font-bold text-sm">Navigating Safest Route</p>
            <p className="text-xs text-emerald-100">
              Step {navIndex + 1} / {activeRoute.path_coords.length} · Risk: {activeRoute.mean_risk.toFixed(1)}
            </p>
          </div>
          <button
            onClick={stopNavigation}
            className="bg-red-500 text-white text-xs px-3 py-1.5 rounded-lg font-bold"
          >
            End
          </button>
        </div>
      )}

      {/* Input card — hidden when navigating */}
      {!isNavigating && (
        <div className="absolute top-10 left-3 right-3 z-50 bg-white rounded-2xl shadow-xl p-4 border border-gray-100">
          <h2 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
            <Navigation size={16} className="text-emerald-600" /> Find Safe Route
          </h2>
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 border border-gray-200 rounded-xl px-3 py-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full shrink-0" />
              <input
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="flex-1 text-sm outline-none"
                placeholder="Start location or lat,lng"
              />
            </div>
            <div className="flex items-center gap-2 border border-gray-200 rounded-xl px-3 py-2">
              <div className="w-2 h-2 bg-red-500 rounded-full shrink-0" />
              <input
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                className="flex-1 text-sm outline-none"
                placeholder="Destination or lat,lng"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={timeBucket}
                onChange={(e) => setTimeBucket(e.target.value)}
                className="flex-1 text-sm border border-gray-200 rounded-xl px-3 py-2 outline-none bg-white"
              >
                <option value="day">🌤 Day</option>
                <option value="evening">🌆 Evening</option>
                <option value="night">🌙 Night</option>
              </select>
              <button
                onClick={handleGenerate}
                disabled={loading}
                className="flex-1 bg-emerald-600 text-white rounded-xl py-2 font-semibold text-sm flex items-center justify-center gap-1.5 disabled:opacity-50 hover:bg-emerald-700 active:scale-95 transition-all"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <><Navigation size={14} /> Go</>}
              </button>
            </div>
          </div>
          {error && <p className="text-red-500 text-xs mt-2 bg-red-50 px-3 py-2 rounded-lg">{error}</p>}
        </div>
      )}

      {/* Results Bottom Sheet */}
      {routeData && !isNavigating && (
        <div className="absolute bottom-0 left-0 right-0 z-20 bg-white rounded-t-3xl shadow-2xl border-t border-gray-100">
          {/* Handle + toggle */}
          <button className="w-full flex justify-center py-3" onClick={() => setShowSheet((s) => !s)}>
            <div className="w-10 h-1 bg-gray-200 rounded-full" />
          </button>
          <div className="px-5 pb-5">
            {/* Tabs */}
            <div className="flex bg-gray-100 rounded-xl p-1 mb-4">
              {(["safest", "quickest"] as const).map((tab) => {
                const r = tab === "safest" ? routeData.safest_route : routeData.quickest_route;
                const tabColor = tab === "safest" ? "text-emerald-700" : "text-blue-600";
                return (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === tab ? `bg-white shadow ${tabColor}` : "text-gray-400"}`}
                  >
                    {tab === "safest" ? "🛡️ Safest" : "⚡ Quickest"}
                    <div className="text-gray-400 font-normal text-xs mt-0.5">
                      Risk {r.mean_risk.toFixed(1)} · {Math.ceil(r.duration_s / 60)}min
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Route diff notice */}
            {routesAreDifferent && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl px-3 py-2 mb-3 text-xs text-emerald-700">
                ✅ SafeSphere found a safer alternative route! The Safest route (green) differs from the Quickest (dashed). See both on the map.
              </div>
            )}

            {activeRoute && (
              <>
                {/* Main stats + Start Nav */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className={`text-2xl font-bold ${activeTab === "safest" ? "text-emerald-700" : "text-blue-600"}`}>
                      {Math.ceil(activeRoute.duration_s / 60)} min
                    </div>
                    <div className="text-sm text-gray-400">{(activeRoute.distance_m / 1000).toFixed(2)} km</div>
                  </div>

                  {/* Google Maps-style Start Navigation */}
                  <button
                    onClick={startNavigation}
                    className="bg-emerald-600 text-white px-5 py-3 rounded-2xl font-bold text-sm flex items-center gap-2 hover:bg-emerald-700 active:scale-95 transition-all shadow-lg shadow-emerald-200"
                  >
                    <Navigation size={18} />
                    Start
                  </button>
                </div>

                {/* Safety breakdown */}
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-emerald-50 rounded-xl p-2 text-center">
                    <div className="text-emerald-700 font-bold text-sm">{activeRoute.mean_risk.toFixed(1)}</div>
                    <div className="text-xs text-gray-400">Mean Risk</div>
                  </div>
                  <div className="bg-orange-50 rounded-xl p-2 text-center">
                    <div className="text-orange-600 font-bold text-sm">{activeRoute.max_risk.toFixed(1)}</div>
                    <div className="text-xs text-gray-400">Max Risk</div>
                  </div>
                  <div className="bg-red-50 rounded-xl p-2 text-center">
                    <div className="text-red-600 font-bold text-sm">
                      {activeRoute.unsafe_count ?? activeRoute.unsafe_hex_count ?? 0}
                    </div>
                    <div className="text-xs text-gray-400">Unsafe Hexes</div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
