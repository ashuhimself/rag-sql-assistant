import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
`;

const InputContainer = styled.div`
  flex: 1;
  position: relative;
`;

const TextArea = styled.textarea<{ disabled: boolean }>`
  width: 100%;
  min-height: 44px;
  max-height: 120px;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 22px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.4;
  outline: none;
  background: ${props => props.disabled ? '#f8f9fa' : 'white'};
  color: ${props => props.disabled ? '#6c757d' : '#333'};

  &:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }

  &::placeholder {
    color: #adb5bd;
  }

  &:disabled {
    cursor: not-allowed;
  }
`;

const SendButton = styled.button<{ disabled: boolean }>`
  background: ${props => props.disabled ? '#e9ecef' : '#007bff'};
  color: ${props => props.disabled ? '#6c757d' : 'white'};
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #0056b3;
    transform: scale(1.05);
  }

  &:active:not(:disabled) {
    transform: scale(0.95);
  }
`;

const CharCount = styled.div<{ warning: boolean }>`
  position: absolute;
  bottom: -1.5rem;
  right: 0.5rem;
  font-size: 0.75rem;
  color: ${props => props.warning ? '#dc3545' : '#6c757d'};
`;

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message..."
}) => {
  const [message, setMessage] = useState('');
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const maxLength = 5000;

  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = 'auto';
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled) {
      onSendMessage(trimmed);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
    }
  };

  const isNearLimit = message.length > maxLength * 0.8;
  const canSend = message.trim().length > 0 && !disabled;

  return (
    <Container>
      <InputContainer>
        <TextArea
          ref={textAreaRef}
          value={message}
          onChange={handleChange}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
        />
        <CharCount warning={isNearLimit}>
          {message.length}/{maxLength}
        </CharCount>
      </InputContainer>

      <SendButton
        onClick={handleSubmit}
        disabled={!canSend}
        title="Send message (Enter)"
      >
        ↑
      </SendButton>
    </Container>
  );
};

export default MessageInput;