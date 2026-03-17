import api from "../api/client";

export async function fetchIssues(projectId, params = {}) {
  const response = await api.get(`/projects/${projectId}/issues`, {
    params,
  });
  return response.data;
}

export async function createIssue(projectId, issueData) {
  const response = await api.post(`/projects/${projectId}/issues`, issueData);
  return response.data;
}

export async function updateIssue(projectId, issueId, issueData) {
  const response = await api.patch(
    `/projects/${projectId}/issues/${issueId}`,
    issueData
  );
  return response.data;
}

export async function deleteIssue(projectId, issueId) {
  await api.delete(`/projects/${projectId}/issues/${issueId}`);
}