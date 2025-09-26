import React from 'react';
import styled from 'styled-components';
import { QueryResult as QueryResultType } from '../types';

const Container = styled.div`
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
`;

const Header = styled.div`
  background: #f8f9fa;
  padding: 0.75rem;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.85rem;
  color: #6c757d;
`;

const TableContainer = styled.div`
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
`;

const Th = styled.th`
  background: #f8f9fa;
  padding: 0.75rem 0.5rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
`;

const Td = styled.td`
  padding: 0.5rem;
  border-bottom: 1px solid #f8f9fa;
  vertical-align: top;
`;

const Tr = styled.tr`
  &:hover {
    background: #f8f9fa;
  }
`;

const ErrorMessage = styled.div`
  padding: 1rem;
  background: #f8d7da;
  color: #721c24;
  border-radius: 4px;
`;

const EmptyMessage = styled.div`
  padding: 2rem;
  text-align: center;
  color: #6c757d;
  font-style: italic;
`;

const TruncatedWarning = styled.div`
  background: #fff3cd;
  color: #856404;
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
  border-top: 1px solid #ffeaa7;
`;

interface QueryResultProps {
  result: QueryResultType;
}

const QueryResult: React.FC<QueryResultProps> = ({ result }) => {
  if (!result.success) {
    return (
      <Container>
        <ErrorMessage>
          <strong>Query Error:</strong> {result.error || 'Unknown error occurred'}
        </ErrorMessage>
      </Container>
    );
  }

  const { data = [], columns = [], row_count = 0, truncated = false } = result;

  if (row_count === 0) {
    return (
      <Container>
        <EmptyMessage>
          No results found
        </EmptyMessage>
      </Container>
    );
  }

  const formatCellValue = (value: any) => {
    if (value === null || value === undefined) {
      return <em style={{ color: '#6c757d' }}>null</em>;
    }
    if (typeof value === 'boolean') {
      return value ? 'true' : 'false';
    }
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    return String(value);
  };

  return (
    <Container>
      <Header>
        {row_count} row{row_count !== 1 ? 's' : ''} returned
        {columns.length > 0 && ` • ${columns.length} column${columns.length !== 1 ? 's' : ''}`}
      </Header>

      <TableContainer>
        <Table>
          <thead>
            <tr>
              {columns.map((column, index) => (
                <Th key={index}>{column}</Th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <Tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <Td key={cellIndex}>
                    {formatCellValue(cell)}
                  </Td>
                ))}
              </Tr>
            ))}
          </tbody>
        </Table>
      </TableContainer>

      {truncated && (
        <TruncatedWarning>
          ⚠️ Results truncated for display. Only showing first {data.length} rows.
        </TruncatedWarning>
      )}
    </Container>
  );
};

export default QueryResult;