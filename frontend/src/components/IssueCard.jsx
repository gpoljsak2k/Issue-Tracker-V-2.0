function IssueCard({ issue, onSelect, getStatusColor, getStatusLabel, getPriorityColor }) {
  return (
    <div
      onClick={() => onSelect(issue)}
      style={{
        background: "white",
        padding: "16px",
        borderRadius: "10px",
        border: "1px solid #e2e8f0",
        cursor: "pointer",
      }}
    >
      <div style={{ fontWeight: "500", marginBottom: "10px" }}>
        {issue.title}
      </div>

      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <span
          style={{
            background: getStatusColor(issue.status),
            padding: "4px 10px",
            borderRadius: "999px",
            fontSize: "12px",
          }}
        >
          {getStatusLabel(issue.status)}
        </span>

        <span
          style={{
            background: getPriorityColor(issue.priority),
            padding: "4px 10px",
            borderRadius: "999px",
            fontSize: "12px",
            textTransform: "capitalize",
          }}
        >
          {issue.priority}
        </span>
      </div>
    </div>
  );
}

export default IssueCard;