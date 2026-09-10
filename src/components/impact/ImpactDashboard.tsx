"use client";

import { motion } from "framer-motion";
import { BarChart3 } from "lucide-react";

const CATEGORIES = [
  {
    label: "Social",
    icon: "👥",
    items: [
      { value: "70%",  text: "Faster Compliance Discovery (MSMEs)" },
      { value: "100%", text: "Consumer Trust via Instant Verification" },
    ],
  },
  {
    label: "Economic",
    icon: "📈",
    items: [
      { value: "2×",   text: "Faster Time-to-Market for Startups" },
      { value: "Zero", text: "Compliance Mistakes for Startups" },
    ],
  },
  {
    label: "Quality & Regulatory",
    icon: "🏛️",
    items: [
      { value: "60%",  text: "Less Helpdesk Load (Government/BIS)" },
      { value: "🇮🇳", text: "Atmanirbhar Quality (Nation)" },
    ],
  },
];

export default function ImpactDashboard() {
  return (
    <div style={{ maxWidth: "900px", margin: "0 auto" }}>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <div style={{
          width: "64px",
          height: "64px",
          borderRadius: "var(--radius-lg)",
          background: "rgba(250,93,0,0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "0 auto 16px",
        }}>
          <BarChart3 size={28} color="var(--color-harvest-flame)" />
        </div>
        <h2 style={{ fontSize: "24px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "6px" }}>
          Impact Dashboard
        </h2>
        <p style={{ fontSize: "14px", color: "var(--color-warm-stone)" }}>
          Measurable outcomes from BIS NAVIC deployment
        </p>
      </div>

      {/* Category cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px", marginBottom: "24px" }}>
        {CATEGORIES.map((cat, ci) => (
          <motion.div
            key={cat.label}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: ci * 0.12 }}
            className="card"
            style={{ padding: "28px" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px" }}>
              <span style={{ fontSize: "22px" }}>{cat.icon}</span>
              <h3 style={{ fontSize: "15px", fontWeight: 700, color: "var(--color-ink-black)" }}>{cat.label}</h3>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {cat.items.map((item, ii) => (
                <motion.div
                  key={ii}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: ci * 0.12 + ii * 0.08 + 0.2 }}
                  style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}
                >
                  <div style={{
                    minWidth: "56px",
                    height: "48px",
                    background: "var(--color-cream-canvas)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--color-parchment-shadow)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: item.value.length > 3 ? "14px" : "18px",
                    fontWeight: 800,
                    color: "var(--color-harvest-flame)",
                  }}>
                    {item.value}
                  </div>
                  <p style={{ fontSize: "13px", color: "var(--color-ironwood)", lineHeight: 1.5 }}>
                    {item.text}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Bottom banner */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        style={{
          background: "var(--color-ink-black)",
          borderRadius: "var(--radius-lg)",
          padding: "28px 32px",
          textAlign: "center",
        }}
      >
        <p style={{ fontSize: "18px", fontWeight: 700, color: "var(--color-paper-white)", marginBottom: "6px" }}>
          Making Indian Standards &amp; Certification Seamless &amp; Instant
        </p>
        <p style={{ fontSize: "13px", color: "var(--color-driftwood)" }}>
          BIS NAVIC · Team Nomadic Devs · SIH 2026 · PS ID: SIH26107
        </p>
      </motion.div>
    </div>
  );
}
