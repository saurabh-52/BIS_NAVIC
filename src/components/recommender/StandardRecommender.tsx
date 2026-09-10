"use client";

import { motion } from "framer-motion";
import { Info, BookOpen, AlertCircle, CheckCircle2 } from "lucide-react";
import { StandardData } from "@/lib/standardsFixtures";
import { useAppStore } from "@/store/useAppStore";
import { t } from "@/lib/translations";

interface StandardRecommenderProps {
  standards: StandardData[];
}

export default function StandardRecommender({ standards }: StandardRecommenderProps) {
  const { language } = useAppStore();
  
  if (!standards || standards.length === 0) return null;

  return (
    <div style={{ marginBottom: "32px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
        <BookOpen size={18} color="var(--color-harvest-flame)" />
        <h3 style={{ fontSize: "16px", fontWeight: 700, color: "var(--color-ink-black)" }}>
          {language === "hi" ? "अनुशंसित IS कोड" : "Recommended IS Codes"}
        </h3>
      </div>
      
      {/* Horizontal Scroll Container */}
      <div style={{ 
        display: "flex", 
        gap: "16px", 
        overflowX: "auto", 
        paddingBottom: "16px",
        marginRight: "-32px",
        paddingRight: "32px",
        scrollbarWidth: "none", // Firefox
        msOverflowStyle: "none" // IE
      }}>
        <style>{`
          div::-webkit-scrollbar {
            display: none;
          }
        `}</style>
        
        {standards.map((std, idx) => (
          <motion.div
            key={std.isCode}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1, type: "spring" }}
            whileHover={{ y: -4, boxShadow: "var(--shadow-md)" }}
            style={{
              minWidth: "300px",
              maxWidth: "320px",
              background: "var(--color-paper-white)",
              border: "1px solid var(--color-parchment-shadow)",
              borderRadius: "var(--radius-lg)",
              padding: "20px",
              flexShrink: 0,
              display: "flex",
              flexDirection: "column",
              boxShadow: "var(--shadow-sm)",
              transition: "box-shadow 0.2s"
            }}
          >
            {/* Badge */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
              <div style={{
                fontSize: "11px",
                fontWeight: 700,
                padding: "4px 8px",
                borderRadius: "var(--radius-sm)",
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                background: std.type === "Mandatory" ? "rgba(250,93,0,0.1)" : "rgba(75,85,99,0.06)",
                color: std.type === "Mandatory" ? "var(--color-harvest-flame)" : "var(--color-warm-stone)",
                display: "flex",
                alignItems: "center",
                gap: "4px"
              }}>
                {std.type === "Mandatory" ? <AlertCircle size={12} /> : <Info size={12} />}
                {std.type}
              </div>
            </div>

            {/* Code & Title */}
            <h4 style={{ fontSize: "16px", fontWeight: 800, color: "var(--color-ink-black)", marginBottom: "4px" }}>
              {std.isCode}
            </h4>
            <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--color-warm-stone)", marginBottom: "12px", lineHeight: 1.4 }}>
              {std.title}
            </p>

            {/* Description */}
            <p style={{ fontSize: "12px", color: "var(--color-driftwood)", lineHeight: 1.5, marginTop: "auto" }}>
              {std.description}
            </p>
            
          </motion.div>
        ))}
      </div>
    </div>
  );
}
