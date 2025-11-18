import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export async function uploadDocuments(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const { data } = await axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function askQuestion(query) {
  const { data } = await axios.post(`${API_BASE}/ask`, { query });
  return data;
}

