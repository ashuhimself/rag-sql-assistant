import React, { useState } from 'react';
import styled from 'styled-components';
import QueryResult from './QueryResult';
import { databaseAPI } from '../services/api';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
`;

const SqlEditor = styled.textarea`
  width: 100%;
  height: 200px;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 1rem;

  &:focus {
    outline: none;
    border-color: #3498db;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const ExecuteButton = styled.button`
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;

  &:hover {
    background: #2980b9;
  }

  &:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }
`;

const ClearButton = styled.button`
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;

  &:hover {
    background: #7f8c8d;
  }
`;

const ResultContainer = styled.div`
  flex: 1;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
`;

const ExampleQueries = styled.div`
  margin-bottom: 1rem;
`;

const ExampleTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
`;

const ExampleQuery = styled.div`
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 0.5rem;
  margin-bottom: 0.25rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  cursor: pointer;

  &:hover {
    background: #e9ecef;
  }
`;

const SqlExecutor: React.FC = () => {
  const [sql, setSql] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exampleQueries = [
    'SELECT COUNT(*) as total_customers FROM customers;',
    'SELECT customer_segment, COUNT(*) as count FROM customers GROUP BY customer_segment;',
    'SELECT * FROM accounts WHERE balance > 10000 LIMIT 10;',
    'SELECT t.transaction_type, COUNT(*) as count FROM transactions t GROUP BY t.transaction_type;',
    'SELECT c.first_name, c.last_name, a.balance FROM customers c JOIN accounts a ON c.customer_id = a.customer_id ORDER BY a.balance DESC LIMIT 5;'
  ];

  const executeQuery = async () => {
    if (!sql.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await databaseAPI.executeQuery(sql);
      setResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const clearEditor = () => {
    setSql('');
    setResult(null);
    setError(null);
  };

  const handleExampleClick = (query: string) => {
    setSql(query);
  };

  return (
    <Container>
      <ExampleQueries>
        <ExampleTitle>Example Queries:</ExampleTitle>
        {exampleQueries.map((query, index) => (
          <ExampleQuery key={index} onClick={() => handleExampleClick(query)}>
            {query}
          </ExampleQuery>
        ))}
      </ExampleQueries>

      <SqlEditor
        value={sql}
        onChange={(e) => setSql(e.target.value)}
        placeholder="Enter your SQL query here... (e.g., SELECT * FROM customers LIMIT 10;)"
      />

      <ButtonContainer>
        <ExecuteButton onClick={executeQuery} disabled={isLoading || !sql.trim()}>
          {isLoading ? 'Executing...' : 'Execute Query'}
        </ExecuteButton>
        <ClearButton onClick={clearEditor}>
          Clear
        </ClearButton>
      </ButtonContainer>

      <ResultContainer>
        {error && (
          <div style={{ padding: '1rem', color: '#e74c3c', background: '#fdf2f2' }}>
            Error: {error}
          </div>
        )}
        {result && <QueryResult result={result} />}
        {!result && !error && (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#7f8c8d' }}>
            Execute a SQL query to see results here
          </div>
        )}
      </ResultContainer>
    </Container>
  );
};

export default SqlExecutor;