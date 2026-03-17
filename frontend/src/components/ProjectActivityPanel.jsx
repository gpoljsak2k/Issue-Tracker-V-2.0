function formatDate(value) {
  if (!value) return "";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function startCase(value) {
  if (!value) return "";
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function truncate(text, max = 50) {
  if (!text) return "";
  return text.length > max ? text.slice(0, max) + "..." : text;
}

function formatAction(action) {
  const labels = {
    issue_created: "Issue created",
    issue_updated: "Issue updated",
    issue_deleted: "Issue deleted",
    comment_added: "Comment added",
    comment_updated: "Comment updated",
    comment_deleted: "Comment deleted",
    member_added: "Member added",
    member_removed: "Member removed",
    member_role_updated: "Member role updated",
    label_created: "Label created",
    label_updated: "Label updated",
    label_deleted: "Label deleted",
  };

  return labels[action] || startCase(action) || "Activity";
}

function renderMetadataLine(item) {
  const metadata = item.metadata_json || {};

  if (item.action === "issue_created") {
    return metadata.title
      ? `Created issue "${metadata.title}".`
      : "A new issue was created.";
  }

  if (item.action === "issue_updated") {
    const parts = [];

    if (metadata.old_status || metadata.new_status) {
      parts.push(
        `Status: ${metadata.old_status || "—"} → ${metadata.new_status || "—"}`
      );
    }

    if (metadata.old_priority || metadata.new_priority) {
      parts.push(
        `Priority: ${metadata.old_priority || "—"} → ${metadata.new_priority || "—"}`
      );
    }

    if (metadata.old_title || metadata.new_title) {
      parts.push(
        `Title: ${metadata.old_title || "—"} → ${metadata.new_title || "—"}`
      );
    }

    if (parts.length > 0) {
      return parts.join(" • ");
    }

    return "Issue details were updated.";
  }

  if (item.action === "issue_deleted") {
    return metadata.title
      ? `Deleted issue "${metadata.title}".`
      : "An issue was deleted.";
  }

  if (item.action === "comment_added") {
    if (metadata.body) {
      return `Added comment: "${truncate(metadata.body)}"`;
    }
    return "A comment was added.";
  }

  if (item.action === "comment_updated") {
    return "A comment was updated.";
  }

    if (item.action === "comment_deleted") {
      const bodyPreview = metadata.body
        ? truncate(String(metadata.body).replace(/\s+/g, " ").trim())
        : "";

      if (metadata.author_username && bodyPreview) {
        return `Deleted comment by ${metadata.author_username}: "${bodyPreview}"`;
      }

      if (metadata.author_username) {
        return `Deleted comment by ${metadata.author_username}.`;
      }

      if (metadata.comment_id) {
        return `Deleted comment #${metadata.comment_id}.`;
      }

      return "A comment was deleted.";
    }

  if (item.action === "member_added") {
    const username = metadata.added_username;
    const role = metadata.role;

    if (username && role) {
      return `Added ${username} as ${role}.`;
    }

    if (username) {
      return `Added ${username} to the project.`;
    }

    return "A project member was added.";
  }

  if (item.action === "member_removed") {
    if (metadata.target_username) {
      return `Removed ${metadata.target_username} from the project.`;
    }

    if (metadata.removed_user_id) {
      return `Removed user #${metadata.removed_user_id} from the project.`;
    }

    return "A project member was removed.";
  }

  if (item.action === "member_role_updated") {
    return `Changed role of ${
      metadata.target_username || `user #${metadata.target_user_id}`
    } from ${metadata.old_role} to ${metadata.new_role}.`;
  }

  if (item.action === "label_created") {
    return metadata.name
      ? `Created label "${metadata.name}".`
      : "A label was created.";
  }

  if (item.action === "label_updated") {
    return metadata.name
      ? `Updated label "${metadata.name}".`
      : "A label was updated.";
  }

  if (item.action === "label_deleted") {
    return metadata.name
      ? `Deleted label "${metadata.name}".`
      : "A label was deleted.";
  }

  const entries = Object.entries(metadata);
  if (entries.length === 0) {
    return "Project activity recorded.";
  }

  return entries
    .map(([key, value]) => `${startCase(key)}: ${String(value)}`)
    .join(" • ");
}

function ProjectActivityPanel({ activity = [], loading = false }) {
  const shouldScroll = activity.length > 5;

  return (
    <div
      style={{
        marginTop: "24px",
        background: "white",
        boxSizing: "border-box",
        border: "1px solid #e2e8f0",
        borderRadius: "12px",
        padding: "16px",
      }}
    >
      <h3 style={{ marginTop: 0, marginBottom: "12px" }}>Recent Activity</h3>

      {loading ? (
        <p style={{ color: "#475569", margin: 0 }}>Loading activity...</p>
      ) : activity.length === 0 ? (
        <p style={{ color: "#475569", margin: 0 }}>No activity yet.</p>
      ) : (
        <div
          style={{
            display: "grid",
            gap: "12px",
            maxHeight: shouldScroll ? "320px" : "none",
            overflowY: shouldScroll ? "auto" : "visible",
            paddingRight: shouldScroll ? "4px" : 0,
          }}
        >
          {activity.map((item) => (
            <div
              key={item.id}
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
                  color: "#0f172a",
                  marginBottom: "4px",
                  fontSize: "14px",
                }}
              >
                {formatAction(item.action)}
              </div>

              <div
                style={{
                  fontSize: "13px",
                  color: "#334155",
                  marginBottom: "6px",
                }}
              >
                {renderMetadataLine(item)}
              </div>

              <div
                style={{
                  fontSize: "12px",
                  color: "#64748b",
                  display: "flex",
                  justifyContent: "space-between",
                  gap: "8px",
                  flexWrap: "wrap",
                }}
              >
                <span>
                  By user: {item.actor?.username || `user #${item.actor_id}`}
                </span>
                <span>{formatDate(item.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProjectActivityPanel;