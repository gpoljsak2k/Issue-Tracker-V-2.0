import api from "../api/client";

export async function createUser(userData) {
  const response = await api.post("/users/", userData);
  return response.data;
}