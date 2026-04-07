import type {
  ApiErrorResponse,
  DeleteMaterialResponse,
  ExerciseRequest,
  ExerciseResponse,
  HealthResponse,
  IndexResponse,
  MaterialsResponse,
  QueryRequest,
  SuggestMaterialMetadataResponse,
  TextModeResponse,
  UpdateMaterialMetadataRequest,
  UpdateMaterialMetadataResponse,
  UploadResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim();

if (!API_BASE_URL) {
  throw new Error('缺少 VITE_API_BASE_URL 环境变量，请在 frontend/.env 中配置后端地址。');
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = (await response.json().catch(() => ({}))) as T & ApiErrorResponse;

  if (!response.ok || (typeof data === 'object' && data !== null && 'error' in data && data.error)) {
    throw new Error(extractErrorMessage(data, response.status));
  }

  return data as T;
}

function extractErrorMessage(data: ApiErrorResponse, status: number): string {
  if (data.error) {
    return data.error;
  }

  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => item.msg).filter(Boolean).join('；') || `请求失败（${status}）`;
  }

  if (typeof data.detail === 'string') {
    return data.detail;
  }

  if (data.message) {
    return data.message;
  }

  return `请求失败（${status}）`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
  });

  return parseResponse<T>(response);
}

export function getHealth() {
  return request<HealthResponse>('/');
}

export async function uploadMaterial(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  return request<UploadResponse>('/materials/upload', {
    method: 'POST',
    body: formData,
  });
}

export function buildIndex() {
  return request<IndexResponse>('/materials/index', {
    method: 'POST',
  });
}

export function getMaterials() {
  return request<MaterialsResponse>('/materials');
}

export function deleteMaterial(filename: string) {
  return request<DeleteMaterialResponse>(`/materials/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  });
}

export function updateMaterialMetadata(filename: string, payload: UpdateMaterialMetadataRequest) {
  return request<UpdateMaterialMetadataResponse>(`/materials/${encodeURIComponent(filename)}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export function suggestMaterialMetadata(filename: string) {
  return request<SuggestMaterialMetadataResponse>(`/materials/${encodeURIComponent(filename)}/suggest-metadata`, {
    method: 'POST',
  });
}

export function askQuestion(payload: QueryRequest) {
  return request<TextModeResponse>('/qa/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export function explainTeaching(payload: QueryRequest) {
  return request<TextModeResponse>('/teaching/explain', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export function generateExercises(payload: ExerciseRequest) {
  return request<ExerciseResponse>('/exercises/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}
