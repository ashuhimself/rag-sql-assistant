export interface ChatMessage {
  id: number;
  message_type: 'user' | 'assistant' | 'system';
  content: string;
  sql_query?: string;
  sql_result?: any;
  created_at: string;
}

export interface ChatSession {
  id: number;
  session_id: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  session_id: string;
  message: ChatMessage;
  success: boolean;
  error?: string;
}

export interface QueryResult {
  success: boolean;
  data?: any[][];
  columns?: string[];
  row_count?: number;
  query?: string;
  error?: string;
  truncated?: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}