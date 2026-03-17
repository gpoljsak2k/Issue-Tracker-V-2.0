import CommentsPanel from "./CommentsPanel";

function IssueDetailsPanel({
  activeIssue,
  isEditingIssue,
  editTitle,
  editDescription,
  setEditTitle,
  setEditDescription,
  startEditingIssue,
  cancelEditingIssue,
  saveIssueEdits,
  handleDeleteIssue,
  handleIssueFieldUpdate,
  handleAssigneeChange,
  issueUpdateLoading,
  issueDeleteLoading,
  members = [],
  membersLoading = false,
  comments = [],
  commentsLoading = false,
  commentSubmitting = false,
  commentActionLoading = false,
  handleCreateComment,
  handleUpdateComment,
  handleDeleteComment,
  issueLabels = [],
  projectLabels = [],
  labelsLoading = false,
  handleAddLabel,
  handleRemoveLabel,
}) {
  return (
    <aside
      style={{
        width: "320px",
        borderLeft: "1px solid #e2e8f0",
        background: "white",
        padding: "16px",
        overflowY: "auto",
        maxHeight: "calc(100vh - 57px)",
        boxSizing: "border-box",
      }}
    >
      <h2 style={{ fontSize: "16px", marginBottom: "12px" }}>
        Issue Details
      </h2>

      {activeIssue ? (
        <>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "8px",
              gap: "8px",
            }}
          >
            {!isEditingIssue ? (
              <h3 style={{ margin: 0 }}>{activeIssue.title}</h3>
            ) : (
              <input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                disabled={issueUpdateLoading || issueDeleteLoading}
                style={{
                  flex: 1,
                  padding: "10px 12px",
                  borderRadius: "8px",
                  border: "1px solid #cbd5e1",
                  fontSize: "16px",
                  fontWeight: "600",
                  boxSizing: "border-box",
                }}
              />
            )}

            {!isEditingIssue ? (
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={startEditingIssue}
                  disabled={issueDeleteLoading}
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
                  onClick={handleDeleteIssue}
                  disabled={issueDeleteLoading}
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
                  {issueDeleteLoading ? "Deleting..." : "Delete"}
                </button>
              </div>
            ) : (
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={saveIssueEdits}
                  disabled={issueUpdateLoading || issueDeleteLoading}
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
                  {issueUpdateLoading ? "Saving..." : "Save"}
                </button>

                <button
                  onClick={cancelEditingIssue}
                  disabled={issueUpdateLoading || issueDeleteLoading}
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
            )}
          </div>

          <div
            style={{
              display: "grid",
              gap: "12px",
              marginBottom: "16px",
            }}
          >
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "13px",
                  marginBottom: "6px",
                  color: "#475569",
                }}
              >
                Status
              </label>
              <select
                value={activeIssue.status}
                onChange={(e) => handleIssueFieldUpdate("status", e.target.value)}
                disabled={issueUpdateLoading || issueDeleteLoading}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
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

            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "13px",
                  marginBottom: "6px",
                  color: "#475569",
                }}
              >
                Priority
              </label>
              <select
                value={activeIssue.priority}
                onChange={(e) => handleIssueFieldUpdate("priority", e.target.value)}
                disabled={issueUpdateLoading || issueDeleteLoading}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
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

            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "13px",
                  marginBottom: "6px",
                  color: "#475569",
                }}
              >
                Assignee
              </label>
              <select
                value={activeIssue.assignee_id ?? ""}
                onChange={(e) => handleAssigneeChange(e.target.value)}
                disabled={issueUpdateLoading || issueDeleteLoading || membersLoading}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "10px 12px",
                  borderRadius: "8px",
                  border: "1px solid #cbd5e1",
                  fontSize: "14px",
                  background: "white",
                }}
              >
                <option value="">Unassigned</option>

                {members.map((member) => (
                  <option key={member.userId} value={member.userId}>
                    {member.displayName}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "13px",
                  marginBottom: "6px",
                  color: "#475569",
                }}
              >
                Labels
              </label>

              {labelsLoading ? (
                <p
                  style={{
                    color: "#475569",
                    fontSize: "13px",
                    margin: "0 0 8px 0",
                  }}
                >
                  Loading labels...
                </p>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "6px",
                    marginBottom: "8px",
                  }}
                >
                  {issueLabels.length === 0 ? (
                    <span style={{ fontSize: "13px", color: "#64748b" }}>
                      No labels assigned.
                    </span>
                  ) : (
                    issueLabels.map((label) => (
                      <span
                        key={label.id}
                        onClick={() => handleRemoveLabel?.(label.id)}
                        style={{
                          padding: "4px 8px",
                          borderRadius: "999px",
                          background: label.color || "#e2e8f0",
                          fontSize: "12px",
                          cursor: "pointer",
                        }}
                        title="Click to remove"
                      >
                        {label.name} ✕
                      </span>
                    ))
                  )}
                </div>
              )}

              <select
                defaultValue=""
                onChange={(e) => {
                  if (!e.target.value) return;
                  handleAddLabel?.(Number(e.target.value));
                  e.target.value = "";
                }}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "10px 12px",
                  borderRadius: "8px",
                  border: "1px solid #cbd5e1",
                  fontSize: "14px",
                  background: "white",
                }}
              >
                <option value="">Add label</option>
                {projectLabels.map((label) => (
                  <option key={label.id} value={label.id}>
                    {label.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {issueUpdateLoading && (
            <p style={{ color: "#475569", fontSize: "13px", marginTop: 0 }}>
              Saving changes...
            </p>
          )}

          {issueDeleteLoading && (
            <p style={{ color: "#b91c1c", fontSize: "13px", marginTop: 0 }}>
              Deleting issue...
            </p>
          )}

          {membersLoading && (
            <p style={{ color: "#475569", fontSize: "13px", marginTop: 0 }}>
              Loading project members...
            </p>
          )}

          {isEditingIssue ? (
            <div style={{ marginTop: "12px" }}>
              <label
                style={{
                  display: "block",
                  fontSize: "13px",
                  marginBottom: "6px",
                  color: "#475569",
                }}
              >
                Description
              </label>

              <textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                disabled={issueUpdateLoading || issueDeleteLoading}
                rows={5}
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
          ) : (
            <p style={{ color: "#475569" }}>
              {activeIssue.description || "No description provided."}
            </p>
          )}

          <CommentsPanel
            comments={comments}
            loading={commentsLoading}
            submitting={commentSubmitting}
            actionLoading={commentActionLoading}
            onSubmit={handleCreateComment}
            onUpdate={handleUpdateComment}
            onDelete={handleDeleteComment}
          />
        </>
      ) : (
        <p style={{ color: "#475569" }}>
          No issues match the current filters.
        </p>
      )}
    </aside>
  );
}

export default IssueDetailsPanel;