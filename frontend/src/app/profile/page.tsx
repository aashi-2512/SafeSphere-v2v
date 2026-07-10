"use client";

import { Shield, Phone, ChevronRight, Bell, MapPin, User } from "lucide-react";
import Link from "next/link";

export default function ProfilePage() {
  return (
    <div className="flex flex-col min-h-full bg-gray-50 pb-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-emerald-700 to-emerald-500 pt-10 pb-12 px-5 rounded-b-3xl">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center text-3xl shadow">👩</div>
          <div>
            <h1 className="text-white text-xl font-bold">Shreya Mehta</h1>
            <p className="text-emerald-100 text-sm">+91 98765 43210</p>
            <span className="inline-block mt-1 bg-white/20 text-white text-xs px-2 py-0.5 rounded-full">SafeSphere Pro</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="mx-4 -mt-6 grid grid-cols-2 gap-3 relative z-10">
        {[
          { label: "Alerts Sent", value: "2", icon: "🚨" },
          { label: "Safety Score", value: "82", icon: "🛡️" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-2xl p-3 text-center shadow-sm border border-gray-100">
            <div className="text-2xl mb-1">{s.icon}</div>
            <div className="text-lg font-bold text-gray-800">{s.value}</div>
            <div className="text-xs text-gray-400">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Emergency Contacts */}
      <div className="px-4 mt-5">
        <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Emergency Contacts</h2>
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
          {[
            { name: "Mom", phone: "+91 99001 11234", relation: "Mother" },
            { name: "Aisha", phone: "+91 87654 32100", relation: "Friend" },
            { name: "Rahul", phone: "+91 77889 90011", relation: "Brother" },
          ].map((c, i) => (
            <div key={c.name} className={`flex items-center gap-3 p-4 ${i !== 2 ? "border-b border-gray-50" : ""}`}>
              <div className="w-10 h-10 bg-emerald-100 text-emerald-700 rounded-xl flex items-center justify-center font-bold text-sm">
                {c.name[0]}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-sm text-gray-800">{c.name} <span className="text-gray-400 font-normal">· {c.relation}</span></p>
                <p className="text-xs text-gray-400">{c.phone}</p>
              </div>
              <Phone size={16} className="text-emerald-500" />
            </div>
          ))}
          <button className="w-full py-3 text-sm text-emerald-600 font-semibold text-center border-t border-gray-50">
            + Add Contact
          </button>
        </div>
      </div>

      {/* My Alerts */}
      <div className="px-4 mt-5">
        <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">My SOS History</h2>
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
          {[
            { loc: "Bandra West", time: "Jul 9, 8:42 PM", status: "Resolved", color: "text-emerald-600 bg-emerald-50" },
            { loc: "Kurla Station", time: "Jul 2, 10:15 PM", status: "Resolved", color: "text-emerald-600 bg-emerald-50" },
          ].map((a, i) => (
            <div key={i} className={`flex items-center gap-3 p-4 ${i === 0 ? "border-b border-gray-50" : ""}`}>
              <div className="w-9 h-9 bg-red-100 rounded-xl flex items-center justify-center text-base">🚨</div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">{a.loc}</p>
                <p className="text-xs text-gray-400">{a.time}</p>
              </div>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${a.color}`}>{a.status}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Settings */}
      <div className="px-4 mt-5">
        <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Settings</h2>
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
          {[
            { label: "Location Sharing", icon: MapPin, color: "text-blue-500 bg-blue-50" },
            { label: "SOS Notifications", icon: Bell, color: "text-red-500 bg-red-50" },
            { label: "Safe Zone Alerts", icon: Shield, color: "text-emerald-500 bg-emerald-50" },
            { label: "Account & Privacy", icon: User, color: "text-purple-500 bg-purple-50" },
          ].map((item, i) => (
            <div key={item.label} className={`flex items-center gap-3 p-4 ${i !== 3 ? "border-b border-gray-50" : ""}`}>
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${item.color}`}>
                <item.icon size={18} />
              </div>
              <span className="flex-1 text-sm font-medium text-gray-800">{item.label}</span>
              <ChevronRight size={16} className="text-gray-300" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
