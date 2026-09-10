"use client";

import Navbar from "@/components/shell/Navbar";
import { useRouter } from "next/navigation";
import { Sparkles, ShieldCheck, ArrowRight, BarChart3, Clock, Search } from "lucide-react";
import { motion } from "framer-motion";
import { useAppStore } from "@/store/useAppStore";
import { t } from "@/lib/translations";
import { HighlightTerms } from "@/components/ui/GlossaryTooltip";
import ApplicationTrackerModal from "@/components/dashboard/ApplicationTrackerModal";
import { useState } from "react";

export default function DashboardPage() {
  const router = useRouter();
  const { language } = useAppStore();
  const [trackerTitle, setTrackerTitle] = useState<string | null>(null);

  return (
    <div style={{ minHeight: "100vh", background: "var(--color-cream-canvas)", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <main style={{ flex: 1, padding: "64px 32px", maxWidth: "1160px", margin: "0 auto", width: "100%" }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          style={{ marginBottom: "48px" }}
        >
          <h1 style={{ fontSize: "36px", fontWeight: 800, color: "var(--color-ink-black)", marginBottom: "8px", letterSpacing: "-0.5px" }}>
            {t("dashboard.title", language)}
          </h1>
          <p style={{ fontSize: "16px", color: "var(--color-warm-stone)" }}>
            {t("dashboard.subtitle", language)}
          </p>
        </motion.div>

        {/* ── Main Actions Grid ───────────────────────────────── */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px", marginBottom: "40px" }}>
          
          {/* Compliance Assistant Card */}
          <motion.div style={{ position: "relative", zIndex: 1 }} whileHover={{ zIndex: 10 }} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
            <button
              onClick={() => router.push("/app?tab=roadmap")}
              style={{
                width: "100%",
                background: "var(--color-paper-white)",
                border: "1px solid var(--color-parchment-shadow)",
                borderRadius: "var(--radius-lg)",
                padding: "40px 32px",
                textAlign: "left",
                cursor: "pointer",
                boxShadow: "0 8px 30px rgba(0,0,0,0.03)",
                transition: "all 0.2s",
                display: "flex", flexDirection: "column", gap: "16px",
                height: "100%",
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = "var(--color-harvest-flame)";
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = "0 12px 40px rgba(250,93,0,0.08)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = "var(--color-parchment-shadow)";
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 8px 30px rgba(0,0,0,0.03)";
              }}
            >
              <div style={{
                width: "56px", height: "56px", borderRadius: "16px",
                background: "rgba(250,93,0,0.08)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <Sparkles size={28} color="var(--color-harvest-flame)" />
              </div>
              <div>
                <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "8px" }}>{t("dashboard.compliance.title", language)}</h2>
                <p style={{ fontSize: "14px", color: "var(--color-warm-stone)", lineHeight: 1.6 }}>
                  <HighlightTerms text={t("dashboard.compliance.desc", language)} />
                </p>
              </div>
              <div style={{ marginTop: "auto", display: "flex", alignItems: "center", gap: "6px", fontSize: "14px", fontWeight: 600, color: "var(--color-harvest-flame)", paddingTop: "12px" }}>
                {t("dashboard.compliance.cta", language)} <ArrowRight size={14} />
              </div>
            </button>
          </motion.div>

          {/* Verify Product Card */}
          <motion.div style={{ position: "relative", zIndex: 1 }} whileHover={{ zIndex: 10 }} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}>
            <button
              onClick={() => router.push("/app?tab=verify")}
              style={{
                width: "100%",
                background: "var(--color-paper-white)",
                border: "1px solid var(--color-parchment-shadow)",
                borderRadius: "var(--radius-lg)",
                padding: "40px 32px",
                textAlign: "left",
                cursor: "pointer",
                boxShadow: "0 8px 30px rgba(0,0,0,0.03)",
                transition: "all 0.2s",
                display: "flex", flexDirection: "column", gap: "16px",
                height: "100%",
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = "var(--color-harvest-flame)";
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = "0 12px 40px rgba(250,93,0,0.08)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = "var(--color-parchment-shadow)";
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 8px 30px rgba(0,0,0,0.03)";
              }}
            >
              <div style={{
                width: "56px", height: "56px", borderRadius: "16px",
                background: "rgba(250,93,0,0.08)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <ShieldCheck size={28} color="var(--color-harvest-flame)" />
              </div>
              <div>
                <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "8px" }}>{t("dashboard.verify.title", language)}</h2>
                <p style={{ fontSize: "14px", color: "var(--color-warm-stone)", lineHeight: 1.6 }}>
                  <HighlightTerms text={t("dashboard.verify.desc", language)} />
                </p>
              </div>
              <div style={{ marginTop: "auto", display: "flex", alignItems: "center", gap: "6px", fontSize: "14px", fontWeight: 600, color: "var(--color-harvest-flame)", paddingTop: "12px" }}>
                {t("dashboard.verify.cta", language)} <ArrowRight size={14} />
              </div>
            </button>
          </motion.div>

          {/* Impact Dashboard Card */}
          <motion.div style={{ position: "relative", zIndex: 1 }} whileHover={{ zIndex: 10 }} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.3 }}>
            <button
              onClick={() => router.push("/app?tab=impact")}
              style={{
                width: "100%",
                background: "var(--color-paper-white)",
                border: "1px solid var(--color-parchment-shadow)",
                borderRadius: "var(--radius-lg)",
                padding: "40px 32px",
                textAlign: "left",
                cursor: "pointer",
                boxShadow: "0 8px 30px rgba(0,0,0,0.03)",
                transition: "all 0.2s",
                display: "flex", flexDirection: "column", gap: "16px",
                height: "100%",
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = "var(--color-harvest-flame)";
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = "0 12px 40px rgba(250,93,0,0.08)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = "var(--color-parchment-shadow)";
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 8px 30px rgba(0,0,0,0.03)";
              }}
            >
              <div style={{
                width: "56px", height: "56px", borderRadius: "16px",
                background: "rgba(250,93,0,0.08)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <BarChart3 size={28} color="var(--color-harvest-flame)" />
              </div>
              <div>
                <h2 style={{ fontSize: "22px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "8px" }}>{t("dashboard.impact.title", language)}</h2>
                <p style={{ fontSize: "14px", color: "var(--color-warm-stone)", lineHeight: 1.6 }}>
                  <HighlightTerms text={t("dashboard.impact.desc", language)} />
                </p>
              </div>
              <div style={{ marginTop: "auto", display: "flex", alignItems: "center", gap: "6px", fontSize: "14px", fontWeight: 600, color: "var(--color-harvest-flame)", paddingTop: "12px" }}>
                {t("dashboard.impact.cta", language)} <ArrowRight size={14} />
              </div>
            </button>
          </motion.div>

        </div>

        {/* ── Recent Activity ───────────────────────────────── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.4 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "20px" }}>
            <Clock size={18} color="var(--color-ironwood)" />
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--color-ink-black)" }}>{t("dashboard.activity.title", language)}</h3>
          </div>

          <div style={{
            background: "var(--color-paper-white)",
            border: "1px solid var(--color-parchment-shadow)",
            borderRadius: "var(--radius-lg)",
            overflow: "hidden",
            boxShadow: "0 4px 12px rgba(0,0,0,0.02)",
          }}>
            {[
              { type: "search", textKey: "dashboard.activity.item1", dateKey: "dashboard.activity.time1", statusKey: "dashboard.activity.status1", statusEn: "Completed" },
              { type: "verify", textKey: "dashboard.activity.item2", dateKey: "dashboard.activity.time2", statusKey: "dashboard.activity.status2", statusEn: "Valid" },
              { type: "search", textKey: "dashboard.activity.item3", dateKey: "dashboard.activity.time3", statusKey: "dashboard.activity.status1", statusEn: "Completed" },
            ].map((item, idx) => (
              <button key={idx} onClick={() => setTrackerTitle(t(item.textKey, language))} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "20px 24px",
                borderBottom: idx !== 2 ? "1px solid var(--color-parchment-shadow)" : "none",
                background: "transparent",
                borderTop: "none", borderLeft: "none", borderRight: "none",
                width: "100%",
                cursor: "pointer",
                textAlign: "left",
                transition: "background 0.2s"
              }}
              onMouseOver={e => e.currentTarget.style.background = "var(--color-cream-canvas)"}
              onMouseOut={e => e.currentTarget.style.background = "transparent"}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <div style={{
                    width: "40px", height: "40px", borderRadius: "50%",
                    background: item.type === "search" ? "rgba(250,93,0,0.06)" : "rgba(10, 180, 80, 0.06)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    {item.type === "search" ? <Search size={18} color="var(--color-harvest-flame)" /> : <ShieldCheck size={18} color="var(--color-valid-green)" />}
                  </div>
                  <div>
                    <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)", marginBottom: "4px" }}>
                      <HighlightTerms text={t(item.textKey, language)} />
                    </p>
                    <p style={{ fontSize: "13px", color: "var(--color-warm-stone)" }}>{t(item.dateKey, language)}</p>
                  </div>
                </div>
                <div style={{
                  padding: "6px 12px", borderRadius: "var(--radius-full)", fontSize: "12px", fontWeight: 600,
                  background: item.statusEn === "Valid" ? "var(--color-valid-green-bg)" : "var(--color-cream-canvas)",
                  color: item.statusEn === "Valid" ? "var(--color-valid-green)" : "var(--color-ironwood)",
                }}>
                  {t(item.statusKey, language)}
                </div>
              </button>
            ))}
          </div>
        </motion.div>

      </main>

      <ApplicationTrackerModal 
        isOpen={!!trackerTitle} 
        onClose={() => setTrackerTitle(null)} 
        title={trackerTitle || ""} 
      />
    </div>
  );
}
