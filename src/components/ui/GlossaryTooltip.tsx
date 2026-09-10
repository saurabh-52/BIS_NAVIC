"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Info } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { GlossaryTerm, getGlossaryDef } from "@/lib/glossary";

interface Props {
  term: GlossaryTerm;
  children: React.ReactNode;
}

export default function GlossaryTooltip({ term, children }: Props) {
  const { language } = useAppStore();
  const [isOpen, setIsOpen] = useState(false);
  const def = getGlossaryDef(term, language);

  return (
    <span 
      style={{ position: "relative", display: "inline-block" }}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
      onClick={() => setIsOpen(!isOpen)}
    >
      <span style={{ 
        borderBottom: "1.5px dotted var(--color-harvest-flame)", 
        cursor: "help",
        color: "inherit",
        display: "inline-flex",
        alignItems: "center",
        gap: "2px"
      }}>
        {children}
      </span>

      <AnimatePresence>
        {isOpen && (
          <motion.span
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 350, damping: 25 }}
            style={{
              position: "absolute",
              bottom: "100%",
              left: "50%",
              transform: "translateX(-50%)",
              marginBottom: "8px",
              width: "max-content",
              maxWidth: "280px",
              background: "var(--color-ink-black)",
              color: "var(--color-paper-white)",
              padding: "16px",
              borderRadius: "var(--radius-md)",
              boxShadow: "var(--shadow-lg)",
              zIndex: 9999,
              pointerEvents: "none",
              textAlign: "left",
              display: "block",
            }}
          >
            <span style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "6px" }}>
              <Info size={14} color="var(--color-harvest-flame)" />
              <strong style={{ fontSize: "14px", fontWeight: 700 }}>
                {def.title}
              </strong>
            </span>
            <span style={{ display: "block", fontSize: "12px", lineHeight: 1.5, opacity: 0.9, margin: 0, whiteSpace: "normal" }}>
              {def.desc}
            </span>

            {/* Triangle pointer */}
            <span style={{
              display: "block",
              position: "absolute",
              bottom: "-6px",
              left: "50%",
              transform: "translateX(-50%)",
              width: 0,
              height: 0,
              borderLeft: "6px solid transparent",
              borderRight: "6px solid transparent",
              borderTop: "6px solid var(--color-ink-black)",
            }} />
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  );
}

const TERMS_MAP: Record<string, GlossaryTerm> = {
  "CM/L": "CML",
  "CRS": "CRS",
  "ISI": "ISI",
  "HUID": "HUID",
  "Eco Mark": "ECOMARK",
  "MSME": "MSME",
  "R-Number": "R_NUMBER",
  "R-नंबर": "R_NUMBER",
  "FMCS": "FMCS",
};

export function HighlightTerms({ text }: { text: string }) {
  if (!text) return null;
  const terms = Object.keys(TERMS_MAP);
  // Sort by length descending to match longest terms first (e.g., "Eco Mark" before "Eco")
  terms.sort((a, b) => b.length - a.length);
  
  const regex = new RegExp(`(${terms.join("|")})`, 'g');
  const parts = text.split(regex);
  
  return (
    <>
      {parts.map((part, i) => {
        const matchedTerm = TERMS_MAP[part];
        if (matchedTerm) {
          return (
            <GlossaryTooltip key={i} term={matchedTerm}>
              {part}
            </GlossaryTooltip>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}
