function IssuesToolbar({
  showCreateForm,
  selectedProjectId,
  issuesLoading,
  onToggleCreateForm,
  onRefresh,
  search,
  statusFilter,
  priorityFilter,
  assignedToMeOnly = false,
  onSearchChange,
  onStatusFilterChange,
  onPriorityFilterChange,
  onAssignedToMeChange,
}) {
  return (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "16px",
          gap: "12px",
        }}
      >
        <h2 style={{ fontSize: "18px", margin: 0 }}>Issues</h2>

        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={onToggleCreateForm}
            disabled={!selectedProjectId}
            style={{
              padding: "8px 12px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              background: "white",
              cursor: "pointer",
            }}
          >
            {showCreateForm ? "Cancel" : "New Issue"}
          </button>

          <button
            onClick={onRefresh}
            disabled={!selectedProjectId || issuesLoading}
            style={{
              padding: "8px 12px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              background: "white",
              cursor: "pointer",
            }}
          >
            {issuesLoading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: "12px", marginBottom: "16px" }}>
        <input
          type="text"
          placeholder="Search issues..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            fontSize: "14px",
          }}
        />

        <select
          value={statusFilter}
          onChange={(e) => onStatusFilterChange(e.target.value)}
          style={{
            padding: "10px 12px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            fontSize: "14px",
            background: "white",
          }}
        >
          <option value="all">All statuses</option>
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="in_review">In review</option>
          <option value="blocked">Blocked</option>
          <option value="done">Done</option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => onPriorityFilterChange(e.target.value)}
          style={{
            padding: "10px 12px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            fontSize: "14px",
            background: "white",
          }}
        >
          <option value="all">All priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      <div style={{ marginBottom: "16px" }}>
        <label
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px",
            color: "#334155",
            cursor: "pointer",
          }}
        >
          <input
            type="checkbox"
            checked={assignedToMeOnly}
            onChange={(e) => onAssignedToMeChange?.(e.target.checked)}
          />
          Assigned to me
        </label>
      </div>
    </>
  );
}

export default IssuesToolbar;