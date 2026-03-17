import api from "../api/client";

export async function fetchProjectLabels(projectId) {
  const res = await api.get(`/projects/${projectId}/labels`);
  return res.data;
}

export async function createLabel(projectId, data) {
  const res = await api.post(`/projects/${projectId}/labels`, data);
  return res.data;
}

export async function updateLabel(projectId, labelId, data) {
  const res = await api.patch(`/projects/${projectId}/labels/${labelId}`, data);
  return res.data;
}

export async function deleteLabel(projectId, labelId) {
  await api.delete(`/projects/${projectId}/labels/${labelId}`);
}

export async function fetchIssueLabels(projectId, issueId) {
  const res = await api.get(`/projects/${projectId}/issues/${issueId}/labels`);
  return res.data;
}

export async function attachLabel(projectId, issueId, labelId) {
  const res = await api.post(
    `/projects/${projectId}/issues/${issueId}/labels`,
    { label_id: labelId }
  );
  return res.data;
}

export async function removeLabel(projectId, issueId, labelId) {
  await api.delete(
    `/projects/${projectId}/issues/${issueId}/labels/${labelId}`
  );
}