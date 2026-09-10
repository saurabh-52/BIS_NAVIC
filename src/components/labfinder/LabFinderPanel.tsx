"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { X, Search, MapPin, Phone, Navigation, Clock, DollarSign, CheckCircle, Filter } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { mockLabs } from "@/services/mockData";

const FILTERS = ["NABL Accredited", "BIS Recognized", "Available Now", "Electronics", "Chemical", "Mechanical"];

export default function LabFinderPanel() {
  const { isLabFinderOpen, setLabFinderOpen } = useAppStore();
  const [search, setSearch] = useState("");
  const [activeFilters, setActiveFilters] = useState<string[]>([]);

  const toggleFilter = (f: string) => {
    setActiveFilters(prev => prev.includes(f) ? prev.filter(x => x !== f) : [...prev, f]);
  };

  const filtered = mockLabs.filter(lab => {
    const matchesSearch = !search ||
      lab.name.toLowerCase().includes(search.toLowerCase()) ||
      lab.city.toLowerCase().includes(search.toLowerCase());
    const matchesFilters = activeFilters.every(f => {
      if (f === "NABL Accredited")  return lab.nabl;
      if (f === "BIS Recognized")   return lab.bisRecognized;
      if (f === "Available Now")    return lab.available;
      if (f === "Electronics")      return lab.testScopes.includes("Electronics") || lab.testScopes.includes("IT Equipment");
      if (f === "Chemical")         return lab.testScopes.includes("Chemical");
      if (f === "Mechanical")       return lab.testScopes.includes("Physical Testing");
      return true;
    });
    return matchesSearch && matchesFilters;
  });

  return (
    <AnimatePresence>
      {isLabFinderOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(29,30,28,0.5)",
            backdropFilter: "blur(4px)",
            zIndex: 9999, // very high
            display: "flex",
            justifyContent: "flex-end", // Align to right
          }}
          onClick={() => setLabFinderOpen(false)}
        >
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            onClick={e => e.stopPropagation()}
            style={{
              background: "var(--color-paper-white)",
              boxShadow: "var(--shadow-lg)",
              width: "100%",
              maxWidth: "500px", // Side panel width
              height: "100vh",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            {/* Header */}
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "20px 24px",
              borderBottom: "1px solid var(--color-parchment-shadow)",
            }}>
              <h2 style={{ fontSize: "16px", fontWeight: 700, color: "var(--color-ink-black)", display: "flex", alignItems: "center", gap: "8px" }}>
                <MapPin size={16} color="var(--color-harvest-flame)" /> Find Nearest Testing Lab
              </h2>
              <button
                onClick={() => setLabFinderOpen(false)}
                style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--color-driftwood)" }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Search + Filters */}
            <div style={{ padding: "16px 24px", borderBottom: "1px solid var(--color-parchment-shadow)" }}>
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                border: "1px solid var(--color-bone)",
                borderRadius: "var(--radius-md)",
                padding: "10px 14px",
                marginBottom: "12px",
                background: "var(--color-cream-canvas)",
              }}>
                <Search size={15} color="var(--color-driftwood)" />
                <input
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search by city or lab name..."
                  style={{
                    flex: 1,
                    background: "transparent",
                    border: "none",
                    outline: "none",
                    fontSize: "14px",
                    color: "var(--color-ink-black)",
                  }}
                />
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Filter size={12} color="var(--color-driftwood)" />
                {FILTERS.map(f => (
                  <button
                    key={f}
                    onClick={() => toggleFilter(f)}
                    className={activeFilters.includes(f) ? "pill active" : "pill"}
                    style={{ fontSize: "11px" }}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            {/* Labs list */}
            <div style={{ flex: 1, overflowY: "auto", padding: "16px 24px", display: "flex", flexDirection: "column", gap: "12px" }}>
              {filtered.map((lab, i) => (
                <motion.div
                  key={lab.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  style={{
                    padding: "18px",
                    background: "var(--color-cream-canvas)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--color-parchment-shadow)",
                    transition: "border-color 0.2s",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                    <div>
                      <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--color-ink-black)" }}>{lab.name}</p>
                      <p style={{ fontSize: "12px", color: "var(--color-driftwood)", display: "flex", alignItems: "center", gap: "4px", marginTop: "2px" }}>
                        <MapPin size={11} /> {lab.city}, {lab.state} · {lab.distance}
                      </p>
                    </div>
                    {lab.bisRecognized && (
                      <span className="badge-valid" style={{ flexShrink: 0 }}>
                        <CheckCircle size={10} /> BIS Recognized
                      </span>
                    )}
                  </div>

                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "10px" }}>
                    {lab.testScopes.map(s => (
                      <span key={s} className="pill" style={{ fontSize: "11px", cursor: "default" }}>{s}</span>
                    ))}
                  </div>

                  <div style={{ display: "flex", gap: "16px", marginBottom: "12px", fontSize: "12px", color: "var(--color-driftwood)" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: "4px" }}><Clock size={11} /> {lab.turnaround}</span>
                    <span style={{ display: "flex", alignItems: "center", gap: "4px" }}><DollarSign size={11} /> {lab.feeRange}</span>
                    {lab.nabl && <span style={{ fontWeight: 700, color: "var(--color-warm-stone)" }}>NABL</span>}
                  </div>

                  <div style={{ display: "flex", gap: "8px" }}>
                    <a href={`tel:${lab.contact}`} className="btn-ghost" style={{ fontSize: "12px", display: "flex", alignItems: "center", gap: "5px", textDecoration: "none" }}>
                      <Phone size={12} /> Contact
                    </a>
                    <button className="btn-ghost" style={{ fontSize: "12px", display: "flex", alignItems: "center", gap: "5px" }}>
                      <Navigation size={12} /> Get Directions
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Map View */}
            <div style={{ padding: "16px 24px", borderTop: "1px solid var(--color-parchment-shadow)", background: "var(--color-cream-canvas)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <p style={{ fontSize: "14px", fontWeight: 700, color: "var(--color-ink-black)" }}>Live Map View</p>
                <span style={{ fontSize: "11px", color: "var(--color-valid-green)", display: "flex", alignItems: "center", gap: "4px" }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "currentColor", animation: "pulse 2s infinite" }}></span>
                  Detecting location
                </span>
              </div>
              <div style={{
                height: "180px",
                background: "var(--color-parchment-shadow)",
                borderRadius: "var(--radius-md)",
                overflow: "hidden",
                border: "1px solid var(--color-bone)"
              }}>
                <iframe
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  loading="lazy"
                  allowFullScreen
                  src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d112000.34440076296!2d77.1024902!3d28.6472799!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390cfd5b347eb62d%3A0x37205b715389640!2sDelhi!5e0!3m2!1sen!2sin!4v1689230000000!5m2!1sen!2sin"
                ></iframe>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
