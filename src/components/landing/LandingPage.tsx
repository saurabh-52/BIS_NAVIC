"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { useRouter } from "next/navigation";
import OtpLoginModal from "@/components/auth/OtpLoginModal";
import { t } from "@/lib/translations";
import { HighlightTerms } from "@/components/ui/GlossaryTooltip";
import {
  Compass, Plus, ChevronDown, Globe,
  ArrowRight, ShieldCheck, ExternalLink, CheckCircle2,
} from "lucide-react";

/* ─────────────────────────────────────────────────────── */

const STATS = [
  { icon: "📋", value: "20,000+", label: "IS Standards" },
  { icon: "🏅", value: "5",       label: "Certification Schemes" },
  { icon: "🔬", value: "500+",    label: "Recognized Labs" },
  { icon: "🌐", value: "10+",     label: "Indian Languages" },
];

const PERSONAS = [
  {
    id: "manufacturer",
    icon: "🏭",
    label: "Manufacturer",
    sub: "MSME / Startup / Enterprise",
    desc: "Find which BIS scheme applies to your product, get exact IS codes, compliance steps, fees, and nearest testing labs.",
    bullets: [
      "IS code & scheme identification",
      "Step-by-step certification roadmap",
      "MSME fee concessions",
    ],
    cta: "Start as Manufacturer",
  },
  {
    id: "importer",
    icon: "📦",
    label: "Importer",
    sub: "Foreign Manufacturer / Trader",
    desc: "Check CRS/ISI mandatory compliance for products entering India. Understand import-specific documentation and BIS registration.",
    bullets: [
      "CRS mandatory product check",
      "Import registration guidance",
      "Foreign manufacturer BIS process",
    ],
    cta: "Start as Importer",
  },
  {
    id: "consumer",
    icon: "👤",
    label: "Consumer",
    sub: "Buyer / End User",
    desc: "Verify ISI marks, CRS registrations, Hallmark HUIDs, and Eco Mark certificates before purchasing any product.",
    bullets: [
      "Instant ISI/CRS verification",
      "Hallmark HUID lookup",
      "Eco Mark certificate check",
    ],
    cta: "Start as Consumer",
  },
];

const IMPACTS = [
  { icon: "⏱️", value: "70%",  label: "Faster Compliance Discovery", sub: "For MSMEs & Startups" },
  { icon: "📉", value: "60%",  label: "Less Helpdesk Load",          sub: "For BIS & Government" },
  { icon: "✅", value: "100%", label: "Consumer Trust",              sub: "Via Instant Verification" },
  { icon: "🚀", value: "Zero", label: "Compliance Mistakes",         sub: "For Startups entering India" },
];

/* ─────────────────────────────────────────────────────── */

