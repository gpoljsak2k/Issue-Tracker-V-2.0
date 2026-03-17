import api from "../api/client";

export async function fetchProjectActivity(projectId) {
  const response = await api.get(`/projects/${projectId}/activity`);
  return response.data;
}