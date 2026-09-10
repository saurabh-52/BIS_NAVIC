"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Search, BrainCircuit, FileSearch, Route, CheckCircle2, Loader2, Sparkles } from "lucide-react";
import { t } from "@/lib/translations";
import { useAppStore } from "@/store/useAppStore";

type TraceNode = {
  id: string;
  icon: React.ReactNode;
  labelKey: string;
};

const DEFAULT_NODES: TraceNode[] = [
  { id: "query", icon: <Search size={18} />, labelKey: "trace.query" },
  { id: "triage", icon: <BrainCircuit size={18} />, labelKey: "trace.triage" },
  { id: "expert", icon: <Sparkles size={18} />, labelKey: "trace.expert.isi" }, // Dynamic later
  { id: "rag", icon: <FileSearch size={18} />, labelKey: "trace.rag" },
  { id: "roadmap", icon: <Route size={18} />, labelKey: "trace.roadmap" },
];

export function classifyExpert(input: string) {
  const lower = input.toLowerCase();
  if (lower.includes("hallmark") || lower.includes("gold") || lower.includes("huid")) return "trace.expert.hallmark";
  if (lower.includes("crs") || lower.includes("electronics") || lower.includes("r-number")) return "trace.expert.crs";
  if (lower.includes("lab") || lower.includes("test")) return "trace.expert.lab";
  return "trace.expert.isi";
}

interface Props {
  query: string;
  onComplete: () => void;
}

export default function AgentTracePanel({ query, onComplete }: Props) {
  const { language } = useAppStore();
  const [activeNode, setActiveNode] = useState(0);
  const [nodes, setNodes] = useState<TraceNode[]>(DEFAULT_NODES);

  useEffect(() => {
    // Dynamically set the expert agent label based on query
    const expertKey = classifyExpert(query);
    const dynamicNodes = [...DEFAULT_NODES];
    dynamicNodes[2] = { ...dynamicNodes[2], labelKey: expertKey };
    setNodes(dynamicNodes);

    // Stagger progression: each node takes ~600ms
    const interval = setInterval(() => {
      setActiveNode(prev => {
        if (prev >= dynamicNodes.length - 1) {
          clearInterval(interval);
          setTimeout(onComplete, 500); // Wait a beat after finishing before calling complete
          return prev + 1;
        }
        return prev + 1;
      });
    }, 600);

    return () => clearInterval(interval);
  }, [query, onComplete]);

  return (
    <div style={{
      background: "var(--color-paper-white)",
      border: "1px solid var(--color-parchment-shadow)",
      borderRadius: "var(--radius-lg)",
      padding: "24px",
      margin: "16px 0",
      boxShadow: "0 4px 12px rgba(0,0,0,0.02)"
    }}>
      <p style={{ fontSize: "12px", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", color: "var(--color-driftwood)", marginBottom: "20px" }}>
        {t("trace.title", language)}
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {nodes.map((node, i) => {
          const isPending = i > activeNode;
          const isActive = i === activeNode;
          const isDone = i < activeNode;

          return (
            <motion.div
              key={node.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              style={{
                display: "flex", alignItems: "center", gap: "16px",
                opacity: isPending ? 0.4 : 1,
                color: isDone ? "var(--color-ink-black)" : isActive ? "var(--color-harvest-flame)" : "var(--color-warm-stone)"
              }}
            >
              <div style={{
                width: "32px", height: "32px", borderRadius: "50%",
                background: isDone ? "rgba(16, 185, 129, 0.1)" : isActive ? "rgba(250, 93, 0, 0.1)" : "var(--color-cream-canvas)",
                display: "flex", alignItems: "center", justifyContent: "center",
                color: isDone ? "var(--color-valid-green)" : isActive ? "var(--color-harvest-flame)" : "var(--color-driftwood)",
              }}>
                {isDone ? <CheckCircle2 size={16} /> : isActive ? <Loader2 size={16} className="lucide-spin" style={{ animation: "spin 1.5s linear infinite" }} /> : node.icon}
              </div>
              
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: "14px", fontWeight: isActive || isDone ? 600 : 500 }}>
                  {t(node.labelKey, language)}
                </p>
                {isActive && (
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ duration: 0.6, ease: "linear" }}
                    style={{
                      height: "2px",
                      background: "var(--color-harvest-flame)",
                      width: "40px",
                      marginTop: "4px",
                      transformOrigin: "left"
                    }}
                  />
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
