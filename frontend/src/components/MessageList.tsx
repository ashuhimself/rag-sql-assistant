import React from 'react';
import styled from 'styled-components';
import { ChatMessage } from '../types';
import MessageBubble from './MessageBubble';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const WelcomeMessage = styled.div`
  background: #e8f4f8;
  border: 1px solid #b8daff;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  color: #495057;
`;

const WelcomeTitle = styled.h3`
  margin: 0 0 1rem 0;
  color: #2c3e50;
`;

const ExampleQueries = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
`;

const ExampleQuery = styled.div`
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0.75rem;
  font-size: 0.9rem;
  color: #6c757d;
`;

interface MessageListProps {
  messages: ChatMessage[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <Container>
        <WelcomeMessage>
          <WelcomeTitle>👋 Welcome to Warehouse Copilot!</WelcomeTitle>
          <p>
            I can help you query the banking database containing information about customers,
            accounts, transactions, loans, and payments. Ask me questions in natural language!
          </p>

          <ExampleQueries>
            <ExampleQuery>
              "How many customers do we have?"
            </ExampleQuery>
            <ExampleQuery>
              "Show me the top 10 customers by account balance"
            </ExampleQuery>
            <ExampleQuery>
              "What are the most recent transactions?"
            </ExampleQuery>
            <ExampleQuery>
              "How many active loans are there?"
            </ExampleQuery>
            <ExampleQuery>
              "Show customers from New York"
            </ExampleQuery>
            <ExampleQuery>
              "What's the average loan amount?"
            </ExampleQuery>
          </ExampleQueries>
        </WelcomeMessage>
      </Container>
    );
  }

  return (
    <Container>
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </Container>
  );
};

export default MessageList;