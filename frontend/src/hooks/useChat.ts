import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { ChatMessage, ChatRequest, ChatSession } from '../types';
import { chatAPI } from '../services/api';

export const useChat = () => {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      id: Date.now(),
      message_type: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const request: ChatRequest = {
        message: content.trim(),
        session_id: currentSession?.session_id || uuidv4(),
      };

      const response = await chatAPI.sendMessage(request);

      if (response.success) {
        // Update session if it's new
        if (!currentSession) {
          const newSession: ChatSession = {
            id: Date.now(),
            session_id: response.session_id,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            messages: [],
          };
          setCurrentSession(newSession);
        }

        // Add assistant response
        setMessages(prev => [...prev, response.message]);
      } else {
        throw new Error(response.error || 'Failed to send message');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);

      // Add error message to chat
      const errorChatMessage: ChatMessage = {
        id: Date.now() + 1,
        message_type: 'system',
        content: `Error: ${errorMessage}`,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorChatMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [currentSession]);

  const loadSession = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const session = await chatAPI.getSession(sessionId);
      setCurrentSession(session);
      setMessages(session.messages);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startNewSession = useCallback(() => {
    setCurrentSession(null);
    setMessages([]);
    setError(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    currentSession,
    messages,
    isLoading,
    error,
    sendMessage,
    loadSession,
    startNewSession,
    clearError,
  };
};