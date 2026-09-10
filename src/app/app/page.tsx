"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowLeftRight } from "lucide-react";
import ChatPanel from "@/components/chat/ChatPanel";
import RoadmapOutput from "@/components/roadmap/RoadmapOutput";
import ConsumerVerifyPanel from "@/components/verify/ConsumerVerifyPanel";
import ImpactDashboard from "@/components/impact/ImpactDashboard";
import { useAppStore } from "@/store/useAppStore";

function AppContent() {
  const { activeTab, setActiveTab } = useAppStore();
  const searchParams = useSearchParams();

  // Resize logic
  const [sidebarWidth, setSidebarWidth] = useState(360);
  const isResizing = useRef(false);

  const startResizing = () => {
    isResizing.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  };

  const stopResizing = () => {
    isResizing.current = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  };

  const resize = (e: MouseEvent) => {
    if (isResizing.current) {
      const newWidth = e.clientX;
      if (newWidth >= 280 && newWidth <= 800) {
        setSidebarWidth(newWidth);
      }
    }
  };

  useEffect(() => {
    window.addEventListener("mousemove", resize);
    window.addEventListener("mouseup", stopResizing);
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, []);

  useEffect(() => {
    const tab = searchParams.get("tab");
    if (tab && (tab === "roadmap" || tab === "verify" || tab === "impact")) {
      setActiveTab(tab);
    }
  }, [searchParams, setActiveTab]);

  if (activeTab === "verify") {
    return (
      <div style={{ flex: 1, padding: "40px 32px", background: "var(--color-cream-canvas)", minHeight: "calc(100vh - 64px)" }}>
        <ConsumerVerifyPanel />
      </div>
    );
  }

  if (activeTab === "impact") {
    return (
      <div style={{ flex: 1, padding: "40px 32px", background: "var(--color-cream-canvas)", minHeight: "calc(100vh - 64px)" }}>
        <ImpactDashboard />
      </div>
    );
  }

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        alignItems: "flex-start",
        gap: "0",
        maxWidth: "100%",
        minHeight: "calc(100vh - 64px)",
      }}
    >
      {/* ── Left Panel ────────────── */}
      <div
        style={{
          width: `${sidebarWidth}px`,
          flexShrink: 0,
          position: "sticky",
          top: "64px",
          height: "calc(100vh - 64px)",
          overflowY: "auto",
          background: "var(--color-paper-white)",
          padding: "24px 20px",
        }}
      >
        <ChatPanel />
      </div>

      {/* ── Resizer ────────────── */}
      <div
        onMouseDown={startResizing}
        style={{
          width: "16px",
          marginLeft: "-8px",
          marginRight: "-8px",
          cursor: "col-resize",
          height: "calc(100vh - 64px)",
          position: "sticky",
          top: "64px",
          zIndex: 10,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
        onMouseEnter={(e) => {
          const line = e.currentTarget.querySelector('.resize-line') as HTMLElement;
          const icon = e.currentTarget.querySelector('.resize-icon') as HTMLElement;
          if (line) line.style.background = "var(--color-harvest-flame)";
          if (icon) {
            icon.style.background = "var(--color-harvest-flame)";
            icon.style.color = "#fff";
            icon.style.borderColor = "var(--color-harvest-flame)";
          }
        }}
        onMouseLeave={(e) => {
          if (!isResizing.current) {
            const line = e.currentTarget.querySelector('.resize-line') as HTMLElement;
            const icon = e.currentTarget.querySelector('.resize-icon') as HTMLElement;
            if (line) line.style.background = "var(--color-parchment-shadow)";
            if (icon) {
              icon.style.background = "var(--color-paper-white)";
              icon.style.color = "var(--color-warm-stone)";
              icon.style.borderColor = "var(--color-parchment-shadow)";
            }
          }
        }}
      >
        {/* The actual visible line */}
        <div 
          className="resize-line"
          style={{
            width: "2px",
            height: "100%",
            background: "var(--color-parchment-shadow)",
            transition: "background 0.2s",
            position: "absolute",
          }} 
        />
        {/* The grabber icon */}
        <div 
          className="resize-icon"
          style={{
            width: "24px",
            height: "24px",
            borderRadius: "50%",
            background: "var(--color-paper-white)",
            border: "1px solid var(--color-parchment-shadow)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 2,
            color: "var(--color-warm-stone)",
            transition: "all 0.2s",
            boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
          }}
        >
          <ArrowLeftRight size={12} />
        </div>
      </div>

      {/* ── Right Panel ──────────────────────────── */}
      <div
        style={{
          flex: 1,
          minWidth: 0,
          padding: "32px 40px",
          background: "var(--color-cream-canvas)",
          minHeight: "calc(100vh - 64px)",
        }}
      >
        <RoadmapOutput />
      </div>
    </div>
  );
}

export default function AppPage() {
  return (
    <Suspense fallback={<div style={{ padding: "40px", color: "var(--color-warm-stone)" }}>Loading...</div>}>
      <AppContent />
    </Suspense>
  );
}
