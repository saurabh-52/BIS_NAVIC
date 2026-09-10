"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { Compass, ChevronDown, Plus, FlaskConical } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { motion, AnimatePresence } from "framer-motion";
import { t } from "@/lib/translations";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिंदी" },
  { code: "mr", label: "मराठी", soon: true },
  { code: "ta", label: "தமிழ்", soon: true },
  { code: "te", label: "తెలుగు", soon: true },
];

export default function Navbar() {
  const { language, setLanguage, activeTab, setActiveTab, setNewQuery, addToast, setLabFinderOpen } = useAppStore();
  const [langOpen, setLangOpen] = useState(false);
  const pathname = usePathname();

  const handleLangSelect = (code: string, soon?: boolean) => {
    if (soon) {
      addToast({ message: "Coming soon! More Indian languages are on the way.", type: "info" });
      setLangOpen(false);
      return;
    }
    setLanguage(code as "en" | "hi");
    setLangOpen(false);
  };

  const navLinks = [
    pathname === "/dashboard"
      ? { label: "← Back to Home", id: "home", href: "/", active: false }
      : { label: "← Back to Dashboard", id: "dashboard", href: "/dashboard", active: false }
  ];

  return (
    <nav
      style={{
        background: "var(--color-paper-white)",
        borderBottom: "1px solid var(--color-parchment-shadow)",
        position: "sticky",
        top: 0,
        zIndex: 50,
      }}
    >
      <div style={{
        maxWidth: "1440px",
        margin: "0 auto",
        padding: "0 32px",
        height: "64px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "32px",
      }}>

        {/* Logo */}
        <a href="/" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none", flexShrink: 0 }}>
          <div style={{
            width: "36px", height: "36px",
            background: "var(--color-harvest-flame)",
            borderRadius: "50%",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Compass size={18} color="#fff" />
          </div>
          <div>
            <div style={{ fontSize: "15px", fontWeight: 800, color: "var(--color-ink-black)", lineHeight: 1 }}>
              BIS <span style={{ color: "var(--color-harvest-flame)" }}>NAVIC</span>
            </div>
            <div style={{ fontSize: "10px", color: "var(--color-driftwood)", lineHeight: 1.2, marginTop: "2px" }}>
              Compliance Navigator
            </div>
          </div>
        </a>

        {/* Tabs — centre */}
        <div style={{ display: "flex", alignItems: "center", gap: "4px", position: "absolute", left: "50%", transform: "translateX(-50%)" }}>
          {navLinks.map(link => {
            const isLink = link.href;
            const content = (
              <span style={{
                padding: "6px 16px",
                borderRadius: "var(--radius-full)",
                fontSize: "14px",
                fontWeight: link.active ? 600 : 500,
                color: link.active ? "var(--color-harvest-flame)" : "var(--color-warm-stone)",
                background: link.active ? "rgba(250,93,0,0.08)" : "transparent",
                transition: "all 0.15s",
              }}>
                {link.label}
              </span>
            );

            if (isLink) {
              return (
                <a key={link.label} href={link.href} style={{ textDecoration: "none" }}>
                  {content}
                </a>
              );
            }

            return (
              <button
                key={link.label}
                onClick={() => setActiveTab(link.id as any)}
                style={{
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  padding: 0,
                  display: "flex",
                }}
              >
                {content}
              </button>
            );
          })}
        </div>

        {/* Right controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
          
          {/* Find Labs Button */}
          <button
            onClick={() => setLabFinderOpen(true)}
            style={{
              display: "flex", alignItems: "center", gap: "6px",
              padding: "6px 14px",
              borderRadius: "var(--radius-full)",
              border: "1px solid var(--color-parchment-shadow)",
              background: "var(--color-paper-white)",
              fontSize: "13px",
              fontWeight: 500,
              color: "var(--color-ink-black)",
              cursor: "pointer",
              transition: "all 0.2s",
              boxShadow: "0 2px 8px rgba(0,0,0,0.02)",
            }}
            onMouseOver={e => {
              e.currentTarget.style.borderColor = "var(--color-harvest-flame)";
              e.currentTarget.style.color = "var(--color-harvest-flame)";
            }}
            onMouseOut={e => {
              e.currentTarget.style.borderColor = "var(--color-parchment-shadow)";
              e.currentTarget.style.color = "var(--color-ink-black)";
            }}
          >
            <FlaskConical size={14} /> {t("chat.findLabs", language)}
          </button>

          {/* Language dropdown */}
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setLangOpen(v => !v)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
                padding: "6px 12px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-parchment-shadow)",
                background: "transparent",
                fontSize: "13px",
                color: "var(--color-warm-stone)",
                cursor: "pointer",
              }}
            >
              {language.toUpperCase()} <ChevronDown size={13} />
            </button>

            <AnimatePresence>
              {langOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 6 }}
                  transition={{ duration: 0.15 }}
                  style={{
                    position: "absolute",
                    right: 0,
                    top: "calc(100% + 6px)",
                    background: "var(--color-paper-white)",
                    border: "1px solid var(--color-parchment-shadow)",
                    borderRadius: "var(--radius-lg)",
                    boxShadow: "var(--shadow-sm)",
                    minWidth: "120px",
                    overflow: "hidden",
                    zIndex: 100,
                  }}
                >
                  {LANGUAGES.map(lang => (
                    <button
                      key={lang.code}
                      onClick={() => handleLangSelect(lang.code, lang.soon)}
                      style={{
                        width: "100%",
                        textAlign: "left",
                        padding: "9px 16px",
                        fontSize: "13px",
                        color: lang.code === language ? "var(--color-harvest-flame)" : "var(--color-ink-black)",
                        background: "transparent",
                        fontWeight: lang.code === language ? 600 : 400,
                        border: "none",
                        cursor: "pointer",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      {lang.label}
                      {lang.soon && (
                        <span style={{
                          fontSize: "10px",
                          background: "var(--color-cream-canvas)",
                          color: "var(--color-driftwood)",
                          padding: "2px 6px",
                          borderRadius: "var(--radius-full)",
                          border: "1px solid var(--color-parchment-shadow)",
                        }}>
                          Soon
                        </span>
                      )}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* New Query */}
          <button
            onClick={setNewQuery}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "5px",
              padding: "7px 16px",
              borderRadius: "var(--radius-md)",
              background: "var(--color-harvest-flame)",
              color: "var(--color-paper-white)",
              border: "none",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              boxShadow: "var(--shadow-sm)",
              transition: "background 0.2s",
            }}
          >
            <Plus size={14} />
            New Query
          </button>
        </div>
      </div>
    </nav>
  );
}
