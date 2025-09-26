import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
`;

const Content = styled.div`
  flex: 1;
`;

const Title = styled.div`
  font-weight: 600;
  color: #721c24;
  margin-bottom: 0.25rem;
`;

const Message = styled.div`
  color: #721c24;
  font-size: 0.9rem;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #721c24;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  margin-left: 1rem;
  opacity: 0.7;

  &:hover {
    opacity: 1;
  }
`;

interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onDismiss }) => {
  return (
    <Container>
      <Content>
        <Title>Error</Title>
        <Message>{message}</Message>
      </Content>
      {onDismiss && (
        <CloseButton onClick={onDismiss} title="Dismiss">
          ×
        </CloseButton>
      )}
    </Container>
  );
};

export default ErrorMessage;