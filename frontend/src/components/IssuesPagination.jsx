function IssuesPagination({
  total = 0,
  limit = 5,
  offset = 0,
  onPrevious,
  onNext,
}) {
  if (total === 0) return null;

  const start = offset + 1;
  const end = Math.min(offset + limit, total);
  const hasPrevious = offset > 0;
  const hasNext = offset + limit < total;

  return (
    <div
      style={{
        marginTop: "16px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: "12px",
        flexWrap: "wrap",
      }}
    >
      <div style={{ fontSize: "14px", color: "#475569" }}>
        Showing {start}-{end} of {total} issues
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        <button
          onClick={onPrevious}
          disabled={!hasPrevious}
          style={{
            padding: "8px 12px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            background: hasPrevious ? "white" : "#f8fafc",
            cursor: hasPrevious ? "pointer" : "not-allowed",
          }}
        >
          Previous
        </button>

        <button
          onClick={onNext}
          disabled={!hasNext}
          style={{
            padding: "8px 12px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            background: hasNext ? "white" : "#f8fafc",
            cursor: hasNext ? "pointer" : "not-allowed",
          }}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default IssuesPagination;