import axios from "axios";

export const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export const setToken = (t) => localStorage.setItem("token", t);

export const clearToken = () => localStorage.removeItem("token");

export const getToken = () => localStorage.getItem("token");