/**
 * AI Security Analyst - API Client
 */
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${url}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }
    return response;
  } catch (error) {
    if (error.message === 'Failed to fetch') {
      throw new Error('Cannot connect to backend. Make sure the server is running on port 8000.');
    }
    throw error;
  }
}

export async function uploadLog(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/logs/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Upload failed: ${res.status}`);
  }
  return res.json();
}

export async function analyzeSample(sampleName) {
  const res = await request(`/api/logs/upload-sample/${sampleName}`, { method: 'POST' });
  return res.json();
}

export async function getAnalysis(analysisId) {
  const res = await request(`/api/logs/analysis/${analysisId}`);
  return res.json();
}

export async function getThreats(analysisId) {
  const res = await request(`/api/logs/threats/${analysisId}`);
  return res.json();
}

export async function listAnalyses() {
  const res = await request('/api/logs/list');
  return res.json();
}

export async function sendChatMessage(analysisId, message) {
  const res = await request('/api/chat/message', {
    method: 'POST',
    body: JSON.stringify({ analysis_id: analysisId, message }),
  });
  return res.json();
}

export async function getChatHistory(analysisId) {
  const res = await request(`/api/chat/history/${analysisId}`);
  return res.json();
}

export async function clearChatHistory(analysisId) {
  const res = await request(`/api/chat/history/${analysisId}`, { method: 'DELETE' });
  return res.json();
}

export async function generateReport(analysisId, companyName = 'Your Company') {
  const res = await request('/api/reports/generate', {
    method: 'POST',
    body: JSON.stringify({ analysis_id: analysisId, company_name: companyName }),
  });
  return res.json();
}

export function getReportDownloadUrl(reportId) {
  return `${API_BASE}/api/reports/download/${reportId}`;
}

export async function healthCheck() {
  const res = await request('/api/health');
  return res.json();
}

export async function getSamples() {
  const res = await request('/api/samples');
  return res.json();
}
