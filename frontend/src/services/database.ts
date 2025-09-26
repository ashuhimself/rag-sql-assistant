import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface TableInfo {
  table_name: string;
  row_count: number;
  description: string;
}

export interface Relationship {
  from: string;
  to: string;
  type: string;
}

export interface DatabaseStats {
  total_tables: number;
  total_rows: number;
  tables: TableInfo[];
  relationships: Relationship[];
}

export const databaseAPI = {
  async getStats(): Promise<DatabaseStats> {
    const response = await axios.get(`${API_BASE_URL}/api/database/stats/`);
    return response.data;
  },

  async testConnection(): Promise<{ success: boolean; message: string }> {
    const response = await axios.get(`${API_BASE_URL}/api/database/test/`);
    return response.data;
  }
};