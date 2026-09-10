"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { X, Phone, KeyRound, ArrowRight } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { useRouter } from "next/navigation";
import { t } from "@/lib/translations";

interface Props {
  onSkip?: () => void;
}

export default function OtpLoginModal({ onSkip }: Props) {
  const { addToast, language } = useAppStore();
  const router = useRouter();
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");

  const handleSendOtp = () => {
    if (phone.length < 10) {
      addToast({ message: "Enter a valid 10-digit mobile number", type: "error" });
      return;
    }
    setStep("otp");
    addToast({ message: `OTP sent to +91 ${phone}`, type: "success" });
  };

  const handleVerify = () => {
    addToast({ message: "Logged in successfully!", type: "success" });
    router.push("/dashboard");
  };

  const handleClose = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (onSkip) onSkip();
  };

  const handleGuest = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    addToast({ message: "Logged in as Guest", type: "info" });
    router.push("/dashboard");
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(29, 30, 28, 0.5)",
        backdropFilter: "blur(4px)",
        zIndex: 200,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
      }}
      onClick={handleClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        onClick={e => e.stopPropagation()}
        style={{
          background: "var(--color-paper-white)",
          borderRadius: "var(--radius-lg)",
          padding: "40px",
          width: "100%",
          maxWidth: "400px",
          boxShadow: "var(--shadow-lg)",
        }}
      >
        {/* Close */}
        <button
          onClick={handleClose}
          style={{
            position: "absolute",
            top: "16px",
            right: "16px",
            background: "transparent",
            border: "none",
            cursor: "pointer",
            color: "var(--color-driftwood)",
          }}
        >
          <X size={18} />
        </button>

        {/* Icon */}
        <div style={{
          width: "52px",
          height: "52px",
          borderRadius: "var(--radius-lg)",
          background: "rgba(250,93,0,0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: "20px",
        }}>
          {step === "phone" ? (
            <Phone size={22} color="var(--color-harvest-flame)" />
          ) : (
            <KeyRound size={22} color="var(--color-harvest-flame)" />
          )}
        </div>

        <h2 style={{
          fontSize: "22px",
          fontWeight: 700,
          color: "var(--color-ink-black)",
          marginBottom: "6px",
        }}>
          {step === "phone" ? t("login.title", language) : "Enter OTP"}
        </h2>
        <p style={{ fontSize: "14px", color: "var(--color-warm-stone)", marginBottom: "28px" }}>
          {step === "phone"
            ? t("login.sub", language)
            : `OTP sent to +91 ${phone}. Enter any 4-digit code to continue.`}
        </p>

        <AnimatePresence mode="wait">
          {step === "phone" ? (
            <motion.div key="phone" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div style={{ position: "relative", marginBottom: "16px" }}>
                <span style={{
                  position: "absolute",
                  left: "14px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  fontSize: "14px",
                  fontWeight: 600,
                  color: "var(--color-ink-black)",
                }}>
                  +91
                </span>
                <input
                  type="tel"
                  maxLength={10}
                  value={phone}
                  onChange={e => setPhone(e.target.value.replace(/\D/g, ""))}
                  placeholder="98765 43210"
                  className="input-field"
                  style={{ paddingLeft: "48px" }}
                  onKeyDown={e => e.key === "Enter" && handleSendOtp()}
                />
              </div>
              <button className="btn-primary" onClick={handleSendOtp}>
                {t("login.btn", language)}
              </button>
            </motion.div>
          ) : (
            <motion.div key="otp" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <input
                type="text"
                maxLength={4}
                value={otp}
                onChange={e => setOtp(e.target.value.replace(/\D/g, ""))}
                placeholder="0000"
                className="input-field"
                style={{ textAlign: "center", fontSize: "24px", letterSpacing: "10px", marginBottom: "16px" }}
                onKeyDown={e => e.key === "Enter" && handleVerify()}
              />
              <button className="btn-primary" onClick={handleVerify}>
                Verify &amp; Enter App <ArrowRight size={14} style={{ display: "inline", marginLeft: "4px" }} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={handleGuest}
          style={{
            width: "100%",
            marginTop: "16px",
            background: "transparent",
            border: "none",
            color: "var(--color-warm-stone)",
            fontSize: "14px",
            cursor: "pointer",
            padding: "8px",
          }}
        >
          {t("login.guest", language)}
        </button>
      </motion.div>
    </motion.div>
  );
}
