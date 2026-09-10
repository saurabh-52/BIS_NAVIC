"use client";

import { motion } from "framer-motion";
import { CheckCircle, Circle, Loader2, Cpu } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";

const STAGE_ICONS = ["🎯", "🧩", "🔍", "🤖", "✅", "🗺️"];

export default function AgentPipelineLog() {
  const { pipelineStages } = useAppStore();
  if (!pipelineStages.length) return null;

  return (
    <div style={{
      background: "var(--color-paper-white)",
      borderRadius: "var(--radius-lg)",
      padding: "28px",
      boxShadow: "var(--shadow-sm)",
      marginBottom: "20px",
    }}>
      <h3 style={{
        fontSize: "14px",
        fontWeight: 700,
        color: "var(--color-ink-black)",
        marginBottom: "20px",
        display: "flex",
        alignItems: "center",
        gap: "8px",
      }}>
        <Cpu size={15} color="var(--color-harvest-flame)" />
        Agentic Pipeline
      </h3>

      <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
        {pipelineStages.map((stage, i) => {
          const isActive    = stage.status === "running";
          const isCompleted = stage.status === "done";
          const isPending   = stage.status === "pending";
          const isLast      = i === pipelineStages.length - 1;

          return (
            <div key={stage.id} style={{ display: "flex", gap: "12px" }}>
              {/* Connector line column */}
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "24px", flexShrink: 0 }}>
                <motion.div
                  initial={false}
                  animate={{
                    background: isCompleted || isActive
                      ? "var(--color-harvest-flame)"
                      : "var(--color-parchment-shadow)",
                    scale: isActive ? 1.15 : 1,
                  }}
                  transition={{ duration: 0.3 }}
                  style={{
                    width: "24px",
                    height: "24px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {isCompleted ? (
                    <CheckCircle size={14} color="#fff" />
                  ) : isActive ? (
                    <Loader2 size={12} color="#fff" className="animate-spin" style={{ animation: "spin 1s linear infinite" }} />
                  ) : (
                    <Circle size={12} color="var(--color-bone)" fill="none" />
                  )}
                </motion.div>
                {!isLast && (
                  <div style={{
                    width: "2px",
                    flex: 1,
                    minHeight: "16px",
                    background: isCompleted ? "var(--color-harvest-flame)" : "var(--color-parchment-shadow)",
                    margin: "3px 0",
                    transition: "background 0.3s",
                  }} />
                )}
              </div>

              {/* Stage content */}
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.12 }}
                style={{
                  paddingBottom: isLast ? "0" : "16px",
                  flex: 1,
                }}
              >
                <p style={{
                  fontSize: "13px",
                  fontWeight: 600,
                  color: isActive
                    ? "var(--color-harvest-flame)"
                    : isCompleted
                    ? "var(--color-ink-black)"
                    : "var(--color-driftwood)",
                  transition: "color 0.3s",
                  marginBottom: "2px",
                }}>
                  {STAGE_ICONS[i]} {stage.label}
                </p>
                {stage.detail && (
                  <p style={{
                    fontSize: "12px",
                    color: "var(--color-ash)",
                    lineHeight: 1.4,
                  }}>
                    {stage.detail}
                  </p>
                )}
              </motion.div>
            </div>
          );
        })}

        {/* Completion banner */}
        {pipelineStages.every(s => s.status === "done") && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            style={{
              marginTop: "12px",
              padding: "10px 14px",
              background: "rgba(250, 93, 0, 0.06)",
              border: "1px solid rgba(250, 93, 0, 0.2)",
              borderRadius: "var(--radius-sm)",
              fontSize: "13px",
              fontWeight: 600,
              color: "var(--color-harvest-flame)",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            ✅ Roadmap ready!
          </motion.div>
        )}
      </div>
    </div>
  );
}
