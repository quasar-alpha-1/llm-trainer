import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const getJobs = () => axios.get(`${API_BASE}/api/jobs`).then(r => r.data);
export const getJob = (id) => axios.get(`${API_BASE}/api/jobs/${id}`).then(r => r.data);
export const createJob = (data) => axios.post(`${API_BASE}/api/jobs`, data).then(r => r.data);
export const getModels = () => axios.get(`${API_BASE}/api/models`).then(r => r.data);
export const getDatasets = () => axios.get(`${API_BASE}/api/datasets`).then(r => r.data);
export const uploadDataset = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post(`${API_BASE}/api/datasets/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data);
};
export const cancelJob = (id) => axios.post(`${API_BASE}/api/jobs/${id}/cancel`).then(r => r.data);
export const postComment = (id, comment) => axios.post(`${API_BASE}/api/jobs/${id}/comments`, { comment }).then(r => r.data);
export const downloadWeights = (id, format) => axios.get(`${API_BASE}/api/jobs/${id}/download?format=${format}`, { responseType: 'blob' });
export const exportToHF = (id, repo, token) => axios.post(`${API_BASE}/api/jobs/${id}/export_hf`, { repo, token }).then(r => r.data);
export const importFromHF = (repo, token) => axios.post(`${API_BASE}/api/models/import_hf`, { repo, token }).then(r => r.data);
export const getLocalModels = () => axios.get(`${API_BASE}/api/local-models`).then(r => r.data);
export const deleteLocalModel = (id) => axios.delete(`${API_BASE}/api/local-models/${id}`).then(r => r.data);
export const saveHfToken = (token) => axios.post(`${API_BASE}/api/settings/hf-token`, { token }).then(r => r.data);
export const getSettings = () => axios.get(`${API_BASE}/api/settings`).then(r => r.data);
export const updateSettings = (data) => axios.post(`${API_BASE}/api/settings`, data).then(r => r.data);