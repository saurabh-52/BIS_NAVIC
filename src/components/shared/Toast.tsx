"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, CheckCircle, AlertTriangle, Info } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { useEffect } from "react";

const TOAST_STYLES = {
  success: { bg: "var(--color-valid-green-bg)",  border: "var(--color-valid-green)", icon: CheckCircle,      iconColor: "var(--color-valid-green)" },
  error:   { bg: "var(--color-error-red-bg)",    border: "var(--color-error-red)",   icon: AlertTriangle,     iconColor: "var(--color-error-red)" },
  info:    { bg: "rgba(250,93,0,0.06)",           border: "rgba(250,93,0,0.3)",       icon: Info,              iconColor: "var(--color-harvest-flame)" },
};

function ToastItem({ toast }: { toast: { id: string; message: string; type: "success" | "error" | "info" } }) {
  const { removeToast } = useAppStore();
  const style = TOAST_STYLES[toast.type];
  const Icon = style.icon;

  useEffect(() => {
    const t = setTimeout(() => removeToast(toast.id), 3500);
    return () => clearTimeout(t);
  }, [toast.id, removeToast]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 80, scale: 0.96 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 80, scale: 0.96 }}
      transition={{ type: "spring", damping: 22 }}
      style={{
        display: "flex",
        alignItems: "center",
        gap: "10px",
        padding: "12px 16px",
        background: style.bg,
        border: `1px solid ${style.border}`,
        borderRadius: "var(--radius-md)",
        boxShadow: "var(--shadow-sm)",
        maxWidth: "360px",
        fontSize: "13px",
        color: "var(--color-ink-black)",
        fontWeight: 500,
      }}
    >
      <Icon size={15} color={style.iconColor} style={{ flexShrink: 0 }} />
      <span style={{ flex: 1 }}>{toast.message}</span>
      <button
        onClick={() => removeToast(toast.id)}
        style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--color-driftwood)", padding: "2px" }}
      >
        <X size={13} />
      </button>
    </motion.div>
  );
}

export function ToastContainer() {
  const { toasts } = useAppStore();
  return (
    <div style={{
      position: "fixed",
      bottom: "24px",
      right: "24px",
      zIndex: 999,
      display: "flex",
      flexDirection: "column",
      gap: "8px",
    }}>
      <AnimatePresence mode="popLayout">
        {toasts.map(toast => (
          <ToastItem key={toast.id} toast={toast} />
        ))}
      </AnimatePresence>
    </div>
  );
}
