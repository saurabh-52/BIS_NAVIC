"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Shield, CheckCircle, ExternalLink, Info } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { mockVerification } from "@/services/mockData";
import { t } from "@/lib/translations";
import { HighlightTerms } from "@/components/ui/GlossaryTooltip";

type VerifyTab = "isi" | "hallmark" | "ecomark";

const TABS: { id: VerifyTab; icon: string }[] = [
  { id: "isi",      icon: "🔖" },
  { id: "hallmark", icon: "💍" },
  { id: "ecomark",  icon: "🌿" },
];

export default function ConsumerVerifyPanel() {
  const { addToast, language } = useAppStore();
  const [tab, setTab] = useState<VerifyTab>("isi");
  const [input, setInput] = useState("");
  const [result, setResult] = useState<typeof mockVerification.isi | typeof mockVerification.hallmark | null>(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    await new Promise(r => setTimeout(r, 1100));
    setResult(tab === "isi" ? mockVerification.isi : mockVerification.hallmark);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: "860px", margin: "0 auto" }}>
      
      {/* ── Header ────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: "16px", marginBottom: "24px" }}>
        <div style={{
          width: "48px",
          height: "48px",
          borderRadius: "12px",
          background: "rgba(250,93,0,0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}>
          <Shield size={24} color="var(--color-harvest-flame)" />
        </div>
        <div>
          <h2 style={{ fontSize: "24px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "4px" }}>
            {t("verify.title", language)}
          </h2>
          <p style={{ fontSize: "14px", color: "var(--color-warm-stone)" }}>
            {t("verify.subtitle", language)}
          </p>
        </div>
      </div>

      {/* ── Info Banner ───────────────────────────────── */}
      <div style={{
        background: "rgba(250,93,0,0.05)",
        border: "1px solid rgba(250,93,0,0.12)",
        borderRadius: "var(--radius-lg)",
        padding: "16px 20px",
        display: "flex",
        gap: "16px",
        marginBottom: "40px",
      }}>
        <div style={{
          fontSize: "14px",
          fontWeight: 800,
          color: "var(--color-harvest-flame)",
          background: "rgba(250,93,0,0.1)",
          padding: "4px 8px",
          borderRadius: "var(--radius-sm)",
          height: "fit-content",
        }}>
          IN
        </div>
        <div>
          <p style={{ fontSize: "13px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "4px" }}>
            {t("verify.powered", language)}
          </p>
          <p style={{ fontSize: "13px", color: "var(--color-warm-stone)", lineHeight: 1.5 }}>
            {t("verify.poweredSub", language)}
          </p>
        </div>
      </div>

      {/* ── Tabs ──────────────────────────────────────── */}
      <div style={{ display: "flex", borderBottom: "1px solid var(--color-parchment-shadow)", marginBottom: "24px", gap: "24px" }}>
        {TABS.map(tabItem => (
          <button
            key={tabItem.id}
            onClick={() => { setTab(tabItem.id); setResult(null); setInput(""); }}
            style={{
              padding: "12px 0",
              background: "transparent",
              border: "none",
              borderBottom: tab === tabItem.id ? "2px solid var(--color-harvest-flame)" : "2px solid transparent",
              fontSize: "14px",
              fontWeight: tab === tabItem.id ? 600 : 500,
              color: tab === tabItem.id ? "var(--color-harvest-flame)" : "var(--color-warm-stone)",
              cursor: "pointer",
              transition: "all 0.2s",
              marginBottom: "-1px",
            }}
          >
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ fontSize: "14px", color: "inherit" }}>{tabItem.icon}</span>
              {t(`verify.tabs.${tabItem.id}`, language)}
            </span>
          </button>
        ))}
      </div>

      {/* ── Input Card ────────────────────────────────── */}
      <motion.div
        whileHover={{ zIndex: 10 }}
        style={{
          background: "var(--color-paper-white)",
          border: "1px solid var(--color-parchment-shadow)",
          borderRadius: "var(--radius-lg)",
          padding: "32px",
          boxShadow: "var(--shadow-sm)",
          marginBottom: "24px",
          position: "relative",
        }}
      >
        
        {/* Card Header */}
        <div style={{ marginBottom: "24px" }}>
          <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "4px" }}>
            {t(`verify.card.${tab}`, language)}
          </h3>
          <div style={{ fontSize: "13px", color: "var(--color-warm-stone)", lineHeight: 1.5 }}>
            <HighlightTerms text={t(`verify.card.${tab}Sub`, language)} />
          </div>
        </div>

        {/* Input Field Area */}
        <div style={{ marginBottom: "24px" }}>
          <label style={{ fontSize: "13px", fontWeight: 700, color: "var(--color-ink-black)", display: "block", marginBottom: "4px" }}>
            <HighlightTerms text={t(`verify.label.${tab}`, language)} />
          </label>
          <div style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "12px", lineHeight: 1.5 }}>
            <HighlightTerms text={tab === "isi" ? t("verify.label.isiSub", language) : ""} />
          </div>
          
          <div style={{
            display: "flex",
            alignItems: "center",
            border: "1px solid var(--color-parchment-shadow)",
            borderRadius: "var(--radius-md)",
            background: "var(--color-cream-canvas)",
            overflow: "hidden",
            maxWidth: "600px",
            transition: "border-color 0.2s",
          }}
          onFocusCapture={(e) => { e.currentTarget.style.borderColor = "var(--color-harvest-flame)" }}
          onBlurCapture={(e) => { e.currentTarget.style.borderColor = "var(--color-parchment-shadow)" }}
          >
            {tab === "isi" && (
              <div style={{
                padding: "12px 16px",
                borderRight: "1px solid var(--color-parchment-shadow)",
                background: "var(--color-paper-white)",
                fontSize: "14px",
                color: "var(--color-warm-stone)",
              }}>
                CM/L or R-
              </div>
            )}
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder={tab === "isi" ? "e.g. 123456" : "e.g. AB12CD"}
              style={{
                flex: 1,
                padding: "12px 16px",
                background: "transparent",
                border: "none",
                outline: "none",
                fontSize: "15px",
                color: "var(--color-ink-black)",
              }}
              onKeyDown={e => e.key === "Enter" && handleVerify()}
            />
          </div>
        </div>

        {/* Verify Button */}
        <button
          onClick={handleVerify}
          disabled={!input.trim() || loading}
          style={{
            background: input.trim() && !loading ? "var(--color-harvest-flame)" : "var(--color-parchment-shadow)",
            color: input.trim() && !loading ? "#fff" : "var(--color-driftwood)",
            border: "none",
            borderRadius: "var(--radius-md)",
            padding: "12px 24px",
            fontSize: "14px",
            fontWeight: 600,
            cursor: input.trim() && !loading ? "pointer" : "not-allowed",
            boxShadow: input.trim() && !loading ? "var(--shadow-sm)" : "none",
            transition: "all 0.2s",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          {loading ? (
            <>
              <svg style={{ animation: "spin 1s linear infinite" }} width="16" height="16" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="60 40" />
              </svg>
              Verifying...
            </>
          ) : (
            <>
              <Search size={16} />
              {t("verify.btn", language)}
            </>
          )}
        </button>

        {/* Divider */}
        <div style={{ height: "1px", background: "var(--color-parchment-shadow)", margin: "32px 0 24px" }} />

        {/* Demo Numbers */}
        <div>
          <p style={{
            fontSize: "10px",
            fontWeight: 700,
            letterSpacing: "0.8px",
            textTransform: "uppercase",
            color: "var(--color-driftwood)",
            marginBottom: "12px",
          }}>
            {t("verify.examples", language)}
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
            {[
              "123456 — Helmet CM/L (Valid)",
              "987654 — LED Bulb R-No. (Expired)",
              "456789 — Water CM/L (Valid)"
            ].map(demo => (
              <button
                key={demo}
                onClick={() => setInput(demo.split(" ")[0])}
                style={{
                  padding: "6px 14px",
                  borderRadius: "var(--radius-full)",
                  border: "1px solid var(--color-parchment-shadow)",
                  background: "transparent",
                  fontSize: "12px",
                  color: "var(--color-ironwood)",
                  cursor: "pointer",
                  transition: "background 0.2s",
                }}
                onMouseEnter={e => { e.currentTarget.style.background = "var(--color-cream-canvas)" }}
                onMouseLeave={e => { e.currentTarget.style.background = "transparent" }}
              >
                {demo}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* ── Results ───────────────────────────────────── */}
        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              whileHover={{ zIndex: 10 }}
              style={{
                background: "var(--color-paper-white)",
                border: "1px solid var(--color-parchment-shadow)",
                borderRadius: "var(--radius-lg)",
                padding: "32px",
                boxShadow: "var(--shadow-sm)",
                position: "relative",
              }}
            >
            {/* Status header */}
            <div style={{ display: "flex", alignItems: "center", gap: "14px", marginBottom: "20px", paddingBottom: "16px", borderBottom: "1px solid var(--color-parchment-shadow)" }}>
              <div style={{
                width: "48px",
                height: "48px",
                borderRadius: "var(--radius-lg)",
                background: "var(--color-valid-green-bg)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}>
                <CheckCircle size={22} color="var(--color-valid-green)" />
              </div>
              <div>
                <p style={{ fontSize: "17px", fontWeight: 700, color: "var(--color-valid-green)" }}>✅ Valid BIS Licence</p>
                <p style={{ fontSize: "13px", color: "var(--color-driftwood)", marginTop: "2px" }}>
                  {"expiry" in result ? `Licence expires on ${result.expiry}` : `Hallmarked on ${result.stampDate}`}
                </p>
              </div>
            </div>

            {/* Details grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              <div>
                <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>Product</p>
                <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.product}</p>
              </div>
              <div>
                <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>Brand</p>
                <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.brand}</p>
              </div>
              <div>
                <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>IS Code</p>
                <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.isCode}</p>
              </div>
              {"licenseNumber" in result ? (
                <div>
                  <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>License No.</p>
                  <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.licenseNumber}</p>
                </div>
              ) : (
                <div>
                  <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>Purity</p>
                  <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.purity}</p>
                </div>
              )}
              {"manufacturer" in result ? (
                <div style={{ gridColumn: "span 2" }}>
                  <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>Manufacturer</p>
                  <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.manufacturer}</p>
                </div>
              ) : (
                <>
                  <div>
                    <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>Jeweller</p>
                    <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.jeweller}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginBottom: "4px" }}>AHC (Assaying Center)</p>
                    <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--color-ink-black)" }}>{result.ahc}</p>
                  </div>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
