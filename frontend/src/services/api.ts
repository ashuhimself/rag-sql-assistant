import axios from 'axios';
import { ChatRequest, ChatResponse, ChatSession, QueryResult, ApiResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat/', request);
    return response.data;
  },

  getSession: async (sessionId: string): Promise<ChatSession> => {
    const response = await api.get(`/chat/sessions/${sessionId}/`);
    return response.data;
  },

  listSessions: async (): Promise<ChatSession[]> => {
    const response = await api.get('/chat/sessions/');
    return response.data;
  },
};

export const databaseAPI = {
  executeQuery: async (query: string): Promise<QueryResult> => {
    const response = await api.post('/database/execute/', { query });
    return response.data;
  },

  testConnection: async (): Promise<ApiResponse> => {
    const response = await api.get('/database/test/');
    return response.data;
  },

  listTables: async (): Promise<ApiResponse<string[]>> => {
    const response = await api.get('/database/tables/');
    return response.data;
  },

  getTableInfo: async (tableName: string): Promise<ApiResponse> => {
    const response = await api.get(`/database/tables/${tableName}/`);
    return response.data;
  },
};

export const embeddingsAPI = {
  searchSchemas: async (query: string, limit: number = 3): Promise<ApiResponse> => {
    const response = await api.post('/embeddings/search/', { query, limit });
    return response.data;
  },

  listSchemas: async (): Promise<ApiResponse> => {
    const response = await api.get('/embeddings/schemas/');
    return response.data;
  },

  embedSchema: async (data: {
    table_name: string;
    ddl_statement: string;
    description?: string;
  }): Promise<ApiResponse> => {
    const response = await api.post('/embeddings/embed/', data);
    return response.data;
  },
};

export default api;