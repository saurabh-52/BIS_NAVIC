import type { Metadata } from "next";
import { Inter, Fraunces } from "next/font/google";
import "./globals.css";
import StoreProvider from "@/store/StoreProvider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  display: "swap",
  weight: ["400"],
  style: ["normal", "italic"],
});

export const metadata: Metadata = {
  title: "BIS NAVIC — AI-Powered BIS Certification Assistant",
  description: "Navigate BIS certification instantly. AI-powered guidance for IS codes, schemes, fees & labs — in plain English or Hindi. Built by Team Nomadic Devs for SIH 2026.",
  keywords: ["BIS", "NAVIC", "certification", "ISI Mark", "CRS", "Hallmarking", "FMCS", "compliance", "India", "MSME"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${fraunces.variable}`}>
      <body className="min-h-screen flex flex-col">
        <StoreProvider>
          {children}
        </StoreProvider>
      </body>
    </html>
  );
}
