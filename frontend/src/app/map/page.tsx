"use client";

import dynamic from "next/dynamic";
import { useState, useCallback, useRef } from "react";
import { Search, MapPin, Loader2 } from "lucide-react";

const SafetyMapView = dynamic<any>(() => import("@/components/SafetyMapView") as any, { 
  ssr: false, 
  loading: () => <div className="w-full h-full bg-gray-200 animate-pulse" /> 
});

interface SafetyInfo {
  safety_score: number;
  safety_label: string;
  crime_count: number;
  nearest_police_m: number;
  nearest_hospital_m: number;
  lat: number;
  lng: number;
}

export default function MapPage() {
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [safetyInfo, setSafetyInfo] = useState<SafetyInfo | null>(null);
  const [focusPoint, setFocusPoint] = useState<[number, number] | null>(null);
  const [locationName, setLocationName] = useState("");
  const [searchError, setSearchError] = useState("");

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setSearchError("");
    setSafetyInfo(null);

    try {
      // 1. Geocode the query
      const geocodeRes = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query + ", Mumbai")}&format=json&limit=1`,
        { headers: { "Accept-Language": "en" } }
      );
      const geocodeData = await geocodeRes.json();

      if (!geocodeData.length) {
        setSearchError("Location not found. Try a more specific query.");
        return;
      }

      const { lat, lon, display_name } = geocodeData[0];
      const latNum = parseFloat(lat);
      const lngNum = parseFloat(lon);
      setFocusPoint([latNum, lngNum]);
      setLocationName(display_name.split(",")[0]);

      // 2. Fetch safety score from backend model
      const scoreRes = await fetch(
        `http://127.0.0.1:8000/safety/score?lat=${latNum}&lng=${lngNum}`
      );
      if (scoreRes.ok) {
        const scoreData = await scoreRes.json();
        setSafetyInfo({ ...scoreData, lat: latNum, lng: lngNum });
      } else {
        setSearchError("Location found but outside Mumbai safety data coverage.");
      }
    } catch {
      setSearchError("Search failed. Check your connection.");
    } finally {
      setSearching(false);
    }
  }, [query]);

  const scoreColor = safetyInfo
    ? safetyInfo.safety_score >= 80 ? "text-emerald-600" : safetyInfo.safety_score >= 40 ? "text-amber-500" : "text-red-600"
    : "";
  const badgeBg = safetyInfo
    ? safetyInfo.safety_score >= 80 ? "bg-emerald-100 text-emerald-700" : safetyInfo.safety_score >= 40 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"
    : "";

  return (
    <div className="relative flex flex-col h-full bg-white">
      {/* Permanent Search Header */}
      <div className="pt-12 px-4 pb-4 shadow-sm z-20 relative bg-white">
        <h1 className="text-xl font-bold text-gray-900 mb-4">Area Safety Map</h1>
        <form onSubmit={handleSearch}>
          <div className="flex items-center bg-gray-50 rounded-2xl border border-gray-200 px-4 py-3 gap-3">
            <Search size={18} className="text-gray-400 shrink-0" />
            <input
              type="text"
              className="flex-1 text-sm outline-none bg-transparent"
              placeholder="Search Mumbai locations…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button
              type="submit"
              disabled={searching}
              className="bg-emerald-600 text-white text-xs px-4 py-2 rounded-lg font-bold flex items-center gap-1 disabled:opacity-60 shadow-sm"
            >
              {searching ? <Loader2 size={14} className="animate-spin" /> : "Search"}
            </button>
          </div>
          {searchError && (
            <p className="text-xs text-red-500 mt-2 ml-1">{searchError}</p>
          )}
        </form>
      </div>

      {/* Map Frame */}
      <div className="flex-1 relative z-0 border-y border-gray-100">
        <SafetyMapView center={[19.0544, 72.8402]} zoom={12} focusPoint={focusPoint} />
      </div>

      {/* Bottom Sheet */}
      <div className="bg-white rounded-t-3xl shadow-2xl border-t border-gray-100 z-20 px-5 py-4 max-h-56 overflow-y-auto">
        <div className="w-10 h-1 bg-gray-200 rounded-full mx-auto mb-3" />
        {safetyInfo ? (
          <>
            <div className="flex justify-between items-start mb-3">
              <div>
                <h2 className="text-base font-bold text-gray-900">{locationName}</h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-3xl font-bold ${scoreColor}`}>{safetyInfo.safety_score.toFixed(0)}</span>
                  <span className="text-gray-400 text-sm">/100</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${badgeBg}`}>{safetyInfo.safety_label.toUpperCase()}</span>
                </div>
                <p className="text-xs text-gray-400 mt-1">From ML model · H3 hex grid</p>
              </div>
              <MapPin className="text-gray-200" size={24} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-blue-50 rounded-xl p-2.5 text-center">
                <div className="text-blue-600 font-bold text-sm">{(safetyInfo.nearest_police_m / 1000).toFixed(1)}km</div>
                <div className="text-xs text-gray-500 mt-0.5">🚔 Police Station</div>
              </div>
              <div className="bg-red-50 rounded-xl p-2.5 text-center">
                <div className="text-red-600 font-bold text-sm">{(safetyInfo.nearest_hospital_m / 1000).toFixed(1)}km</div>
                <div className="text-xs text-gray-500 mt-0.5">🏥 Hospital</div>
              </div>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-sm font-bold text-gray-700 mb-1">Safety Map</h2>
            <p className="text-xs text-gray-400 mb-3">Search any Mumbai location to see its ML-predicted safety score. Tap any hexagon for area details.</p>
            <div className="flex gap-3 text-xs flex-wrap">
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-400 inline-block" /> Safe (80+)</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-400 inline-block" /> Moderate (40–80)</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-400 inline-block" /> Unsafe (&lt;40)</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
