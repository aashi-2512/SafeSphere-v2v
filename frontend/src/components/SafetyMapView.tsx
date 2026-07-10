"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  center: [number, number];
  zoom: number;
  focusPoint?: [number, number] | null;
  route?: [number, number][];
  secondaryRoute?: [number, number][];
  routeColor?: string;
  onMapReady?: (map: any) => void;
}

export default function SafetyMapView({
  center,
  zoom,
  focusPoint,
  route,
  secondaryRoute,
  routeColor = "#10b981",
  onMapReady,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const routeLayerRef = useRef<any>(null);
  const secondaryLayerRef = useRef<any>(null);
  const focusMarkerRef = useRef<any>(null);
  const [mounted, setMounted] = useState(false);

  // Step 1: Mount map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    let destroyed = false;

    const init = async () => {
      const L = (await import("leaflet")).default;

      // Fix default icon
      // @ts-ignore
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      if (destroyed || !containerRef.current) return;

      const map = L.map(containerRef.current, {
        zoomControl: false,
        attributionControl: false,
      }).setView(center, zoom);

      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        { maxZoom: 19 }
      ).addTo(map);

      mapRef.current = map;
      onMapReady?.(map);
      setMounted(true);

      // Load hexagons from backend model
      try {
        const res = await fetch("http://127.0.0.1:8000/safety/hexagons");
        if (!res.ok) return;
        const hexData = await res.json();

        L.geoJSON(hexData, {
          style: (feature: any) => {
            const score = feature?.properties?.safety_score ?? 50;
            const color = score >= 80 ? "#10b981" : score >= 40 ? "#f59e0b" : "#ef4444";
            return { fillColor: color, weight: 1, opacity: 0.35, color, fillOpacity: 0.18 };
          }
        }).addTo(map);
      } catch (e) {
        console.warn("Could not load hexagons", e);
      }
    };

    init();

    return () => {
      destroyed = true;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        setMounted(false);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Step 2: Handle focus point changes
  useEffect(() => {
    if (!mounted || !mapRef.current) return;
    const L = require("leaflet");

    if (focusMarkerRef.current) {
      mapRef.current.removeLayer(focusMarkerRef.current);
      focusMarkerRef.current = null;
    }
    if (focusPoint) {
      mapRef.current.flyTo(focusPoint, 15, { animate: true, duration: 1 });
      focusMarkerRef.current = L.marker(focusPoint).addTo(mapRef.current);
    }
  }, [focusPoint, mounted]);

  // Step 3: Handle primary route drawing
  useEffect(() => {
    if (!mounted || !mapRef.current) return;
    const L = require("leaflet");

    if (routeLayerRef.current) {
      mapRef.current.removeLayer(routeLayerRef.current);
      routeLayerRef.current = null;
    }
    if (route && route.length > 1) {
      const poly = L.polyline(route, {
        color: routeColor,
        weight: 6,
        opacity: 0.9,
        lineJoin: "round",
      }).addTo(mapRef.current);
      routeLayerRef.current = poly;
      mapRef.current.fitBounds(poly.getBounds(), { padding: [60, 60] });

      // Start/End markers
      L.marker(route[0]).bindPopup("🚀 Start").addTo(mapRef.current);
      L.marker(route[route.length - 1]).bindPopup("🏁 Destination").addTo(mapRef.current);
    }
  }, [route, routeColor, mounted]);

  // Step 4: Handle secondary route drawing (quickest)
  useEffect(() => {
    if (!mounted || !mapRef.current) return;
    const L = require("leaflet");

    if (secondaryLayerRef.current) {
      mapRef.current.removeLayer(secondaryLayerRef.current);
      secondaryLayerRef.current = null;
    }
    if (secondaryRoute && secondaryRoute.length > 1) {
      const poly = L.polyline(secondaryRoute, {
        color: "#6b7280",
        weight: 4,
        opacity: 0.6,
        dashArray: "8 6",
        lineJoin: "round",
      }).addTo(mapRef.current);
      secondaryLayerRef.current = poly;
    }
  }, [secondaryRoute, mounted]);

  return (
    <div className="relative w-full h-full">
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <style>{`.hex-tooltip { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 6px 10px; font-size: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.12); }`}</style>
      <div ref={containerRef} className="w-full h-full" />
      {!mounted && (
        <div className="absolute inset-0 bg-gray-200 flex items-center justify-center">
          <div className="text-sm text-gray-500 flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            Loading map…
          </div>
        </div>
      )}
    </div>
  );
}
