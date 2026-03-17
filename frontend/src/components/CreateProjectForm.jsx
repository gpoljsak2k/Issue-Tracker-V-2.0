import { useState } from "react";

function CreateProjectForm({ onCreate, disabled = false, onCancel }) {
  const [name, setName] = useState("");
  const [key, setKey] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    if (!name.trim()) {
      setError("Project name is required.");
      return;
    }

    if (!key.trim()) {
      setError("Project key is required.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      await onCreate({
        name: name.trim(),
        key: key.trim().toUpperCase(),
        description: description.trim() || null,
      });

      setName("");
      setKey("");
      setDescription("");
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Could not create project.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      style={{
        width: "100%",
        boxSizing: "border-box",
        background: "white",
        border: "1px solid #e2e8f0",
        borderRadius: "12px",
        padding: "16px",
        marginBottom: "16px",
      }}
    >
      <h3 style={{ marginTop: 0, marginBottom: "12px" }}>Create Project</h3>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "6px" }}>Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={disabled || submitting}
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

        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "6px" }}>Key</label>
          <input
            type="text"
            value={key}
            onChange={(e) => setKey(e.target.value.toUpperCase())}
            disabled={disabled || submitting}
            placeholder="E.G. DEMO"
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px 12px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
              textTransform: "uppercase",
            }}
          />
        </div>

        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "6px" }}>
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={disabled || submitting}
            rows={3}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px 12px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
              resize: "vertical",
            }}
          />
        </div>

        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          <button
            type="submit"
            disabled={disabled || submitting}
            style={{
              padding: "10px 12px",
              borderRadius: "8px",
              border: "none",
              background: "#0f172a",
              color: "white",
              cursor: "pointer",
            }}
          >
            {submitting ? "Creating..." : "Create Project"}
          </button>

          <button
            type="button"
            onClick={onCancel}
            disabled={submitting}
            style={{
              padding: "10px 12px",
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
          <p style={{ color: "crimson", marginTop: "12px", marginBottom: 0 }}>
            {error}
          </p>
        )}
      </form>
    </div>
  );
}

export default CreateProjectForm;