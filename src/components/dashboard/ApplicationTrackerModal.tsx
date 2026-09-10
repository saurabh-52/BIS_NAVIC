import { motion, AnimatePresence } from "framer-motion";
import { X, Check } from "lucide-react";

interface TrackerModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
}

const steps = [
  { label: "Application Submitted", date: "10 Feb 2026", status: "completed" },
  { label: "Document Verification", date: "In Progress", status: "progress" },
  { label: "Sample Testing", date: "Pending", status: "pending" },
  { label: "Certification Approval", date: "Pending", status: "pending" },
  { label: "R-Number Issued", date: "Pending", status: "pending" }
];

export default function ApplicationTrackerModal({ isOpen, onClose, title }: TrackerModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(29,30,28,0.5)",
            backdropFilter: "blur(4px)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "16px",
          }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 20 }}
            transition={{ type: "spring", damping: 24 }}
            onClick={e => e.stopPropagation()}
            style={{
              background: "#F4F8FD", // Light blue background from screenshot
              borderRadius: "var(--radius-lg)",
              boxShadow: "var(--shadow-lg)",
              border: "1px solid #D6E4F0",
              width: "100%",
              maxWidth: "380px",
              display: "flex",
              flexDirection: "column",
              padding: "24px",
              position: "relative"
            }}
          >
            <button
              onClick={onClose}
              style={{
                position: "absolute",
                top: "16px",
                right: "16px",
                background: "transparent",
                border: "none",
                cursor: "pointer",
                color: "var(--color-driftwood)"
              }}
            >
              <X size={18} />
            </button>

            <h3 style={{ fontSize: "14px", fontWeight: 700, color: "#1E2A44", marginBottom: "24px" }}>
              My Application — CRS Registration
            </h3>

            <div style={{ position: "relative", paddingLeft: "12px", marginBottom: "32px" }}>
              {/* Vertical connecting line */}
              <div style={{
                position: "absolute",
                left: "26px", // 12px (padding) + 14px (half of 28px circle)
                top: "14px",
                bottom: "14px",
                width: "2px",
                background: "#D6E4F0",
                zIndex: 0
              }} />

              {steps.map((step, idx) => (
                <div key={idx} style={{ display: "flex", alignItems: "flex-start", gap: "16px", marginBottom: idx === steps.length - 1 ? 0 : "24px", position: "relative", zIndex: 1 }}>
                  <div style={{
                    width: "30px",
                    height: "30px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "12px",
                    fontWeight: 700,
                    color: step.status === "completed" || step.status === "progress" ? "#fff" : "#8BA3C0",
                    background: step.status === "completed" ? "#7E5BB8" : step.status === "progress" ? "#7E5BB8" : "#E2EAF4",
                    flexShrink: 0
                  }}>
                    {idx + 1}
                  </div>
                  <div style={{ paddingTop: "4px" }}>
                    <p style={{ fontSize: "13px", fontWeight: 700, color: "#1E2A44", marginBottom: "4px" }}>
                      {step.label}
                    </p>
                    <p style={{ fontSize: "11px", color: step.status === "progress" ? "#617A9B" : "#8BA3C0", fontWeight: step.status === "progress" ? 600 : 400 }}>
                      {step.date}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <button style={{
              background: "#7E5BB8",
              color: "#fff",
              border: "none",
              borderRadius: "24px",
              padding: "12px",
              fontSize: "14px",
              fontWeight: 700,
              cursor: "pointer",
              width: "100%",
              transition: "opacity 0.2s"
            }}
            onMouseOver={e => e.currentTarget.style.opacity = "0.9"}
            onMouseOut={e => e.currentTarget.style.opacity = "1"}
            >
              View Details
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
