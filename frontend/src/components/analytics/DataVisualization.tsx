import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import styled from 'styled-components';
import { VisualizationConfig } from '../../services/analyticsService';

const ChartContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const ChartTitle = styled.h3`
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
`;

const ChartDescription = styled.p`
  margin: 0 0 16px 0;
  color: #666;
  font-size: 14px;
`;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

interface DataVisualizationProps {
  config: VisualizationConfig;
  data: any[];
  columns: string[];
}

const DataVisualization: React.FC<DataVisualizationProps> = ({ config, data, columns }) => {
  // Transform data for visualization
  const transformedData = React.useMemo(() => {
    if (!data || !data.length) return [];

    return data.map(row => {
      const item: any = {};
      columns.forEach((col, index) => {
        item[col] = row[index];
      });
      return item;
    });
  }, [data, columns]);

  const renderChart = () => {
    switch (config.type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={transformedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={config.x_column} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar
                dataKey={config.y_column || columns.find(col => col !== config.x_column) || columns[1] || 'value'}
                fill="#0088FE"
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={transformedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={config.x_column} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey={config.y_column || columns.find(col => col !== config.x_column) || columns[1] || 'value'}
                stroke="#0088FE"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={transformedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={config.x_column} type="number" />
              <YAxis dataKey={config.y_column} type="number" />
              <Tooltip />
              <Legend />
              <Scatter fill="#0088FE" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'pie':
        const pieData = transformedData.slice(0, 8); // Limit to 8 slices for readability
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey={config.y_column || columns.find(col => col !== config.x_column) || columns[1] || 'value'}
                nameKey={config.x_column}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                label
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'histogram':
        // For histogram, we need to create bins
        const numericData = transformedData
          .map(item => item[config.x_column])
          .filter(val => typeof val === 'number')
          .sort((a, b) => a - b);

        if (numericData.length === 0) {
          return <div>No numeric data available for histogram</div>;
        }

        const bins = 10;
        const min = Math.min(...numericData);
        const max = Math.max(...numericData);
        const binSize = (max - min) / bins;

        const histogramData = Array.from({ length: bins }, (_, i) => {
          const binStart = min + i * binSize;
          const binEnd = binStart + binSize;
          const count = numericData.filter(val => val >= binStart && val < binEnd).length;
          return {
            range: `${binStart.toFixed(1)}-${binEnd.toFixed(1)}`,
            count
          };
        });

        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={histogramData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0088FE" />
            </BarChart>
          </ResponsiveContainer>
        );

      default:
        return <div>Unsupported chart type: {config.type}</div>;
    }
  };

  return (
    <ChartContainer>
      <ChartTitle>{config.title}</ChartTitle>
      <ChartDescription>{config.description}</ChartDescription>
      {renderChart()}
    </ChartContainer>
  );
};

export default DataVisualization;