import { useState } from "react";

function formatDate(value) {
  if (!value) return "";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function CommentsPanel({
  comments,
  loading,
  submitting,
  actionLoading,
  onSubmit,
  onUpdate,
  onDelete,
}) {
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editBody, setEditBody] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    if (!content.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    try {
      setError("");
      await onSubmit(content.trim());
      setContent("");
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Could not add comment.");
      }
    }
  }

  function startEditing(comment) {
    setEditingCommentId(comment.id);
    setEditBody(comment.body || "");
  }

  function cancelEditing() {
    setEditingCommentId(null);
    setEditBody("");
  }

  async function saveEdit(commentId) {
    if (!editBody.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    try {
      setError("");
      await onUpdate(commentId, editBody.trim());
      setEditingCommentId(null);
      setEditBody("");
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Could not update comment.");
      }
    }
  }

  return (
    <div style={{ marginTop: "20px" }}>
      <h3 style={{ fontSize: "15px", marginBottom: "12px" }}>Comments</h3>

      <form onSubmit={handleSubmit} style={{ marginBottom: "16px" }}>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={3}
          placeholder="Write a comment..."
          disabled={submitting || actionLoading}
          style={{
            width: "100%",
            padding: "10px 12px",
            boxSizing: "border-box",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            fontSize: "14px",
            resize: "vertical",
            marginBottom: "8px",
          }}
        />

        <button
          type="submit"
          disabled={submitting || actionLoading}
          style={{
            padding: "8px 12px",
            borderRadius: "8px",
            border: "none",
            background: "#0f172a",
            color: "white",
            cursor: "pointer",
          }}
        >
          {submitting ? "Posting..." : "Add Comment"}
        </button>

        {error && (
          <p style={{ color: "crimson", marginTop: "10px", marginBottom: 0 }}>
            {error}
          </p>
        )}
      </form>

      {loading ? (
        <p style={{ color: "#475569" }}>Loading comments...</p>
      ) : comments.length === 0 ? (
        <p style={{ color: "#475569" }}>No comments yet.</p>
      ) : (
        <div style={{ display: "grid", gap: "12px" }}>
          {comments.map((comment) => {
            const isEditing = editingCommentId === comment.id;

            return (
              <div
                key={comment.id}
                style={{
                  border: "1px solid #e2e8f0",
                  borderRadius: "10px",
                  padding: "12px",
                  background: "#f8fafc",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "12px",
                    marginBottom: "8px",
                    fontSize: "12px",
                    color: "#64748b",
                  }}
                >
                  <span>
                      {comment.author?.username || `User ${comment.author_id}`}
                  </span>
                  <span>{formatDate(comment.created_at)}</span>
                </div>

                {isEditing ? (
                  <>
                    <textarea
                      value={editBody}
                      onChange={(e) => setEditBody(e.target.value)}
                      rows={3}
                      disabled={actionLoading}
                      style={{
                        width: "100%",
                        padding: "10px 12px",
                        borderRadius: "8px",
                        border: "1px solid #cbd5e1",
                        fontSize: "14px",
                        resize: "vertical",
                        marginBottom: "8px",
                      }}
                    />

                    <div style={{ display: "flex", gap: "8px" }}>
                      <button
                        type="button"
                        onClick={() => saveEdit(comment.id)}
                        disabled={actionLoading}
                        style={{
                          padding: "6px 10px",
                          borderRadius: "8px",
                          border: "none",
                          background: "#0f172a",
                          color: "white",
                          cursor: "pointer",
                          fontSize: "13px",
                        }}
                      >
                        Save
                      </button>

                      <button
                        type="button"
                        onClick={cancelEditing}
                        disabled={actionLoading}
                        style={{
                          padding: "6px 10px",
                          borderRadius: "8px",
                          border: "1px solid #cbd5e1",
                          background: "white",
                          cursor: "pointer",
                          fontSize: "13px",
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <p
                      style={{
                        margin: 0,
                        marginBottom: "10px",
                        color: "#334155",
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {comment.body}
                    </p>

                    <div style={{ display: "flex", gap: "8px" }}>
                      <button
                        type="button"
                        onClick={() => startEditing(comment)}
                        disabled={actionLoading}
                        style={{
                          padding: "6px 10px",
                          borderRadius: "8px",
                          border: "1px solid #cbd5e1",
                          background: "white",
                          cursor: "pointer",
                          fontSize: "13px",
                        }}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        onClick={() => onDelete(comment.id)}
                        disabled={actionLoading}
                        style={{
                          padding: "6px 10px",
                          borderRadius: "8px",
                          border: "1px solid #fecaca",
                          background: "#fef2f2",
                          color: "#b91c1c",
                          cursor: "pointer",
                          fontSize: "13px",
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default CommentsPanel;