export default function LandingPage() {
  const { language, setLanguage, setPersona } = useAppStore();
  const router = useRouter();
  const [showLogin, setShowLogin] = useState(false);
  const [langOpen, setLangOpen] = useState(false);

  const handlePersonaClick = (id: string) => {
    setPersona(id as "manufacturer" | "importer" | "consumer");
    setShowLogin(true);
  };

  return (
    <div style={{ background: "var(--color-cream-canvas)", minHeight: "100vh", fontFamily: "var(--font-sans)" }}>

      {/* ══════════════════════════════════════════════
          NAVBAR
      ══════════════════════════════════════════════ */}
      <nav style={{
        position: "sticky",
        top: 0,
        zIndex: 100,
        background: "var(--color-paper-white)",
        borderBottom: "1px solid var(--color-parchment-shadow)",
      }}>
        <div style={{
          maxWidth: "1160px",
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

          {/* Spacer */}
          <div style={{ flex: 1 }} />

          {/* Right controls */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>

            {/* Lang */}
            <div style={{ position: "relative" }}>
              <button
                onClick={() => setLangOpen(v => !v)}
                style={{
                  display: "flex", alignItems: "center", gap: "5px",
                  padding: "6px 12px",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--color-parchment-shadow)",
                  background: "transparent",
                  fontSize: "13px", color: "var(--color-warm-stone)",
                  cursor: "pointer",
                }}
              >
                {language === "en" ? "EN" : "HI"} <ChevronDown size={13} />
              </button>
              <AnimatePresence>
                {langOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 6 }}
                    style={{
                      position: "absolute", right: 0, top: "calc(100% + 6px)",
                      background: "var(--color-paper-white)",
                      border: "1px solid var(--color-parchment-shadow)",
                      borderRadius: "var(--radius-lg)",
                      boxShadow: "var(--shadow-sm)",
                      overflow: "hidden",
                      zIndex: 200,
                      minWidth: "120px",
                    }}
                  >
                    {["en", "hi"].map(l => (
                      <button key={l} onClick={() => { setLanguage(l as "en" | "hi"); setLangOpen(false); }}
                        style={{
                          width: "100%", textAlign: "left", padding: "9px 16px",
                          fontSize: "13px", color: l === language ? "var(--color-harvest-flame)" : "var(--color-ink-black)",
                          background: "transparent", border: "none", cursor: "pointer",
                          fontWeight: l === language ? 600 : 400,
                        }}>
                        {l === "en" ? "English" : "हिंदी"}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Login */}
            <button
              onClick={() => setShowLogin(true)}
              style={{
                padding: "6px 16px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-parchment-shadow)",
                background: "transparent",
                fontSize: "14px", fontWeight: 500,
                color: "var(--color-ink-black)",
                cursor: "pointer",
              }}
            >
              {t("nav.login", language)}
            </button>

          </div>
        </div>
      </nav>

      {/* ══════════════════════════════════════════════
          HERO
      ══════════════════════════════════════════════ */}
      <section style={{
        maxWidth: "1160px",
        margin: "0 auto",
        padding: "72px 32px 56px",
        textAlign: "center",
        position: "relative",
      }}>

        {/* SIH badge */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            display: "inline-flex", alignItems: "center", gap: "6px",
            padding: "5px 14px",
            borderRadius: "var(--radius-full)",
            background: "rgba(250,93,0,0.08)",
            border: "1px solid rgba(250,93,0,0.2)",
            fontSize: "12px", fontWeight: 600,
            color: "var(--color-harvest-flame)",
            marginBottom: "28px",
          }}
        >
          {t("landing.badge", language)}
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08 }}
          style={{
            fontFamily: "var(--font-display, Fraunces, Georgia, serif)",
            fontSize: "clamp(44px, 7vw, 72px)",
            fontWeight: 800,
            lineHeight: 1.12,
            color: "var(--color-ink-black)",
            marginBottom: "22px",
            letterSpacing: "-1px",
          }}
        >
          {t("landing.heroLine1", language)}{" "}
          <span style={{ color: "var(--color-harvest-flame)" }}>{t("landing.heroLine2", language)}</span>
          <br />{t("landing.heroLine3", language)}
        </motion.h1>

        {/* Sub */}
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.14 }}
          style={{
            fontSize: "18px",
            color: "var(--color-warm-stone)",
            lineHeight: 1.6,
            marginBottom: "10px",
          }}
        >
          {t("landing.sub", language)}{" "}
          <span style={{ color: "var(--color-harvest-flame)", fontWeight: 600 }}>{t("landing.subHighlight", language)}</span>
        </motion.p>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.18 }}
          style={{ fontSize: "13px", color: "var(--color-driftwood)", marginBottom: "36px" }}
        >
          {t("landing.desc", language)}
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22 }}
          style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "12px", marginBottom: "64px" }}
        >
          <button
            onClick={() => setShowLogin(true)}
            style={{
              display: "flex", alignItems: "center", gap: "8px",
              padding: "13px 28px",
              borderRadius: "var(--radius-md)",
              background: "var(--color-harvest-flame)",
              color: "#fff", border: "none",
              fontSize: "15px", fontWeight: 600,
              cursor: "pointer",
              boxShadow: "var(--shadow-lg)",
              transition: "background 0.2s",
            }}
          >
            {t("landing.startCompliance", language)} <ArrowRight size={15} />
          </button>

          <button
            onClick={() => setShowLogin(true)}
            style={{
              display: "flex", alignItems: "center", gap: "8px",
              padding: "12px 24px",
              borderRadius: "var(--radius-md)",
              background: "var(--color-paper-white)",
              color: "var(--color-ink-black)",
              border: "1.5px solid var(--color-parchment-shadow)",
              fontSize: "15px", fontWeight: 600,
              cursor: "pointer",
              transition: "border-color 0.2s",
            }}
          >
            <ShieldCheck size={15} color="var(--color-harvest-flame)" /> {t("landing.verifyProduct", language)}
          </button>
        </motion.div>

        {/* Floating preview cards */}
        <div style={{ position: "relative", height: "130px", maxWidth: "700px", margin: "0 auto" }}>
          {/* Left card */}
          <motion.div
            initial={{ opacity: 0, x: -30, y: 20, rotate: -6 }}
            animate={{ opacity: 1, x: 0, y: 0, rotate: -6 }}
            transition={{ delay: 0.3, type: "spring", damping: 22 }}
            style={{
              position: "absolute",
              left: "5%",
              top: "10px",
              background: "var(--color-paper-white)",
              borderRadius: "var(--radius-lg)",
              padding: "16px 20px",
              boxShadow: "0 12px 32px rgba(0,0,0,0.06)",
              textAlign: "left",
              minWidth: "220px",
              border: "1px solid var(--color-parchment-shadow)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
              <div style={{
                width: "24px", height: "24px",
                borderRadius: "50%",
                background: "rgba(250,93,0,0.1)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <span style={{ fontSize: "12px", color: "var(--color-harvest-flame)" }}>⚡</span>
              </div>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--color-ink-black)" }}>IS Code Found</span>
            </div>
            <p style={{ fontSize: "13px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "6px" }}>
              IS 16102:2018 — LED Bulbs
            </p>
            <span style={{
              fontSize: "11px", padding: "3px 10px",
              borderRadius: "var(--radius-full)",
              background: "rgba(250,93,0,0.1)",
              color: "var(--color-harvest-flame)",
              fontWeight: 600,
            }}>
              ⚙️ CRS Scheme-II
            </span>
            <p style={{ fontSize: "10px", color: "var(--color-driftwood)", marginTop: "8px" }}>
              Step 1: Apply at crsbis.in
            </p>
          </motion.div>

          {/* Right card */}
          <motion.div
            initial={{ opacity: 0, x: 30, y: 20, rotate: 6 }}
            animate={{ opacity: 1, x: 0, y: 0, rotate: 6 }}
            transition={{ delay: 0.4, type: "spring", damping: 22 }}
            style={{
              position: "absolute",
              right: "5%",
              top: "0px",
              background: "var(--color-paper-white)",
              borderRadius: "var(--radius-lg)",
              padding: "16px 20px",
              boxShadow: "0 12px 32px rgba(0,0,0,0.06)",
              textAlign: "left",
              minWidth: "230px",
              border: "1px solid var(--color-parchment-shadow)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
              <CheckCircle2 size={14} color="var(--color-valid-green)" />
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--color-valid-green)" }}>✓ Verified</span>
            </div>
            <p style={{ fontSize: "13px", fontWeight: 700, color: "var(--color-ink-black)", marginBottom: "6px" }}>
              IS 13252:2010 — Smartwatch
            </p>
            <span style={{
              fontSize: "11px", padding: "3px 10px",
              borderRadius: "var(--radius-full)",
              background: "rgba(250,93,0,0.1)",
              color: "var(--color-harvest-flame)",
              fontWeight: 600,
            }}>
              ⚙️ CRS Scheme-II
            </span>
            <p style={{ fontSize: "10px", color: "var(--color-driftwood)", marginTop: "8px" }}>
              Testing at STQC Lab
            </p>
          </motion.div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════
          STATS BAR
      ══════════════════════════════════════════════ */}
      <section style={{ padding: "0 32px 48px", maxWidth: "1160px", margin: "0 auto" }}>
        <div style={{
          background: "var(--color-paper-white)",
          borderRadius: "var(--radius-lg)",
          border: "1px solid var(--color-parchment-shadow)",
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
        }}>
          {STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              style={{
                padding: "32px 24px",
                textAlign: "center",
                borderRight: i < 3 ? "1px solid var(--color-parchment-shadow)" : "none",
              }}
            >
              <div style={{ fontSize: "28px", marginBottom: "8px" }}>{stat.icon}</div>
              <div style={{ fontSize: "32px", fontWeight: 800, color: "var(--color-harvest-flame)", lineHeight: 1, marginBottom: "6px" }}>
                {stat.value}
              </div>
              <div style={{ fontSize: "13px", color: "var(--color-driftwood)" }}>
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════
          WHO ARE YOU
      ══════════════════════════════════════════════ */}
      <section style={{ padding: "0 32px 64px", maxWidth: "1160px", margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: "36px" }}>
          <h2 style={{ fontSize: "32px", fontWeight: 800, color: "var(--color-ink-black)", marginBottom: "10px" }}>
            Who are you?
          </h2>
          <p style={{ fontSize: "15px", color: "var(--color-warm-stone)" }}>
            Select your role to get a personalized compliance roadmap
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px" }}>
          {PERSONAS.map((p, i) => (
            <motion.div
              key={p.id}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              whileHover={{ zIndex: 10 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              style={{
                position: "relative",
                zIndex: 1,
                background: "var(--color-paper-white)",
                borderRadius: "var(--radius-lg)",
                border: "1px solid var(--color-parchment-shadow)",
                padding: "28px 24px 24px",
                display: "flex",
                flexDirection: "column",
                gap: "0",
              }}
            >
              {/* Icon + title */}
              <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "6px" }}>
                <span style={{ fontSize: "28px" }}>{p.icon}</span>
                <div>
                  <p style={{ fontSize: "18px", fontWeight: 700, color: "var(--color-ink-black)", lineHeight: 1 }}>{t(`landing.persona.${p.id}.label`, language)}</p>
                  <p style={{ fontSize: "12px", color: "var(--color-driftwood)", marginTop: "2px" }}>{t(`landing.persona.${p.id}.sub`, language)}</p>
                </div>
              </div>

              {/* Description */}
              <p style={{ fontSize: "14px", color: "var(--color-warm-stone)", lineHeight: 1.6, margin: "14px 0 16px" }}>
                <HighlightTerms text={t(`landing.persona.${p.id}.desc`, language)} />
              </p>

              {/* Bullets */}
              <ul style={{ listStyle: "none", padding: 0, margin: "0 0 20px", display: "flex", flexDirection: "column", gap: "6px" }}>
                {[1, 2, 3].map(b => (
                  <li key={b} style={{ display: "flex", alignItems: "center", gap: "7px", fontSize: "13px", color: "var(--color-ironwood)" }}>
                    <CheckCircle2 size={13} color="var(--color-harvest-flame)" style={{ flexShrink: 0 }} />
                    <HighlightTerms text={t(`landing.persona.${p.id}.b${b}`, language)} />
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <button
                onClick={() => handlePersonaClick(p.id)}
                style={{
                  width: "100%",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: "6px",
                  padding: "12px",
                  borderRadius: "var(--radius-md)",
                  background: "var(--color-harvest-flame)",
                  color: "#fff", border: "none",
                  fontSize: "14px", fontWeight: 600,
                  cursor: "pointer",
                  marginTop: "auto",
                  boxShadow: "var(--shadow-sm)",
                  transition: "background 0.2s",
                }}
              >
                {t(`landing.persona.${p.id}.cta`, language)} <ArrowRight size={13} />
              </button>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════
          IMPACT STRIP
      ══════════════════════════════════════════════ */}
      <section style={{ padding: "0 32px 64px", maxWidth: "1160px", margin: "0 auto" }}>
        <div style={{
          background: "rgba(250,93,0,0.05)",
          border: "1px solid rgba(250,93,0,0.12)",
          borderRadius: "var(--radius-lg)",
          padding: "48px 40px",
        }}>
          <div style={{ textAlign: "center", marginBottom: "40px" }}>
            <h2 style={{ fontSize: "26px", fontWeight: 800, color: "var(--color-ink-black)", marginBottom: "8px" }}>
              {t("landing.impact.title", language)}
            </h2>
            <p style={{ fontSize: "14px", color: "var(--color-driftwood)" }}>
              {t("landing.impact.sub", language)}
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "24px" }}>
            {IMPACTS.map((item, i) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                style={{ textAlign: "center" }}
              >
                <div style={{
                  width: "48px", height: "48px",
                  borderRadius: "50%",
                  background: "rgba(250,93,0,0.1)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 12px",
                  fontSize: "20px",
                }}>
                  {item.icon}
                </div>
                <p style={{ fontSize: "36px", fontWeight: 800, color: "var(--color-harvest-flame)", lineHeight: 1, marginBottom: "6px" }}>
                  {item.value}
                </p>
                <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--color-ink-black)", marginBottom: "3px" }}>
                  {t(`landing.impact.${i+1}.label`, language)}
                </p>
                <p style={{ fontSize: "12px", color: "var(--color-driftwood)", lineHeight: 1.5 }}>
                  <HighlightTerms text={t(`landing.impact.${i+1}.sub`, language)} />
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════
          FOOTER
      ══════════════════════════════════════════════ */}
      <footer style={{
        background: "var(--color-paper-white)",
        borderTop: "1px solid var(--color-parchment-shadow)",
      }}>
        <div style={{
          maxWidth: "1160px",
          margin: "0 auto",
          padding: "32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "24px",
        }}>
          {/* Logo */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{
              width: "34px", height: "34px",
              background: "var(--color-harvest-flame)",
              borderRadius: "50%",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Compass size={16} color="#fff" />
            </div>
            <div>
              <div style={{ fontSize: "14px", fontWeight: 800, color: "var(--color-ink-black)" }}>
                BIS NAVIC
              </div>
              <div style={{ fontSize: "10px", color: "var(--color-driftwood)" }}>
                Team Nomadic Devs · SIH 2026
              </div>
            </div>
          </div>

          {/* Links */}
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            {[
              { label: t("landing.footer.c1", language), href: "/app" },
              { label: t("landing.footer.c2", language),   href: "/app?tab=verify" },
              { label: t("landing.footer.c3", language),       href: "https://bis.gov.in", ext: true },
            ].map(link => (
              <a
                key={link.label}
                href={link.href}
                target={link.ext ? "_blank" : undefined}
                rel={link.ext ? "noopener noreferrer" : undefined}
                style={{
                  fontSize: "13px",
                  color: "var(--color-warm-stone)",
                  textDecoration: "none",
                  display: "flex", alignItems: "center", gap: "3px",
                  transition: "color 0.2s",
                }}
              >
                {link.label}
                {link.ext && <ExternalLink size={11} />}
              </a>
            ))}
          </div>

          {/* WhatsApp */}
          <button style={{
            display: "flex", alignItems: "center", gap: "7px",
            padding: "9px 18px",
            borderRadius: "var(--radius-md)",
            border: "1.5px solid var(--color-parchment-shadow)",
            background: "transparent",
            fontSize: "13px", fontWeight: 600,
            color: "var(--color-ink-black)",
            cursor: "pointer",
          }}>
            {t("landing.footer.chat", language)}
          </button>
        </div>

        {/* Bottom strip */}
        <div style={{
          borderTop: "1px solid var(--color-parchment-shadow)",
          padding: "14px 32px",
          maxWidth: "1160px",
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <p style={{ fontSize: "12px", color: "var(--color-driftwood)" }}>
            © 2026 BIS NAVIC · Team Nomadic Devs · Prototype for SIH 2026
          </p>
          <p style={{ fontSize: "12px", color: "var(--color-driftwood)" }}>
            All BIS data is illustrative. Not an official BIS product.
          </p>
        </div>
      </footer>

      {/* OTP Modal — login button only */}
      <AnimatePresence>
        {showLogin && (
          <OtpLoginModal onSkip={() => setShowLogin(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}
