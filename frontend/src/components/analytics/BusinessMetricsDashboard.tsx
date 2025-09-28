import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { analyticsService, BusinessMetricsResponse } from '../../services/analyticsService';

const DashboardContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin: 16px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const DashboardTitle = styled.h2`
  margin: 0 0 24px 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
`;

const MetricCategory = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
`;

const CategoryTitle = styled.h3`
  margin: 0 0 16px 0;
  color: #495057;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MetricItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #dee2e6;

  &:last-child {
    border-bottom: none;
  }
`;

const MetricLabel = styled.span`
  color: #666;
  font-size: 14px;
`;

const MetricValue = styled.span<{ highlight?: boolean }>`
  font-weight: 600;
  font-size: 14px;
  color: ${props => props.highlight ? '#007bff' : '#333'};
`;

const RefreshButton = styled.button`
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    background: #0056b3;
  }

  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  color: #666;
`;

const ErrorMessage = styled.div`
  background: #f8d7da;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
  margin: 16px 0;
`;

const LastUpdated = styled.div`
  color: #666;
  font-size: 12px;
  text-align: right;
  margin-top: 16px;
`;

const BusinessMetricsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<BusinessMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await analyticsService.getBusinessMetrics();
      setMetrics(response);
    } catch (err) {
      setError('Failed to load business metrics');
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value: number, decimals: number = 0) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <DashboardContainer>
        <LoadingSpinner>
          <div>🔄 Loading business metrics...</div>
        </LoadingSpinner>
      </DashboardContainer>
    );
  }

  if (error) {
    return (
      <DashboardContainer>
        <DashboardTitle>📊 Metrics Dashboard</DashboardTitle>
        <ErrorMessage>{error}</ErrorMessage>
        <RefreshButton onClick={fetchMetrics}>
          🔄 Retry
        </RefreshButton>
      </DashboardContainer>
    );
  }

  if (!metrics) {
    return null;
  }

  return (
    <DashboardContainer>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <DashboardTitle>📊 Metrics Dashboard</DashboardTitle>
        <RefreshButton onClick={fetchMetrics} disabled={loading}>
          🔄 Refresh
        </RefreshButton>
      </div>

      <MetricsGrid>
        {/* Customer Metrics */}
        <MetricCategory>
          <CategoryTitle>👥 Customer Metrics</CategoryTitle>
          <MetricItem>
            <MetricLabel>Total Customers</MetricLabel>
            <MetricValue highlight>
              {formatNumber(metrics.metrics.customer_metrics.total_customers)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Premium Customer Rate</MetricLabel>
            <MetricValue>
              {formatPercentage(metrics.metrics.customer_metrics.premium_customer_rate)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Avg Credit Score</MetricLabel>
            <MetricValue>
              {formatNumber(metrics.metrics.customer_metrics.avg_credit_score)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Avg Annual Income</MetricLabel>
            <MetricValue>
              {formatCurrency(metrics.metrics.customer_metrics.avg_annual_income)}
            </MetricValue>
          </MetricItem>
        </MetricCategory>

        {/* Account Metrics */}
        <MetricCategory>
          <CategoryTitle>🏦 Account Metrics</CategoryTitle>
          <MetricItem>
            <MetricLabel>Total Accounts</MetricLabel>
            <MetricValue highlight>
              {formatNumber(metrics.metrics.account_metrics.total_accounts)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Total Balance</MetricLabel>
            <MetricValue>
              {formatCurrency(metrics.metrics.account_metrics.total_balance)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Avg Account Balance</MetricLabel>
            <MetricValue>
              {formatCurrency(metrics.metrics.account_metrics.avg_account_balance)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Negative Balance Rate</MetricLabel>
            <MetricValue>
              {formatPercentage(metrics.metrics.account_metrics.negative_balance_rate)}
            </MetricValue>
          </MetricItem>
        </MetricCategory>

        {/* Loan Metrics */}
        <MetricCategory>
          <CategoryTitle>💰 Loan Portfolio</CategoryTitle>
          <MetricItem>
            <MetricLabel>Total Loans</MetricLabel>
            <MetricValue highlight>
              {formatNumber(metrics.metrics.loan_metrics.total_loans)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Total Portfolio Value</MetricLabel>
            <MetricValue>
              {formatCurrency(metrics.metrics.loan_metrics.total_loan_portfolio)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Outstanding Balance</MetricLabel>
            <MetricValue>
              {formatCurrency(metrics.metrics.loan_metrics.total_outstanding)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Default Rate</MetricLabel>
            <MetricValue>
              {formatPercentage(metrics.metrics.loan_metrics.default_rate)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Avg Interest Rate</MetricLabel>
            <MetricValue>
              {formatPercentage(metrics.metrics.loan_metrics.avg_interest_rate)}
            </MetricValue>
          </MetricItem>
        </MetricCategory>

        {/* Transaction Metrics */}
        <MetricCategory>
          <CategoryTitle>💳 Transactions (30 days)</CategoryTitle>
          <MetricItem>
            <MetricLabel>Monthly Transaction Count</MetricLabel>
            <MetricValue highlight>
              {formatNumber(metrics.metrics.transaction_metrics.monthly_transaction_count)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Monthly Volume</MetricLabel>
            <MetricValue>
              {formatCurrency(metrics.metrics.transaction_metrics.monthly_transaction_volume)}
            </MetricValue>
          </MetricItem>
          <MetricItem>
            <MetricLabel>Avg Transaction Amount</MetricLabel>
            <MetricValue>
              {formatCurrency(metrics.metrics.transaction_metrics.avg_transaction_amount)}
            </MetricValue>
          </MetricItem>
        </MetricCategory>
      </MetricsGrid>

      <LastUpdated>
        Last updated: {new Date(metrics.calculated_at).toLocaleString()}
      </LastUpdated>
    </DashboardContainer>
  );
};

export default BusinessMetricsDashboard;