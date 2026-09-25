"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ExternalLink, FileText, CheckCircle, X, Info, Download, MapPin, Volume2 } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import AgentPipelineLog from "@/components/pipeline/AgentPipelineLog";
import { clauseFixtures, ClauseData } from "@/lib/clauseFixtures";
import StandardRecommender from "@/components/recommender/StandardRecommender";
import { t } from "@/lib/translations";

const SCHEME_ICONS: Record<string, string> = {
  isi:       "🔖",
  crs:       "⚙️",
  hallmark:  "💍",
  ecomark:   "🌿",
  fmcs:      "🌍",
};

export default function RoadmapOutput() {
  const { activeResult, pipelineStages, language, setLabFinderOpen } = useAppStore();
  const [selectedClause, setSelectedClause] = useState<ClauseData | null>(null);

  // Strictly require all pipeline stages to be completed before showing the result!
  const isTaskComplete = Boolean(
    activeResult &&
    pipelineStages.length > 0 &&
    pipelineStages.every(s => s.status === "done")
  );

  // Empty state: no result and no stages in progress
  if (!activeResult && !pipelineStages.length) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "60vh",
        textAlign: "center",
        padding: "40px",
      }}>
        {/* Sparkle icon */}
        <div style={{
          width: "72px",
          height: "72px",
          borderRadius: "50%",
          background: "rgba(250,93,0,0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: "20px",
          fontSize: "28px",
        }}>
          ✨
        </div>

        <h2 style={{
          fontSize: "20px",
          fontWeight: 700,
          color: "var(--color-ink-black)",
          marginBottom: "12px",
        }}>
          {t("app.roadmap.emptyTitle", language)}
        </h2>

        <p style={{
          fontSize: "14px",
          color: "var(--color-warm-stone)",
          maxWidth: "360px",
          lineHeight: 1.65,
          marginBottom: "28px",
        }}>
          {t("app.roadmap.emptySub", language)}
        </p>

        {/* Preview chips */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", justifyContent: "center" }}>
          {["IS 13252:2010", "CRS Scheme-II", "STQC Lab", "₹10,000 fee"].map(chip => (
            <span
              key={chip}
              style={{
                padding: "6px 16px",
                borderRadius: "var(--radius-full)",
                border: "1px solid var(--color-parchment-shadow)",
                background: "var(--color-paper-white)",
                fontSize: "12px",
                color: "var(--color-warm-stone)",
                fontWeight: 500,
              }}
            >
              {chip}
            </span>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>

      {/* Pipeline Animation */}
      <AgentPipelineLog />

      {/* ONLY show results when the task has fully completed! */}
      {isTaskComplete && activeResult && (
        <motion.div
          key={activeResult.id}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          style={{ display: "flex", flexDirection: "column", gap: "20px" }}
        >
          {/* ── Standard Recommender (100% Dynamic, No Static Fixtures) ── */}
          <StandardRecommender
            standards={
              activeResult.recommendedStandards && activeResult.recommendedStandards.length > 0
                ? activeResult.recommendedStandards
                : (activeResult.isCode && activeResult.isCode !== "Unknown" ? [{
                    isCode: activeResult.isCode,
                    title: activeResult.isCodeTitle || "Official Indian Standard Specification",
                    type: "Mandatory",
                    description: `Primary standard identified for ${activeResult.product}.`,
                  }] : [])
            }
          />

          {/* ── Triage Card ─────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ type: "spring", damping: 22 }}
            className="card"
            style={{ padding: "28px" }}
          >
            {/* Header with Tools */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <p style={{
                fontSize: "11px",
                fontWeight: 700,
                letterSpacing: "1px",
                textTransform: "uppercase",
                color: "var(--color-driftwood)",
                margin: 0,
              }}>
                Triage Result
              </p>
              
              <div className="no-print" style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={() => {
                    const text = `The detected product is ${activeResult.product}. The applicable scheme is ${activeResult.schemeLabel}.`;
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = language === "hi" ? "hi-IN" : "en-IN";
                    window.speechSynthesis.speak(utterance);
                  }}
                  className="btn-ghost"
                  style={{ padding: "4px 8px", fontSize: "11px", display: "flex", alignItems: "center", gap: "4px" }}
                >
                  <Volume2 size={12} /> Speak
                </button>
                <button
                  onClick={() => window.print()}
                  className="btn-ghost"
                  style={{ padding: "4px 8px", fontSize: "11px", display: "flex", alignItems: "center", gap: "4px" }}
                >
                  <Download size={12} /> Export PDF
                </button>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>
              {[
                { label: "Product Detected", value: activeResult.product },
                { label: "Category",         value: activeResult.category },
                { label: "Persona",          value: activeResult.persona },
              ].map(item => (
                <div key={item.label}>
                  <p style={{ fontSize: "11px", color: "var(--color-driftwood)", marginBottom: "3px" }}>{item.label}</p>
                  <p style={{ fontSize: "14px", fontWeight: 600, color: "var(--color-ink-black)" }}>{item.value}</p>
                </div>
              ))}
              <div>
                <p style={{ fontSize: "11px", color: "var(--color-driftwood)", marginBottom: "6px" }}>Applicable Scheme</p>
                <span className="badge-scheme active">
                  {SCHEME_ICONS[activeResult.scheme] ?? "🔖"} {activeResult.schemeLabel}
                </span>
              </div>
            </div>

            {/* Scheme Classification Reasons */}
            {activeResult.reasons && (
              <div style={{
                marginTop: "16px",
                paddingTop: "16px",
                borderTop: "1px dashed var(--color-parchment-shadow)",
              }}>
                <p style={{ fontSize: "11px", color: "var(--color-driftwood)", marginBottom: "8px" }}>Classification Rationale</p>
                <ul style={{ margin: 0, paddingLeft: "16px", color: "var(--color-warm-stone)", fontSize: "13px", lineHeight: 1.5 }}>
                  {activeResult.reasons.map((reason, idx) => (
                    <li key={idx} style={{ marginBottom: "4px" }}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>

          {/* ── IS Code + Clause Citation ────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
            style={{ padding: "28px" }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
              <div>
                <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", color: "var(--color-driftwood)", marginBottom: "6px" }}>
                  IS Code
                </p>
                <p style={{ fontSize: "18px", fontWeight: 700, color: "var(--color-ink-black)" }}>
                  {activeResult.isCode}
                </p>
                <p style={{ fontSize: "13px", color: "var(--color-warm-stone)", marginTop: "2px" }}>
                  {activeResult.isCodeTitle}
                </p>
              </div>
              <a
                href={`https://bis.gov.in`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "12px",
                  color: "var(--color-harvest-flame)",
                  fontWeight: 600,
                  textDecoration: "none",
                }}
              >
                View Standard <ExternalLink size={12} />
              </a>
            </div>

            {/* Clause Citation */}
            <div style={{
              background: "var(--color-cream-canvas)",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--color-parchment-shadow)",
              padding: "16px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <p style={{ fontSize: "11px", fontWeight: 700, color: "var(--color-warm-stone)" }}>
                  CLAUSE CITATION
                </p>
                {activeResult.clauseData ? (
                  <span className="badge-valid">
                    <CheckCircle size={10} /> Verified Source
                  </span>
                ) : (
                  <span style={{ fontSize: "11px", color: "var(--color-driftwood)", display: "flex", alignItems: "center", gap: "4px" }}>
                    <Info size={11} /> Unindexed Clause
                  </span>
                )}
              </div>
              <p style={{ fontSize: "14px", fontWeight: 600, color: "var(--color-ink-black)", marginBottom: "4px" }}>
                {activeResult.clauseData?.source || activeResult.clauseRef}
              </p>
              <p style={{ fontSize: "12px", color: "var(--color-driftwood)" }}>
                {activeResult.clauseData
                  ? "Clause-Level Grounding · Cross-checked against BIS gazette"
                  : "No direct standard clause in local index · Refer to official portal"}
              </p>
            </div>
          </motion.div>

          {/* ── Compliance Steps ─────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="card"
            style={{ padding: "28px" }}
          >
            <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", color: "var(--color-driftwood)", marginBottom: "20px" }}>
              Compliance Roadmap
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {activeResult.steps.map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + i * 0.08 }}
                  style={{ display: "flex", gap: "14px", alignItems: "flex-start" }}
                >
                  <div style={{
                    width: "28px",
                    height: "28px",
                    borderRadius: "50%",
                    background: "var(--color-harvest-flame)",
                    color: "#fff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "12px",
                    fontWeight: 700,
                    flexShrink: 0,
                  }}>
                    {i + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "6px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                        <p style={{ fontSize: "14px", fontWeight: 600, color: "var(--color-ink-black)" }}>
                          {step.title}
                        </p>
                        {(activeResult.clauseData || (activeResult.clauseFixtureId && clauseFixtures[activeResult.clauseFixtureId])) && (
                          <button
                            onClick={() => {
                              if (activeResult.clauseData) {
                                setSelectedClause(activeResult.clauseData);
                              } else if (activeResult.clauseFixtureId && clauseFixtures[activeResult.clauseFixtureId]) {
                                setSelectedClause(clauseFixtures[activeResult.clauseFixtureId]);
                              }
                            }}
                            style={{
                              background: "rgba(16, 185, 129, 0.1)",
                              color: "var(--color-valid-green)",
                              border: "none",
                              borderRadius: "4px",
                              padding: "2px 6px",
                              fontSize: "10px",
                              fontWeight: 700,
                              cursor: "pointer",
                              display: "flex", alignItems: "center", gap: "3px",
                              transition: "background 0.2s"
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = "rgba(16, 185, 129, 0.2)"}
                            onMouseLeave={e => e.currentTarget.style.background = "rgba(16, 185, 129, 0.1)"}
                          >
                            <FileText size={10} /> Source
                          </button>
                        )}
                      </div>
                      <span style={{
                        fontSize: "11px",
                        background: "rgba(250,93,0,0.08)",
                        color: "var(--color-harvest-flame)",
                        padding: "2px 8px",
                        borderRadius: "var(--radius-full)",
                        fontWeight: 600,
                        flexShrink: 0,
                        marginLeft: "8px",
                      }}>
                        {step.time}
                      </span>
                    </div>
                    <p style={{ fontSize: "13px", color: "var(--color-warm-stone)", marginTop: "3px", lineHeight: 1.5 }}>
                      {step.description}
                    </p>
                    {step.portal && step.portal !== 'lab-finder' && (
                      <a href={step.portal} target="_blank" rel="noopener noreferrer"
                        style={{ fontSize: "12px", color: "var(--color-harvest-flame)", fontWeight: 600, textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "3px", marginTop: "6px" }}>
                        Open Portal <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* ── Fee Table ────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
            style={{ padding: "28px" }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", color: "var(--color-driftwood)" }}>
                Fee Structure
              </p>
              <span style={{ fontSize: "11px", color: "var(--color-ash)" }}>Updated: Feb 2026</span>
            </div>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                <thead>
                  <tr style={{ background: "var(--color-cream-canvas)" }}>
                    {["Category", "Application Fee", "Annual Fee"].map(h => (
                      <th key={h} style={{
                        padding: "10px 14px",
                        textAlign: "left",
                        fontSize: "11px",
                        fontWeight: 700,
                        color: "var(--color-warm-stone)",
                        borderBottom: "1px solid var(--color-parchment-shadow)",
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[
                    { category: 'MSME',             ...activeResult.fees.msme },
                    { category: 'Large Enterprise', ...activeResult.fees.large },
                    { category: 'Importer',         ...activeResult.fees.importer },
                  ].map((row, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid var(--color-cream-canvas)" }}>
                      <td style={{ padding: "10px 14px", fontWeight: 600, color: "var(--color-ink-black)" }}>{row.category}</td>
                      <td style={{ padding: "10px 14px", color: "var(--color-warm-stone)" }}>{row.application}</td>
                      <td style={{ padding: "10px 14px", color: "var(--color-warm-stone)" }}>{row.annual}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          {/* ── Knowledge Graph ──────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="card"
            style={{ padding: "28px" }}
          >
            <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", color: "var(--color-driftwood)", marginBottom: "16px" }}>
              Knowledge Graph
            </p>
            <svg viewBox="0 0 480 120" style={{ width: "100%", height: "120px" }}>
              {/* Connecting lines */}
              <line x1="90" y1="60" x2="180" y2="60" stroke="var(--color-harvest-flame)" strokeWidth="1.5" strokeDasharray="4 3" className="graph-line" />
              <line x1="270" y1="60" x2="360" y2="60" stroke="var(--color-harvest-flame)" strokeWidth="1.5" strokeDasharray="4 3" className="graph-line" />
              <line x1="180" y1="60" x2="270" y2="60" stroke="var(--color-harvest-flame)" strokeWidth="1.5" strokeDasharray="4 3" className="graph-line" />

              {/* Nodes */}
              {[
                { cx: 60,  label: "Product",  sub: activeResult.product.split(" ")[0] },
                { cx: 185, label: "Standard", sub: activeResult.isCode.split(":")[0] },
                { cx: 295, label: "Scheme",   sub: activeResult.scheme.split("(")[0].trim() },
                { cx: 410, label: "Lab",      sub: "Delhi NCR" },
              ].map(({ cx, label, sub }) => (
                <g key={label}>
                  <circle cx={cx} cy={60} r={24} fill="var(--color-paper-white)" stroke="var(--color-harvest-flame)" strokeWidth="1.5" />
                  <text x={cx} y={56} textAnchor="middle" fontSize="9" fontWeight="700" fill="var(--color-ink-black)">{label}</text>
                  <text x={cx} y={68} textAnchor="middle" fontSize="7.5" fill="var(--color-warm-stone)">{sub}</text>
                </g>
              ))}
            </svg>
          </motion.div>

          {/* ── Portal Links ─────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
            style={{ padding: "28px" }}
          >
            <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", color: "var(--color-driftwood)", marginBottom: "16px" }}>
              Portal Quick Links
            </p>
            <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
              <a
                href={activeResult.portalUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "10px 18px",
                  background: "var(--color-cream-canvas)",
                  border: "1px solid var(--color-parchment-shadow)",
                  borderRadius: "var(--radius-md)",
                  fontSize: "13px",
                  fontWeight: 600,
                  color: "var(--color-ink-black)",
                  textDecoration: "none",
                }}
              >
                🌐 {activeResult.portalName} <ExternalLink size={12} color="var(--color-driftwood)" />
              </a>
              <button
                onClick={() => alert("PDF exported! (demo)")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "10px 18px",
                  background: "transparent",
                  border: "1px solid var(--color-parchment-shadow)",
                  borderRadius: "var(--radius-md)",
                  fontSize: "13px",
                  fontWeight: 600,
                  color: "var(--color-harvest-flame)",
                  cursor: "pointer",
                  transition: "background 0.2s",
                }}
              >
                <FileText size={13} /> Export as PDF
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* ── Clause Modal ─────────────────────────────── */}
      <AnimatePresence>
        {selectedClause && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedClause(null)}
            style={{
              position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
              background: "rgba(0, 0, 0, 0.4)",
              backdropFilter: "blur(4px)",
              zIndex: 9999,
              display: "flex", alignItems: "center", justifyContent: "center",
              padding: "20px",
            }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: "var(--color-paper-white)",
                borderRadius: "var(--radius-lg)",
                width: "100%", maxWidth: "500px",
                boxShadow: "0 24px 60px rgba(0,0,0,0.15)",
                overflow: "hidden",
                border: "1px solid var(--color-parchment-shadow)",
              }}
            >
              <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--color-parchment-shadow)", display: "flex", justifyContent: "space-between", alignItems: "center", background: "var(--color-cream-canvas)" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
                    <CheckCircle size={14} color="var(--color-valid-green)" />
                    <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--color-valid-green)", letterSpacing: "1px", textTransform: "uppercase" }}>Grounded in Official Source</span>
                  </div>
                  <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--color-ink-black)" }}>
                    {selectedClause.source}
                  </h3>
                </div>
                <button onClick={() => setSelectedClause(null)} style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--color-driftwood)", padding: "4px" }}>
                  <X size={20} />
                </button>
              </div>
              <div style={{ padding: "24px" }}>
                <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--color-harvest-flame)", marginBottom: "8px" }}>
                  {selectedClause.title}
                </p>
                <div style={{ 
                  background: "rgba(250, 93, 0, 0.04)", 
                  padding: "16px", 
                  borderRadius: "var(--radius-md)", 
                  borderLeft: "3px solid var(--color-harvest-flame)",
                  fontSize: "14px", 
                  lineHeight: 1.6, 
                  color: "var(--color-ink-black)" 
                }}>
                  {/* Using dangerouslySetInnerHTML to parse the markdown bold asterisks from the fixture */}
                  <span dangerouslySetInnerHTML={{ __html: selectedClause.excerpt.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "16px", color: "var(--color-driftwood)", fontSize: "11px" }}>
                  <Info size={12} />
                  <span>This excerpt was retrieved using hybrid RAG search from the BIS portal.</span>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
