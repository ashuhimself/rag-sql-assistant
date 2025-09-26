import React from 'react';
import styled, { keyframes } from 'styled-components';

const bounce = keyframes`
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
`;

const Container = styled.div`
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1rem;
`;

const LoadingBubble = styled.div`
  max-width: 70%;
  padding: 1rem 1.25rem;
  border-radius: 18px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const DotsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Dot = styled.div`
  width: 8px;
  height: 8px;
  background: #007bff;
  border-radius: 50%;
  animation: ${bounce} 1.4s infinite ease-in-out both;

  &:nth-child(1) {
    animation-delay: -0.32s;
  }

  &:nth-child(2) {
    animation-delay: -0.16s;
  }

  &:nth-child(3) {
    animation-delay: 0;
  }
`;

const LoadingText = styled.span`
  color: #6c757d;
  font-style: italic;
  margin-left: 0.5rem;
`;

const LoadingIndicator: React.FC = () => {
  return (
    <Container>
      <LoadingBubble>
        <DotsContainer>
          <Dot />
          <Dot />
          <Dot />
          <LoadingText>Thinking...</LoadingText>
        </DotsContainer>
      </LoadingBubble>
    </Container>
  );
};

export default LoadingIndicator;