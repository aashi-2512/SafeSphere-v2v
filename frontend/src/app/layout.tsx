import type { Metadata } from "next";
import "./globals.css";
import DeviceFrame from "@/components/DeviceFrame";

export const metadata: Metadata = {
  title: "SafeSphere V2",
  description: "Next Generation Women's Safety App",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <DeviceFrame>{children}</DeviceFrame>
      </body>
    </html>
  );
}
