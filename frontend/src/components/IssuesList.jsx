import IssueCard from "./IssueCard";

function IssuesList({
  issuesLoading,
  error,
  filteredIssues = [],
  onSelectIssue,
  getStatusColor,
  getStatusLabel,
  getPriorityColor,
}) {
  if (issuesLoading) {
    return <p>Loading issues...</p>;
  }

  if (error) {
    return <p style={{ color: "crimson" }}>{error}</p>;
  }

  if (filteredIssues.length === 0) {
    return (
      <p style={{ color: "#475569" }}>
        No issues found for this project.
      </p>
    );
  }

  const shouldScroll = filteredIssues.length > 5;

  return (
    <div
      style={{
        display: "grid",
        gap: "12px",
        maxHeight: shouldScroll ? "520px" : "none",
        overflowY: shouldScroll ? "auto" : "visible",
        paddingRight: shouldScroll ? "4px" : 0,
      }}
    >
      {filteredIssues.map((issue) => (
        <IssueCard
          key={issue.id}
          issue={issue}
          onSelect={onSelectIssue}
          getStatusColor={getStatusColor}
          getStatusLabel={getStatusLabel}
          getPriorityColor={getPriorityColor}
        />
      ))}
    </div>
  );
}

export default IssuesList;