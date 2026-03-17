import { useState } from "react";

function ProjectLabelsPanel({
  selectedProject,
  projectLabels = [],
  onCreateLabel,
  onDeleteLabel,
}) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [color, setColor] = useState("#e2e8f0");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    if (!name.trim()) {
      setError("Label name is required.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      await onCreateLabel({
        name: name.trim(),
        color,
      });

      setName("");
      setColor("#e2e8f0");
      setShowForm(false);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Could not create label.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      style={{
        marginTop: "16px",
        paddingTop: "16px",
        borderTop: "1px solid #e2e8f0",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "12px",
          gap: "8px",
        }}
      >
        <h3 style={{ margin: 0, fontSize: "15px" }}>Project Labels</h3>

        {selectedProject && (
          <button
            onClick={() => setShowForm((prev) => !prev)}
            style={{
              padding: "6px 10px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              background: "white",
              cursor: "pointer",
              fontSize: "13px",
            }}
          >
            {showForm ? "Close" : "New Label"}
          </button>
        )}
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          style={{
            width: "100%",
            boxSizing: "border-box",
            marginBottom: "16px",
            padding: "12px",
            border: "1px solid #e2e8f0",
            borderRadius: "10px",
            background: "#f8fafc",
          }}
        >
          <div style={{ marginBottom: "10px" }}>
            <label
              style={{
                display: "block",
                marginBottom: "6px",
                fontSize: "13px",
              }}
            >
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={submitting}
              placeholder="Enter label name"
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "10px 12px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "14px",
              }}
            />
          </div>

          <div style={{ marginBottom: "10px" }}>
            <label
              style={{
                display: "block",
                marginBottom: "6px",
                fontSize: "13px",
              }}
            >
              Color
            </label>
            <input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              disabled={submitting}
              style={{
                width: "100%",
                height: "40px",
                boxSizing: "border-box",
                padding: "4px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                background: "white",
              }}
            />
          </div>

          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: "8px 12px",
                borderRadius: "8px",
                border: "none",
                background: "#0f172a",
                color: "white",
                cursor: "pointer",
              }}
            >
              {submitting ? "Creating..." : "Create Label"}
            </button>

            <button
              type="button"
              onClick={() => setShowForm(false)}
              disabled={submitting}
              style={{
                padding: "8px 12px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                background: "white",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
          </div>

          {error && (
            <p style={{ color: "crimson", marginTop: "10px", marginBottom: 0 }}>
              {error}
            </p>
          )}
        </form>
      )}

      {projectLabels.length === 0 ? (
        <p style={{ color: "#475569", fontSize: "14px" }}>No labels yet.</p>
      ) : (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
          {projectLabels.map((label) => (
            <span
              key={label.id}
              onClick={() => onDeleteLabel(label.id)}
              title="Click to delete"
              style={{
                padding: "6px 10px",
                borderRadius: "999px",
                background: label.color || "#e2e8f0",
                fontSize: "12px",
                cursor: "pointer",
              }}
            >
              {label.name} ✕
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProjectLabelsPanel;