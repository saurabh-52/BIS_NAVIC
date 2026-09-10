"use client";

import { useState, useRef } from "react";
import { Mic, Sparkles, FlaskConical, LogIn } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAppStore } from "@/store/useAppStore";
import { runComplianceQuery } from "@/services/mockAgentService";
import AgentTracePanel from "./AgentTracePanel";
import type { PipelineStage, HistoryItem } from "@/services/mockData";
import { t } from "@/lib/translations";

const QUICK_QUERIES = [
  { icon: "⚙️", key: "chat.chip.1" },
  { icon: "💡", key: "chat.chip.2" },
  { icon: "💻", key: "chat.chip.3" },
  { icon: "🪖", key: "chat.chip.4" },
  { icon: "💍", key: "chat.chip.5" },
  { icon: "🌿", key: "chat.chip.6" },
];

const FULL_CHIPS = [
  "I want to sell smartwatches in India",
  "How do I certify LED bulbs?",
  "Is my imported laptop CRS compliant?",
  "Verify ISI mark on a helmet",
  "I want to hallmark gold jewellery",
  "I want an Eco Mark for my detergent",
];

const PERSONAS = [
  { id: "manufacturer", icon: "🏭", label: "Manufacturer" },
  { id: "importer",     icon: "📦", label: "Importer" },
  { id: "consumer",     icon: "👤", label: "Consumer" },
] as const;

