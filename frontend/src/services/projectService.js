import api from "../api/client";

export async function fetchProjects() {
  const response = await api.get("/projects/");
  return response.data;
}

export async function createProject(projectData) {
  const response = await api.post("/projects/", projectData);
  return response.data;
}

export async function deleteProject(projectId) {
  await api.delete(`/projects/${projectId}`);
}
