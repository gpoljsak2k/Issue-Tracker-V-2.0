import { useState } from "react";

function CreateIssueForm({ onCreate, disabled = false }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [status, setStatus] = useState("todo");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    if (!title.trim()) {
      setError("Title is required.");
      setSuccess("");
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      await onCreate({
        title: title.trim(),
        description: description.trim(),
        priority,
        status,
      });

      setTitle("");
      setDescription("");
      setPriority("medium");
      setStatus("todo");
      setSuccess("Issue created successfully.");
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Could not create issue.");
      }

      setSuccess("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      style={{
        background: "white",
        border: "1px solid #e2e8f0",
        borderRadius: "12px",
        padding: "16px",
        marginBottom: "20px",
      }}
    >
      <h3 style={{ marginTop: 0, marginBottom: "12px" }}>Create Issue</h3>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", marginBottom: "6px" }}>Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={disabled || submitting}
            placeholder="Enter issue title..."
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
          <label style={{ display: "block", marginBottom: "6px" }}>
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={disabled || submitting}
            placeholder="Describe the issue..."
            rows={4}
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

        <div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "6px" }}>
              Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              disabled={disabled || submitting}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "14px",
                background: "white",
              }}
            >
              <option value="todo">To do</option>
              <option value="in_progress">In progress</option>
              <option value="in_review">In review</option>
              <option value="blocked">Blocked</option>
              <option value="done">Done</option>
            </select>
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "6px" }}>
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={disabled || submitting}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "14px",
                background: "white",
              }}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={disabled || submitting}
          style={{
            padding: "10px 14px",
            borderRadius: "8px",
            border: "none",
            background: "#0f172a",
            color: "white",
            cursor: "pointer",
          }}
        >
          {submitting ? "Creating..." : "Create Issue"}
        </button>
      </form>

      {error && (
        <p style={{ color: "crimson", marginTop: "12px", marginBottom: 0 }}>
          {error}
        </p>
      )}

      {success && (
        <p style={{ color: "green", marginTop: "12px", marginBottom: 0 }}>
          {success}
        </p>
      )}
    </div>
  );
}

export default CreateIssueForm;