"use client";

import LabFinderPanel from "@/components/labfinder/LabFinderPanel";
import { ToastContainer } from "@/components/shared/Toast";

// Harvest design system is light-only — no dark mode toggling needed.
export default function StoreProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <LabFinderPanel />
      <ToastContainer />
    </>
  );
}
