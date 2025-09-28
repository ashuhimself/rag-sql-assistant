import React from 'react';
import styled from 'styled-components';
import { Insight } from '../../services/analyticsService';

const PanelContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const PanelTitle = styled.h3`
  margin: 0 0 16px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const InsightCard = styled.div<{ significance: number }>`
  background: ${props =>
    props.significance > 0.8 ? '#fff3cd' :
    props.significance > 0.5 ? '#d1ecf1' :
    '#f8f9fa'};
  border: 1px solid ${props =>
    props.significance > 0.8 ? '#ffc107' :
    props.significance > 0.5 ? '#bee5eb' :
    '#e9ecef'};
  border-radius: 6px;
  padding: 16px;
  margin: 12px 0;
`;

const InsightType = styled.span<{ type: string }>`
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  background: ${props => {
    switch (props.type) {
      case 'trend': return '#e3f2fd';
      case 'anomaly': return '#ffebee';
      case 'correlation': return '#f3e5f5';
      case 'pattern': return '#e8f5e8';
      default: return '#f5f5f5';
    }
  }};
  color: ${props => {
    switch (props.type) {
      case 'trend': return '#1976d2';
      case 'anomaly': return '#c62828';
      case 'correlation': return '#7b1fa2';
      case 'pattern': return '#388e3c';
      default: return '#666';
    }
  }};
`;

const InsightTitle = styled.h4`
  margin: 8px 0 4px 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
`;

const InsightDescription = styled.p`
  margin: 4px 0 8px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.4;
`;

const SignificanceBar = styled.div<{ level: number }>`
  width: 100%;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 8px;

  &::after {
    content: '';
    display: block;
    width: ${props => props.level * 100}%;
    height: 100%;
    background: ${props =>
      props.level > 0.8 ? '#dc3545' :
      props.level > 0.5 ? '#ffc107' :
      '#28a745'};
    transition: width 0.3s ease;
  }
`;

const RecommendationCard = styled.div`
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 16px;
  margin: 12px 0;
`;

const RecommendationText = styled.p`
  margin: 0;
  color: #495057;
  font-size: 14px;
  line-height: 1.5;
`;

const StatsSummary = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 16px 0;
`;

const StatCard = styled.div`
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

interface InsightsPanelProps {
  insights: Insight[];
  recommendations: string[];
  statisticalSummary?: any;
  metadata?: {
    analysis_type: string;
    row_count: number;
    column_count: number;
  };
}

const InsightsPanel: React.FC<InsightsPanelProps> = ({
  insights,
  recommendations,
  statisticalSummary,
  metadata
}) => {
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'trend': return '📈';
      case 'anomaly': return '⚠️';
      case 'correlation': return '🔗';
      case 'pattern': return '🔍';
      case 'threshold': return '🚨';
      case 'forecast': return '🔮';
      default: return '💡';
    }
  };

  return (
    <PanelContainer>
      <PanelTitle>
        🧠 Analytics Insights
      </PanelTitle>

      {metadata && (
        <StatsSummary>
          <StatCard>
            <StatValue>{metadata.row_count.toLocaleString()}</StatValue>
            <StatLabel>Records Analyzed</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>{metadata.column_count}</StatValue>
            <StatLabel>Columns</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>{insights.length}</StatValue>
            <StatLabel>Insights Found</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>{metadata.analysis_type}</StatValue>
            <StatLabel>Analysis Type</StatLabel>
          </StatCard>
        </StatsSummary>
      )}

      {insights.length > 0 && (
        <div>
          <h4>🔎 Key Insights</h4>
          {insights.map((insight, index) => (
            <InsightCard key={index} significance={insight.significance}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span>{getInsightIcon(insight.type)}</span>
                <InsightType type={insight.type}>{insight.type}</InsightType>
              </div>
              <InsightTitle>{insight.title}</InsightTitle>
              <InsightDescription>{insight.description}</InsightDescription>
              <div style={{ fontSize: '12px', color: '#666' }}>
                Metric: {insight.metric} | Value: {insight.value.toLocaleString()}
              </div>
              <SignificanceBar level={insight.significance} />
            </InsightCard>
          ))}
        </div>
      )}

      {recommendations.length > 0 && (
        <div>
          <h4>💡 Recommendations</h4>
          {recommendations.map((recommendation, index) => (
            <RecommendationCard key={index}>
              <RecommendationText>{recommendation}</RecommendationText>
            </RecommendationCard>
          ))}
        </div>
      )}

      {statisticalSummary && Object.keys(statisticalSummary).length > 0 && (
        <div>
          <h4>📊 Statistical Summary</h4>
          <pre style={{
            background: '#f8f9fa',
            padding: '12px',
            borderRadius: '4px',
            fontSize: '12px',
            overflow: 'auto',
            maxHeight: '200px'
          }}>
            {JSON.stringify(statisticalSummary, null, 2)}
          </pre>
        </div>
      )}
    </PanelContainer>
  );
};

export default InsightsPanel;