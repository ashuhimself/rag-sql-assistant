import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { databaseAPI, DatabaseStats, TableInfo, Relationship } from '../services/database';

const Container = styled.div`
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
`;

const Title = styled.h3`
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const StatCard = styled.div`
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 0.25rem;
`;

const TabContainer = styled.div`
  display: flex;
  border-bottom: 1px solid #e9ecef;
  margin-bottom: 1rem;
`;

const Tab = styled.button<{ active: boolean }>`
  background: ${props => props.active ? '#3498db' : 'transparent'};
  color: ${props => props.active ? 'white' : '#6c757d'};
  border: none;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: 4px 4px 0 0;
  font-weight: ${props => props.active ? 'bold' : 'normal'};

  &:hover {
    background: ${props => props.active ? '#3498db' : '#f8f9fa'};
  }
`;

const TableGrid = styled.div`
  display: grid;
  gap: 0.75rem;
`;

const TableRow = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 3fr;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
  align-items: center;
`;

const TableName = styled.div`
  font-weight: bold;
  color: #2c3e50;
`;

const RowCount = styled.div`
  color: #3498db;
  font-weight: bold;
  text-align: center;
`;

const Description = styled.div`
  color: #6c757d;
  font-size: 0.9rem;
`;

const RelationshipGrid = styled.div`
  display: grid;
  gap: 0.5rem;
`;

const RelationshipRow = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 2fr;
  gap: 1rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  align-items: center;
  text-align: center;
`;

const TableRefName = styled.div`
  font-weight: bold;
  color: #2c3e50;
`;

const RelationType = styled.div`
  color: #e67e22;
  font-size: 0.8rem;
  font-weight: bold;
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #6c757d;
  padding: 2rem;
`;

const ErrorMessage = styled.div`
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
`;

const RefreshButton = styled.button`
  background: #28a745;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;

  &:hover {
    background: #218838;
  }
`;

const DatabaseInfo: React.FC = () => {
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'tables' | 'relationships'>('tables');

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await databaseAPI.getStats();
      setStats(data);
    } catch (err) {
      setError('Failed to load database statistics');
      console.error('Error fetching database stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading database information...</LoadingMessage>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage>{error}</ErrorMessage>
        <RefreshButton onClick={fetchStats}>Retry</RefreshButton>
      </Container>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <Container>
      <Header>
        <Title>Database Overview</Title>
        <RefreshButton onClick={fetchStats}>Refresh</RefreshButton>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatValue>{stats.total_tables}</StatValue>
          <StatLabel>Tables</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{stats.total_rows.toLocaleString()}</StatValue>
          <StatLabel>Total Records</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{stats.tables.filter(t => t.row_count > 0).length}</StatValue>
          <StatLabel>Active Tables</StatLabel>
        </StatCard>
      </StatsGrid>

      <TabContainer>
        <Tab
          active={activeTab === 'tables'}
          onClick={() => setActiveTab('tables')}
        >
          Tables & Data
        </Tab>
        <Tab
          active={activeTab === 'relationships'}
          onClick={() => setActiveTab('relationships')}
        >
          Relationships
        </Tab>
      </TabContainer>

      {activeTab === 'tables' && (
        <TableGrid>
          {stats.tables.map((table: TableInfo) => (
            <TableRow key={table.table_name}>
              <TableName>{table.table_name}</TableName>
              <RowCount>{table.row_count.toLocaleString()}</RowCount>
              <Description>{table.description}</Description>
            </TableRow>
          ))}
        </TableGrid>
      )}

      {activeTab === 'relationships' && (
        <RelationshipGrid>
          {stats.relationships && stats.relationships.map((rel: Relationship, index: number) => (
            <RelationshipRow key={index}>
              <TableRefName>{rel.from}</TableRefName>
              <RelationType>{rel.type}</RelationType>
              <TableRefName>{rel.to}</TableRefName>
            </RelationshipRow>
          ))}
        </RelationshipGrid>
      )}
    </Container>
  );
};

export default DatabaseInfo;