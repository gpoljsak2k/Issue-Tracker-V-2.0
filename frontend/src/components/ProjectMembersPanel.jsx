import { useState } from "react";

function ProjectMembersPanel({
  selectedProject,
  members = [],
  membersLoading = false,
  canManageMembers = false,
  currentUser = null,
  onAddMember,
  onUpdateRole,
  onRemoveMember,
}) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("member");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    if (!username.trim()) {
      setError("Username is required.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      await onAddMember({
        username: username.trim(),
        role,
      });

      setUsername("");
      setRole("member");
      setShowAddForm(false);
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.detail || "Could not add project member.";

      setError(message);
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
        <h3 style={{ margin: 0, fontSize: "15px" }}>Project Members</h3>

        {selectedProject && canManageMembers && (
          <button
            onClick={() => setShowAddForm((prev) => !prev)}
            style={{
              padding: "6px 10px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              background: "white",
              cursor: "pointer",
              fontSize: "13px",
            }}
          >
            {showAddForm ? "Close" : "Add Member"}
          </button>
        )}
      </div>

      {showAddForm && canManageMembers && (
        <form
          onSubmit={handleSubmit}
          style={{
            marginBottom: "16px",
            padding: "12px",
            border: "1px solid #e2e8f0",
            borderRadius: "10px",
            background: "#f8fafc",
          }}
        >
          <div style={{ marginBottom: "10px" }}>
            <label style={{ display: "block", marginBottom: "6px", fontSize: "13px" }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={submitting}
              placeholder="Enter username"
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
            <label style={{ display: "block", marginBottom: "6px", fontSize: "13px" }}>
              Role
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              disabled={submitting}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "14px",
                background: "white",
              }}
            >
              <option value="admin">Admin</option>
              <option value="member">Member</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
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
              {submitting ? "Adding..." : "Add"}
            </button>

            <button
              type="button"
              onClick={() => setShowAddForm(false)}
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

      {membersLoading ? (
        <p style={{ color: "#475569", fontSize: "14px" }}>Loading members...</p>
      ) : members.length === 0 ? (
        <p style={{ color: "#475569", fontSize: "14px" }}>No members found.</p>
      ) : (
        <div style={{ display: "grid", gap: "10px" }}>
          {members.map((member) => {
            const isOwner = member.role === "owner";
            const isCurrentUser = currentUser?.id === member.userId;

            return (
              <div
                key={member.userId}
                style={{
                  padding: "12px",
                  border: "1px solid #e2e8f0",
                  borderRadius: "10px",
                  background: "#f8fafc",
                }}
              >
                <div
                  style={{
                    fontWeight: "600",
                    marginBottom: "6px",
                    color: "#0f172a",
                  }}
                >
                  {member.displayName}
                  {isCurrentUser ? " (you)" : ""}
                </div>

                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  {canManageMembers && !isOwner ? (
                    <>
                      <select
                        value={member.role}
                        onChange={(e) => onUpdateRole(member.userId, e.target.value)}
                        style={{
                          flex: 1,
                          padding: "8px 10px",
                          borderRadius: "8px",
                          border: "1px solid #cbd5e1",
                          fontSize: "13px",
                          background: "white",
                        }}
                      >
                        <option value="admin">Admin</option>
                        <option value="member">Member</option>
                        <option value="viewer">Viewer</option>
                      </select>

                      <button
                        onClick={() => onRemoveMember(member.userId)}
                        style={{
                          padding: "8px 10px",
                          borderRadius: "8px",
                          border: "1px solid #fecaca",
                          background: "#fef2f2",
                          color: "#b91c1c",
                          cursor: "pointer",
                          fontSize: "13px",
                        }}
                      >
                        Remove
                      </button>
                    </>
                  ) : (
                    <span
                      style={{
                        fontSize: "13px",
                        color: "#475569",
                        background: "#e2e8f0",
                        padding: "6px 10px",
                        borderRadius: "999px",
                      }}
                    >
                      {member.role}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default ProjectMembersPanel;