import api from "../api/client";

export async function fetchProjectMembers(projectId) {
  const response = await api.get(`/projects/${projectId}/members`);
  return response.data;
}

export async function addProjectMember(projectId, memberData) {
  const response = await api.post(`/projects/${projectId}/members`, memberData);
  return response.data;
}

export async function updateProjectMemberRole(projectId, userId, role) {
  const response = await api.patch(`/projects/${projectId}/members/${userId}`, {
    role,
  });
  return response.data;
}

export async function removeProjectMember(projectId, userId) {
  await api.delete(`/projects/${projectId}/members/${userId}`);
}