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

export async function askQuestion(query, top_k = null) {
  const payload = { query: query.trim() };
  if (top_k !== null) {
    payload.top_k = top_k;
  }
  const { data } = await axios.post(`${API_BASE}/ask`, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return data;
}

