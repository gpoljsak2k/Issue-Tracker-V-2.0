export function getStatusLabel(status) {
  if (status === "todo") return "To do";
  if (status === "in_progress") return "In progress";
  if (status === "in_review") return "In review";
  if (status === "blocked") return "Blocked";
  if (status === "done") return "Done";
  return status;
}

export function getStatusColor(status) {
  if (status === "done") return "#dcfce7";
  if (status === "in_progress") return "#dbeafe";
  if (status === "blocked") return "#fee2e2";
  if (status === "in_review") return "#fef3c7";
  return "#e2e8f0";
}

export function getPriorityColor(priority) {
  if (priority === "urgent") return "#fee2e2";
  if (priority === "high") return "#ffedd5";
  if (priority === "medium") return "#fef3c7";
  return "#e2e8f0";
}

export function normalizeProjectMember(member) {
  return {
    userId: member.user_id ?? member.user?.id ?? member.id,
    role: member.role ?? "",
    displayName:
      member.user?.username ||
      member.username ||
      member.user?.email ||
      member.email ||
      `User ${member.user_id ?? member.user?.id ?? member.id}`,
  };
}