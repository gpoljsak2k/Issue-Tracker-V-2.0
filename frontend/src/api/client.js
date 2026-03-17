import axios from "axios";
import { getToken, removeToken } from "../services/auth";

const baseURL = import.meta.env.VITE_API_BASE_URL;

if (!baseURL) {
  throw new Error("Missing VITE_API_BASE_URL");
}

const api = axios.create({
  baseURL,
});

api.interceptors.request.use(
  (config) => {
    const token = getToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
    }
    return Promise.reject(error);
  }
);

export default api;