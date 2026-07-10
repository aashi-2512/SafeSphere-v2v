"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Map, Route as RouteIcon, User } from "lucide-react";

export default function BottomNav() {
  const pathname = usePathname();
  
  // Hide bottom nav on splash, sos, and emergency screens
  if (['/splash', '/sos', '/emergency'].includes(pathname || '')) {
    return null;
  }

  const navItems = [
    { name: "Home", href: "/", icon: Home },
    { name: "Map", href: "/map", icon: Map },
    { name: "Route", href: "/route", icon: RouteIcon },
    { name: "Profile", href: "/profile", icon: User },
  ];

  return (
    <nav className="absolute bottom-0 w-full bg-white border-t border-gray-200 flex justify-between items-center px-6 py-4 z-40 rounded-b-[2rem]">
      {/* Floating SOS Button */}
      <Link href="/sos" className="absolute left-1/2 -top-6 -translate-x-1/2 bg-red-600 text-white w-14 h-14 rounded-full flex items-center justify-center font-bold shadow-[0_0_15px_rgba(220,38,38,0.5)] border-4 border-white z-50 animate-pulse">
        SOS
      </Link>
      
      <div className="w-full flex justify-between">
        {navItems.map((item, idx) => {
          const isActive = pathname === item.href;
          // Add a spacer in the middle for the SOS button
          const isSpacer = idx === 2;
          
          return (
            <div key={item.name} className="flex gap-8">
              {isSpacer && <div className="w-8" />} 
              <Link href={item.href} className={`flex flex-col items-center gap-1 ${isActive ? "text-emerald-600" : "text-gray-400"}`}>
                <item.icon size={24} strokeWidth={isActive ? 2.5 : 1.5} />
                <span className="text-[10px] font-medium">{item.name}</span>
              </Link>
            </div>
          );
        })}
      </div>
    </nav>
  );
}
