function Toast({ toast, onClose }) {
  if (!toast) return null;

  const isError = toast.type === "error";

  return (
    <div
      style={{
        position: "fixed",
        top: "20px",
        right: "20px",
        zIndex: 1000,
        minWidth: "260px",
        maxWidth: "360px",
        padding: "14px 16px",
        borderRadius: "12px",
        border: isError ? "1px solid #fecaca" : "1px solid #bbf7d0",
        background: isError ? "#fef2f2" : "#f0fdf4",
        color: isError ? "#991b1b" : "#166534",
        boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: "12px",
          alignItems: "start",
        }}
      >
        <div>
          <div style={{ fontWeight: "600", marginBottom: "4px" }}>
            {isError ? "Error" : "Success"}
          </div>
          <div style={{ fontSize: "14px" }}>{toast.message}</div>
        </div>

        <button
          onClick={onClose}
          style={{
            border: "none",
            background: "transparent",
            cursor: "pointer",
            fontSize: "16px",
            lineHeight: 1,
            color: "inherit",
          }}
        >
          ×
        </button>
      </div>
    </div>
  );
}

export default Toast;