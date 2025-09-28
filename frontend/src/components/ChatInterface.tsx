import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useChat } from '../hooks/useChat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import DatabaseInfo from './DatabaseInfo';
import SqlExecutor from './SqlExecutor';
import BusinessMetricsDashboard from './analytics/BusinessMetricsDashboard';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const Sidebar = styled.div`
  width: 350px;
  background: #f1f3f4;
  border-right: 1px solid #e9ecef;
  overflow-y: auto;
  padding: 1rem;
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

const Header = styled.div`
  background: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
`;

const Subtitle = styled.p`
  margin: 0.5rem 0 0 0;
  opacity: 0.8;
  font-size: 0.9rem;
`;

const ChatArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
`;

const InputContainer = styled.div`
  padding: 1rem;
  background: white;
  border-top: 1px solid #e9ecef;
`;

const NewChatButton = styled.button`
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 1rem;
  font-size: 0.9rem;

  &:hover {
    background: #2980b9;
  }
`;

const SessionInfo = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const TabContainer = styled.div`
  background: #34495e;
  border-bottom: 1px solid #2c3e50;
`;

const TabList = styled.div`
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
`;

const Tab = styled.button<{ active: boolean }>`
  background: ${props => props.active ? '#2c3e50' : 'transparent'};
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  border-bottom: 2px solid ${props => props.active ? '#3498db' : 'transparent'};

  &:hover {
    background: #2c3e50;
  }
`;

const ChatInterface: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'sql' | 'analytics'>('chat');

  const {
    messages,
    isLoading,
    error,
    sendMessage,
    startNewSession,
    clearError,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  const handleNewChat = () => {
    startNewSession();
  };

  return (
    <Container>
      <Header>
        <SessionInfo>
          <div>
            <Title>Warehouse Copilot</Title>
            <Subtitle>
              Ask questions about banking data - customers, accounts, transactions, loans & more
            </Subtitle>
          </div>
          {activeTab === 'chat' && (
            <NewChatButton onClick={handleNewChat}>
              New Chat
            </NewChatButton>
          )}
        </SessionInfo>
      </Header>

      <TabContainer>
        <TabList>
          <Tab active={activeTab === 'chat'} onClick={() => setActiveTab('chat')}>
            💬 Chat Assistant
          </Tab>
          <Tab active={activeTab === 'sql'} onClick={() => setActiveTab('sql')}>
            ⚡ SQL Executor
          </Tab>
          <Tab active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')}>
            📊 Analytics Dashboard
          </Tab>
        </TabList>
      </TabContainer>

      <MainContent>
        <Sidebar>
          <DatabaseInfo />
        </Sidebar>

        <ChatContainer>
          {activeTab === 'chat' ? (
            <ChatArea>
              <MessagesContainer>
                {error && (
                  <ErrorMessage message={error} onDismiss={clearError} />
                )}

                <MessageList messages={messages} />

                {isLoading && <LoadingIndicator />}

                <div ref={messagesEndRef} />
              </MessagesContainer>

              <InputContainer>
                <MessageInput
                  onSendMessage={handleSendMessage}
                  disabled={isLoading}
                  placeholder="Ask about banking data: 'How many customers do we have?' or 'Show recent transactions'"
                />
              </InputContainer>
            </ChatArea>
          ) : activeTab === 'sql' ? (
            <SqlExecutor />
          ) : (
            <div style={{ overflow: 'auto', padding: '1rem' }}>
              <BusinessMetricsDashboard />
            </div>
          )}
        </ChatContainer>
      </MainContent>
    </Container>
  );
};

export default ChatInterface;