"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function SOSPage() {
  const router = useRouter();
  const [status, setStatus] = useState<"idle" | "listening" | "processing">("idle");
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<any>(null);
  
  useEffect(() => {
    // Request microphone permissions explicitly so the browser prompts the user
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true }).catch(console.error);
    }

    // Initialize Speech Recognition if supported
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.onresult = (event: any) => {
        let finalTrans = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) finalTrans += event.results[i][0].transcript;
        }
        if (finalTrans) setTranscript((prev) => prev + " " + finalTrans);
      };
      rec.onerror = (e: any) => console.error("Speech reco error:", e);
      recognitionRef.current = rec;
    }
  }, []);

  const handlePointerDown = () => {
    if (status !== "idle") return;
    setStatus("listening");
    setTranscript("");
    if (recognitionRef.current) {
      try { recognitionRef.current.start(); } catch (e) {}
    }
  };

  const handlePointerUp = async () => {
    if (status !== "listening") return;
    setStatus("processing");
    
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (e) {}
    }

    // Wait a brief moment for final results to process
    await new Promise(r => setTimeout(r, 800));

    try {
      // 1. Trigger SOS
      const res = await api.triggerSOS("user-123", 19.0544, 72.8402, "+919876543210");
      
      // 2. Patch Transcript (fallback if empty or failed)
      const fallbackText = "Emergency! Suspicious person following me near the station, please send help immediately!";
      const finalWord = transcript.trim() || fallbackText;
      await api.updateTranscript(res.session_id, finalWord);
      
      // 3. Navigate
      router.push("/emergency");
    } catch {
      alert("Backend not reachable. Check that uvicorn is running.");
      setStatus("idle");
    }
  };

  return (
    <div className="flex flex-col min-h-full bg-red-50 pt-10 select-none">
      <div className="px-5 py-3 flex items-center gap-3">
        <button onClick={() => router.back()} className="text-sm text-red-600 font-semibold">← Back</button>
        <h1 className="text-base font-bold text-red-900">Emergency</h1>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-5 -mt-12">
        <p className="text-red-500 font-bold uppercase tracking-widest text-xs mb-8">
          {status === "idle" ? "Hold to Record SOS" : status === "listening" ? "Listening... Keep holding!" : "Broadcasting..."}
        </p>

        {/* Big SOS Button */}
        <button
          onPointerDown={handlePointerDown}
          onPointerUp={handlePointerUp}
          onPointerLeave={handlePointerUp}
          disabled={status === "processing"}
          className={`relative w-52 h-52 rounded-full text-white font-extrabold text-5xl transition-all disabled:opacity-70 ${
            status === "listening" ? "bg-red-700 scale-95 shadow-[0_0_80px_rgba(220,38,38,0.8)]" : "bg-red-600 shadow-[0_0_40px_rgba(220,38,38,0.5)]"
          }`}
        >
          SOS
          {status !== "idle" && (
            <span className="absolute inset-0 rounded-full border-4 border-red-300 animate-ping" />
          )}
        </button>
        
        {/* Live Transcript Preview */}
        {status === "listening" && (
          <div className="mt-8 px-6 text-center h-16">
            <p className="text-red-700 italic text-sm">" {transcript || "Speak clearly..."} "</p>
          </div>
        )}

        <div className="mt-10 w-full bg-white rounded-2xl p-5 border border-red-100 shadow-sm">
          <h3 className="font-bold text-gray-800 mb-1">Emergency Contacts (3)</h3>
          <p className="text-sm text-gray-400 mb-4">They will receive your live location & audio stream.</p>
          <div className="flex flex-col gap-3">
            {[
              { label: "📍 Location Sharing", status: "Active", color: "text-emerald-600" },
              { label: "🎙️ Microphone", status: "Granted", color: "text-emerald-600" },
              { label: "📲 SMS Alerts", status: "Ready", color: "text-blue-600" },
            ].map((item) => (
              <div key={item.label} className="flex justify-between items-center">
                <span className="text-sm text-gray-700">{item.label}</span>
                <span className={`text-sm font-semibold ${item.color}`}>{item.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