export default function ChatPanel() {
  const {
    persona, language, setPersona,
    setPipelineStages, setActiveResult,
    addToHistory, setActiveTab, addToast,
    setLabFinderOpen,
  } = useAppStore();

  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [processingQuery, setProcessingQuery] = useState("");
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const q = query.trim();
    if (!q || loading) return;
    setLoading(true);
    setProcessingQuery(q);
    setQuery("");
  };

  const handleTraceComplete = async () => {
    try {
      const result = await runComplianceQuery(processingQuery, persona, language, (stages: PipelineStage[]) => {
        setPipelineStages(stages);
      });
      setActiveResult(result);
      addToHistory({ id: `h-${Date.now()}`, query: processingQuery, scheme: result.scheme, timestamp: "Just now", queryKey: result.id });
      setActiveTab("roadmap");
    } catch {
      addToast({ message: "Something went wrong. Please try again.", type: "error" });
    } finally {
      setLoading(false);
      setProcessingQuery("");
    }
  };

  const handleQuickQuery = (chip: string) => {
    setQuery(chip);
    textareaRef.current?.focus();
  };

  const handleMicClick = () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      addToast({ message: "Speech recognition is not supported in this browser.", type: "error" });
      return;
    }
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = language === "hi" ? "hi-IN" : "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setQuery(prev => prev + (prev ? " " : "") + transcript);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>

      {/* ── Panel Header ─────────────────────── */}
      <div style={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        marginBottom: "20px",
      }}>
        <div>
          <h2 style={{ fontSize: "16px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "3px" }}>
            {t("chat.title", language)}
          </h2>
          <p style={{ fontSize: "12px", color: "var(--color-driftwood)" }}>
            {t("chat.subtitle", language)}
          </p>
        </div>
        <button
          style={{
            display: "flex", alignItems: "center", gap: "5px",
            padding: "5px 12px",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--color-parchment-shadow)",
            background: "transparent",
            fontSize: "12px", fontWeight: 600,
            color: "var(--color-warm-stone)",
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          <LogIn size={12} /> {t("nav.login", language)}
        </button>
      </div>

      {/* ── YOUR ROLE ────────────────────────── */}
      <div style={{ marginBottom: "16px" }}>
        <p style={{
          fontSize: "10px",
          fontWeight: 700,
          letterSpacing: "0.9px",
          textTransform: "uppercase",
          color: "var(--color-driftwood)",
          marginBottom: "8px",
        }}>
          {t("chat.role", language)}
        </p>
        <div style={{ display: "flex", gap: "8px" }}>
          {PERSONAS.map(p => {
            const isActive = p.id === persona;
            return (
              <button
                key={p.id}
                onClick={() => setPersona(p.id)}
                style={{
                  display: "flex", alignItems: "center", gap: "5px",
                  padding: "6px 14px",
                  borderRadius: "var(--radius-full)",
                  fontSize: "12px",
                  fontWeight: isActive ? 700 : 500,
                  border: "1.5px solid",
                  cursor: "pointer",
                  transition: "all 0.18s ease",
                  borderColor: isActive ? "var(--color-harvest-flame)" : "var(--color-parchment-shadow)",
                  background: "transparent",
                  color: isActive ? "var(--color-harvest-flame)" : "var(--color-warm-stone)",
                }}
              >
                {p.icon} {t(`landing.persona.${p.id}.label`, language)}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Textarea ─────────────────────────── */}
      <div style={{ marginBottom: "12px", position: "relative" }}>
        <textarea
          ref={textareaRef}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => {
            if ((e.metaKey || e.ctrlKey) && e.key === "Enter") handleSubmit();
          }}
          placeholder={t("chat.placeholder", language)}
          rows={6}
          style={{
            width: "100%",
            background: "var(--color-cream-canvas)",
            border: "1px solid var(--color-parchment-shadow)",
            borderRadius: "var(--radius-md)",
            padding: "14px 16px 40px",
            fontSize: "14px",
            color: "var(--color-ink-black)",
            resize: "none",
            outline: "none",
            lineHeight: 1.65,
            fontFamily: "var(--font-sans)",
            transition: "border-color 0.2s",
          }}
          onFocus={e => (e.target.style.borderColor = "var(--color-harvest-flame)")}
          onBlur={e => (e.target.style.borderColor = "var(--color-parchment-shadow)")}
        />
        {/* Bottom bar inside textarea */}
        <div style={{
          position: "absolute",
          bottom: "10px",
          left: "12px",
          right: "12px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          pointerEvents: "none",
        }}>
          <button
            onClick={handleMicClick}
            className={isListening ? "pulse-anim" : ""}
            style={{
              background: isListening ? "rgba(250,93,0,0.1)" : "transparent",
              border: "none",
              color: isListening ? "var(--color-harvest-flame)" : "var(--color-driftwood)",
              cursor: "pointer",
              display: "flex", alignItems: "center",
              justifyContent: "center",
              pointerEvents: "all",
              width: "28px", height: "28px",
              borderRadius: "50%",
              transition: "all 0.2s",
            }}
          >
            <Mic size={14} />
            <style>{`
              @keyframes pulse-mic {
                0% { box-shadow: 0 0 0 0 rgba(250,93,0,0.4); }
                70% { box-shadow: 0 0 0 6px rgba(250,93,0,0); }
                100% { box-shadow: 0 0 0 0 rgba(250,93,0,0); }
              }
              .pulse-anim {
                animation: pulse-mic 1.5s infinite;
              }
            `}</style>
          </button>
          <span style={{ fontSize: "11px", color: "var(--color-driftwood)" }}>
            ⌘+Enter to submit
          </span>
        </div>
      </div>

      {/* ── Analyze Button ───────────────────── */}
      <button
        onClick={handleSubmit}
        disabled={loading || !query.trim()}
        style={{
          width: "100%",
          display: "flex", alignItems: "center", justifyContent: "center", gap: "7px",
          padding: "12px",
          borderRadius: "var(--radius-md)",
          background: query.trim() && !loading ? "var(--color-harvest-flame)" : "var(--color-parchment-shadow)",
          color: query.trim() && !loading ? "#fff" : "var(--color-driftwood)",
          border: "none",
          fontSize: "14px", fontWeight: 600,
          cursor: query.trim() && !loading ? "pointer" : "not-allowed",
          transition: "all 0.2s",
          marginBottom: "20px",
          boxShadow: query.trim() && !loading ? "var(--shadow-sm)" : "none",
        }}
      >
        {loading ? (
          <>
            <svg style={{ animation: "spin 1s linear infinite", flexShrink: 0 }} width="14" height="14" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" strokeDasharray="60 40" />
            </svg>
            Analyzing...
          </>
        ) : (
          <>
            <Sparkles size={14} />
            {t("chat.analyze", language)} →
          </>
        )}
      </button>

      {/* ── Dynamic Bottom Area ──────────────── */}
      <AnimatePresence mode="wait">
        {processingQuery ? (
          <motion.div key="trace" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
            <AgentTracePanel query={processingQuery} onComplete={handleTraceComplete} />
          </motion.div>
        ) : (
          <motion.div key="quick-queries" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {/* ── Quick Queries ────────────────────── */}
            <div style={{ marginBottom: "20px" }}>
              <p style={{
                fontSize: "10px",
                fontWeight: 700,
                letterSpacing: "0.9px",
                textTransform: "uppercase",
                color: "var(--color-driftwood)",
                marginBottom: "10px",
              }}>
                {t("chat.quickQueries", language)}
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "7px" }}>
                {QUICK_QUERIES.map((chip, i) => (
                  <button
                    key={i}
                    onClick={() => handleQuickQuery(FULL_CHIPS[i])}
                    style={{
                      display: "flex", alignItems: "center", gap: "6px",
                      padding: "8px 10px",
                      borderRadius: "var(--radius-full)",
                      border: "1px solid var(--color-parchment-shadow)",
                      background: "transparent",
                      fontSize: "11px",
                      color: "var(--color-ironwood)",
                      cursor: "pointer",
                      textAlign: "left",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      transition: "border-color 0.15s, background 0.15s",
                    }}
                    onMouseEnter={e => {
                      (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--color-harvest-flame)";
                      (e.currentTarget as HTMLButtonElement).style.background = "rgba(250,93,0,0.04)";
                    }}
                    onMouseLeave={e => {
                      (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--color-parchment-shadow)";
                      (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                    }}
                  >
                    <span style={{ fontSize: "14px" }}>{chip.icon}</span>
                    <span style={{ fontSize: "12px", color: "var(--color-ink-black)" }}>{t(chip.key, language)}</span>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>



      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
