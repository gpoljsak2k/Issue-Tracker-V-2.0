import api from "../api/client";

export async function fetchComments(projectId, issueId) {
  const response = await api.get(
    `/projects/${projectId}/issues/${issueId}/comments`
  );
  return response.data;
}

export async function createComment(projectId, issueId, body) {
  const response = await api.post(
    `/projects/${projectId}/issues/${issueId}/comments`,
    { body }
  );
  return response.data;
}

export async function updateComment(projectId, issueId, commentId, body) {
  const response = await api.patch(
    `/projects/${projectId}/issues/${issueId}/comments/${commentId}`,
    { body }
  );
  return response.data;
}

export async function deleteComment(projectId, issueId, commentId) {
  await api.delete(
    `/projects/${projectId}/issues/${issueId}/comments/${commentId}`,
  );
}