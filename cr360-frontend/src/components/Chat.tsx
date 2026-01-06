/**
 * Chat Component
 * Main chat interface for querying CR360 backend
 */

import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../services/api';
import { logger } from '../utils/logger';
import { ResultsTable } from './ResultsTable';
import { AmbiguityCard } from './AmbiguityCard';
import { ErrorCard } from './ErrorCard';
import { LoadingSpinner } from './LoadingSpinner';
import type {
  ChatResponse,
  ChatSuccessResponse,
  AmbiguityResponse,
  ErrorResponse,
  Message,
  Clarification,
} from '../types/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: ChatResponse;
  timestamp: Date;
}

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>();
  const [pendingClarification, setPendingClarification] = useState<{
    query: string;
    ambiguityResponse: AmbiguityResponse;
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logger.componentMount('Chat');
    return () => logger.componentUnmount('Chat');
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (query: string) => {
    if (!query.trim() || isLoading) return;

    const userMessageId = `user-${Date.now()}`;
    const userMessage: ChatMessage = {
      id: userMessageId,
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    logger.info('User submitted query', { query, conversationId });
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Build conversation history
      const conversationHistory: Message[] = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Send query to backend
      const response = await apiClient.sendQueryWithHistory(
        query,
        conversationId,
        conversationHistory
      );

      // Store conversation ID for future messages
      if (response.success) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.success
          ? `Found ${response.result.row_count} results`
          : 'Query processed',
        response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      logger.error('Failed to send query', error);

      // Add error message
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Failed to process query',
        response: {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          error_type: 'NetworkError',
          timestamp: new Date().toISOString(),
        },
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    logger.info('User clicked suggestion', { suggestion });
    setInputValue(suggestion);
  };

  const handleClarificationSubmit = async (
    clarifications: Clarification[],
    originalQuery: string
  ) => {
    logger.info('User submitted clarifications', {
      clarifications,
      originalQuery,
      conversationId
    });

    setIsLoading(true);
    setPendingClarification(null);

    try {
      // Build conversation history
      const conversationHistory: Message[] = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Send clarified query to backend
      const response = await apiClient.sendQueryWithHistory(
        originalQuery,
        conversationId,
        conversationHistory,
        false, // check_ambiguity = false
        clarifications // Pass clarifications
      );

      // Store conversation ID for future messages
      if (response.success) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.success
          ? `Found ${response.result.row_count} results`
          : 'Query processed',
        response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      logger.error('Failed to send clarified query', error);

      // Add error message
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Failed to process clarified query',
        response: {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          error_type: 'NetworkError',
          timestamp: new Date().toISOString(),
        },
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSubmit(inputValue);
  };

  const renderResponse = (response: ChatResponse) => {
    if (response.success) {
      const successResponse = response as ChatSuccessResponse;
      return (
        <ResultsTable
          data={successResponse.result.results}
          explanation={successResponse.result.explanation}
          sql={successResponse.result.sql}
        />
      );
    }

    // Check for ambiguity response
    if ('is_ambiguous' in response && response.is_ambiguous) {
      const ambiguityResponse = response as AmbiguityResponse;
      return (
        <AmbiguityCard
          message="Your query needs clarification"
          reasons={ambiguityResponse.reasons}
          suggestions={ambiguityResponse.suggestions}
          questions={ambiguityResponse.questions}
          originalQuery={ambiguityResponse.query}
          onSuggestionClick={handleSuggestionClick}
          onClarificationSubmit={handleClarificationSubmit}
        />
      );
    }

    const errorResponse = response as ErrorResponse;
    return (
      <ErrorCard
        errorType={errorResponse.error_type}
        message={errorResponse.error}
        details={errorResponse.details}
      />
    );
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#f9fafb'}}>
      {/* Header */}
      <div style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '20px 24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{fontSize: '24px', fontWeight: 'bold', color: '#111827', margin: 0}}>
          CR360 Credit Risk Analytics
        </h1>
        <p style={{fontSize: '14px', color: '#6b7280', marginTop: '4px', marginBottom: 0}}>
          Ask questions about your credit portfolio in natural language
        </p>
      </div>

      {/* Messages Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        maxWidth: '1200px',
        width: '100%',
        margin: '0 auto'
      }}>
        {messages.length === 0 && (
          <div style={{textAlign: 'center', padding: '48px 24px'}}>
            <h2 style={{fontSize: '20px', fontWeight: '600', color: '#374151', marginBottom: '16px'}}>
              Welcome to CR360
            </h2>
            <p style={{color: '#6b7280', marginBottom: '24px'}}>
              Try asking questions like:
            </p>
            <div style={{maxWidth: '600px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '8px'}}>
              {[
                'What is the total outstanding balance for the latest quarter?',
                'Show me outstanding balance by product for Q4 2024',
                'What is the 30+ day delinquency rate for Q4 2024?',
                'Show me all available quarters in the data',
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(example)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '12px 16px',
                    backgroundColor: 'white',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '14px',
                    color: '#374151',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = '#3b82f6';
                    e.currentTarget.style.backgroundColor = '#eff6ff';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = '#d1d5db';
                    e.currentTarget.style.backgroundColor = 'white';
                  }}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} style={{marginBottom: '24px'}}>
            {/* User message */}
            {message.role === 'user' && (
              <div style={{display: 'flex', justifyContent: 'flex-end', marginBottom: '12px'}}>
                <div style={{
                  backgroundColor: '#2563eb',
                  color: 'white',
                  borderRadius: '12px',
                  padding: '12px 16px',
                  maxWidth: '80%',
                  wordWrap: 'break-word'
                }}>
                  <p style={{margin: 0, fontSize: '14px', lineHeight: '1.5'}}>{message.content}</p>
                </div>
              </div>
            )}

            {/* Assistant response */}
            {message.role === 'assistant' && message.response && (
              <div style={{marginTop: '8px'}}>
                {renderResponse(message.response)}
              </div>
            )}
          </div>
        ))}

        {isLoading && <LoadingSpinner />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{
        backgroundColor: 'white',
        borderTop: '1px solid #e5e7eb',
        padding: '16px 24px',
        boxShadow: '0 -1px 3px rgba(0,0,0,0.1)'
      }}>
        <form onSubmit={handleFormSubmit} style={{maxWidth: '1200px', margin: '0 auto'}}>
          <div style={{display: 'flex', gap: '12px'}}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about your credit portfolio..."
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '12px 16px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                backgroundColor: isLoading ? '#f3f4f6' : 'white',
                cursor: isLoading ? 'not-allowed' : 'text'
              }}
              onFocus={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                }
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#d1d5db';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              style={{
                padding: '12px 24px',
                backgroundColor: (isLoading || !inputValue.trim()) ? '#9ca3af' : '#2563eb',
                color: 'white',
                borderRadius: '8px',
                fontWeight: '500',
                border: 'none',
                cursor: (isLoading || !inputValue.trim()) ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => {
                if (!isLoading && inputValue.trim()) {
                  e.currentTarget.style.backgroundColor = '#1d4ed8';
                }
              }}
              onMouseOut={(e) => {
                if (!isLoading && inputValue.trim()) {
                  e.currentTarget.style.backgroundColor = '#2563eb';
                }
              }}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
