import React, { useState } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ChatMessage } from '../types';
import QueryResult from './QueryResult';
import DataVisualization from './analytics/DataVisualization';
import InsightsPanel from './analytics/InsightsPanel';

const Container = styled.div<{ messageType: string }>`
  display: flex;
  justify-content: ${props => props.messageType === 'user' ? 'flex-end' : 'flex-start'};
  margin-bottom: 1rem;
`;

const Bubble = styled.div<{ messageType: string }>`
  max-width: 70%;
  padding: 1rem 1.25rem;
  border-radius: 18px;
  background: ${props => {
    if (props.messageType === 'user') return '#007bff';
    if (props.messageType === 'system') return '#dc3545';
    return '#f8f9fa';
  }};
  color: ${props => {
    if (props.messageType === 'user') return 'white';
    if (props.messageType === 'system') return 'white';
    return '#333';
  }};
  border: ${props => props.messageType === 'assistant' ? '1px solid #e9ecef' : 'none'};
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const MessageContent = styled.div`
  word-wrap: break-word;

  p:last-child {
    margin-bottom: 0;
  }

  code {
    background: rgba(0,0,0,0.1);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-size: 0.9em;
  }
`;

const SqlSection = styled.div`
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
`;

const SqlHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
`;

const SqlLabel = styled.span`
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;

  &:hover {
    background: rgba(0,123,255,0.1);
  }
`;

const SqlContainer = styled.div`
  background: #2d3748;
  border-radius: 6px;
  overflow: hidden;
`;

const Timestamp = styled.div`
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.5rem;
`;

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showSql, setShowSql] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Container messageType={message.message_type}>
      <Bubble messageType={message.message_type}>
        <MessageContent>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </MessageContent>

        {message.sql_query && (
          <SqlSection>
            <SqlHeader>
              <SqlLabel>SQL Query</SqlLabel>
              <ToggleButton onClick={() => setShowSql(!showSql)}>
                {showSql ? 'Hide' : 'Show'} SQL
              </ToggleButton>
            </SqlHeader>
            {showSql && (
              <SqlContainer>
                <SyntaxHighlighter
                  language="sql"
                  style={tomorrow}
                  customStyle={{
                    margin: 0,
                    fontSize: '0.85rem',
                  }}
                >
                  {message.sql_query}
                </SyntaxHighlighter>
              </SqlContainer>
            )}
          </SqlSection>
        )}

        {message.sql_result && (
          <SqlSection>
            <SqlHeader>
              <SqlLabel>Query Result</SqlLabel>
              <ToggleButton onClick={() => setShowResult(!showResult)}>
                {showResult ? 'Hide' : 'Show'} Result
              </ToggleButton>
            </SqlHeader>
            {showResult && (
              <QueryResult result={message.sql_result} />
            )}
          </SqlSection>
        )}

        {message.sql_result && message.sql_result.analysis && (
          <SqlSection>
            <SqlHeader>
              <SqlLabel>📊 Analytics & Insights</SqlLabel>
              <ToggleButton onClick={() => setShowAnalytics(!showAnalytics)}>
                {showAnalytics ? 'Hide' : 'Show'} Analytics
              </ToggleButton>
            </SqlHeader>
            {showAnalytics && (
              <div>
                {/* Insights Panel */}
                <InsightsPanel
                  insights={message.sql_result.analysis.insights || []}
                  recommendations={message.sql_result.analysis.recommendations || []}
                  statisticalSummary={message.sql_result.analysis.statistical}
                  metadata={message.sql_result.analysis.metadata}
                />

                {/* Visualizations */}
                {message.sql_result.analysis.visualizations &&
                 message.sql_result.analysis.visualizations.length > 0 && (
                  <div>
                    {message.sql_result.analysis.visualizations.slice(0, 3).map((vizConfig: any, index: number) => (
                      <DataVisualization
                        key={index}
                        config={vizConfig}
                        data={message.sql_result.data || []}
                        columns={message.sql_result.columns || []}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </SqlSection>
        )}

        <Timestamp>
          {formatTimestamp(message.created_at)}
        </Timestamp>
      </Bubble>
    </Container>
  );
};

export default MessageBubble;