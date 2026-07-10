"use client";

import { usePathname } from "next/navigation";
import BottomNav from "./BottomNav";

export default function DeviceFrame({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  // Admin dashboard gets full width desktop view
  if (pathname?.startsWith("/admin")) {
    return <div className="w-full min-h-screen bg-gray-50">{children}</div>;
  }

  // Mobile App gets the iPhone device frame
  return (
    <div className="relative w-full max-w-[400px] h-[850px] bg-white rounded-[3rem] shadow-2xl border-[14px] border-gray-900 overflow-hidden flex flex-col">
      {/* iPhone Dynamic Island Notch */}
      <div className="absolute top-0 inset-x-0 h-7 flex justify-center z-50 pointer-events-none">
        <div className="w-32 h-7 bg-gray-900 rounded-b-3xl"></div>
      </div>
      
      {/* App Content */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden bg-gray-50 pb-20">
        {children}
      </div>

      {/* Bottom Navigation (Sticky) */}
      <BottomNav />
    </div>
  );
}
