import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface AnalyticsRequest {
  query: string;
  analysis_type?: string;
  session_id?: string;
}

export interface BusinessMetricsResponse {
  success: boolean;
  metrics: {
    customer_metrics: {
      total_customers: number;
      premium_customer_rate: number;
      avg_credit_score: number;
      avg_annual_income: number;
    };
    account_metrics: {
      total_accounts: number;
      total_balance: number;
      avg_account_balance: number;
      negative_balance_rate: number;
    };
    loan_metrics: {
      total_loans: number;
      total_loan_portfolio: number;
      total_outstanding: number;
      default_rate: number;
      avg_interest_rate: number;
    };
    transaction_metrics: {
      monthly_transaction_count: number;
      monthly_transaction_volume: number;
      avg_transaction_amount: number;
    };
  };
  calculated_at: string;
}

export interface CohortAnalysisRequest {
  cohort_type: 'customer_acquisition' | 'transaction_behavior' | 'loan_performance';
  time_period: 'monthly' | 'quarterly' | 'yearly';
}

export interface SmartInsightsRequest {
  query: string;
}

export interface Insight {
  type: string;
  title: string;
  description: string;
  significance: number;
  metric: string;
  value: number;
}

export interface VisualizationConfig {
  type: 'histogram' | 'bar' | 'line' | 'scatter' | 'pie';
  title: string;
  x_column: string;
  y_column?: string;
  description: string;
}

export interface AnalysisResult {
  success: boolean;
  query_result: {
    success: boolean;
    data: any[][];
    columns: string[];
    row_count: number;
  };
  analysis: {
    descriptive: any;
    statistical: any;
    insights: Insight[];
    visualizations: VisualizationConfig[];
    recommendations: string[];
    metadata: {
      analysis_type: string;
      row_count: number;
      column_count: number;
    };
  };
  analysis_type: string;
}

class AnalyticsService {
  private axiosInstance = axios.create({
    baseURL: `${API_BASE_URL}/api/analytics/`,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async analyzeData(request: AnalyticsRequest): Promise<AnalysisResult> {
    try {
      const response = await this.axiosInstance.post('analyze/', request);
      return response.data;
    } catch (error) {
      console.error('Error analyzing data:', error);
      throw new Error('Failed to analyze data');
    }
  }

  async getBusinessMetrics(): Promise<BusinessMetricsResponse> {
    try {
      const response = await this.axiosInstance.get('metrics/');
      return response.data;
    } catch (error) {
      console.error('Error fetching business metrics:', error);
      throw new Error('Failed to fetch business metrics');
    }
  }

  async performCohortAnalysis(request: CohortAnalysisRequest): Promise<any> {
    try {
      const response = await this.axiosInstance.post('cohort/', request);
      return response.data;
    } catch (error) {
      console.error('Error performing cohort analysis:', error);
      throw new Error('Failed to perform cohort analysis');
    }
  }

  async getSmartInsights(request: SmartInsightsRequest): Promise<any> {
    try {
      const response = await this.axiosInstance.post('insights/', request);
      return response.data;
    } catch (error) {
      console.error('Error generating smart insights:', error);
      throw new Error('Failed to generate smart insights');
    }
  }

  async getAnalysisReports(sessionId?: string): Promise<any> {
    try {
      const params = sessionId ? { session_id: sessionId } : {};
      const response = await this.axiosInstance.get('reports/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching analysis reports:', error);
      throw new Error('Failed to fetch analysis reports');
    }
  }

  async getAnalysisReportDetail(reportId: number): Promise<any> {
    try {
      const response = await this.axiosInstance.get(`reports/${reportId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching analysis report detail:', error);
      throw new Error('Failed to fetch analysis report detail');
    }
  }
}

export const analyticsService = new AnalyticsService();