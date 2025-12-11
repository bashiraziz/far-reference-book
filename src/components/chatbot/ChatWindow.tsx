/**
 * ChatWindow - Main chat interface UI.
 */

import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { type Message } from '../../services/chatApi';
import './ChatWindow.css';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  streamingMessageId: string | null;
  onSendMessage: (content: string) => void;
  onRegenerateMessage: (messageId: string) => void;
  onClearConversation: () => void;
  onClose: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  error,
  streamingMessageId,
  onSendMessage,
  onRegenerateMessage,
  onClearConversation,
  onClose,
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <div className="chat-window">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <h3>FAR Assistant</h3>
          <p className="chat-subtitle">Ask questions about Federal Acquisition Regulations</p>
        </div>
        <div className="chat-header-actions">
          <button
            className="chat-header-btn"
            onClick={onClearConversation}
            title="Clear conversation"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
            </svg>
          </button>
          <button className="chat-header-btn" onClick={onClose} title="Close chat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="chat-welcome-header">
              <div className="chat-welcome-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                  <path d="M8 10h.01M12 10h.01M16 10h.01" />
                </svg>
              </div>
              <h3>Welcome to FAR Assistant</h3>
              <p className="chat-welcome-subtitle">
                Your AI-powered guide to Federal Acquisition Regulations
              </p>
            </div>

            <div className="chat-welcome-stats">
              <div className="chat-welcome-stat">
                <div className="chat-welcome-stat-value">53</div>
                <div className="chat-welcome-stat-label">FAR Parts</div>
              </div>
              <div className="chat-welcome-stat">
                <div className="chat-welcome-stat-value">7,718</div>
                <div className="chat-welcome-stat-label">Sections Indexed</div>
              </div>
              <div className="chat-welcome-stat">
                <div className="chat-welcome-stat-value">AI</div>
                <div className="chat-welcome-stat-label">Powered Search</div>
              </div>
            </div>

            <div className="chat-welcome-section">
              <p className="chat-welcome-section-title">Popular Questions</p>
              <div className="chat-welcome-cards">
                <button
                  className="chat-welcome-card"
                  onClick={() => onSendMessage("What is FAR Section 5.101?")}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <path d="M21 21l-4.35-4.35" />
                  </svg>
                  <span>What is FAR Section 5.101?</span>
                </button>
                <button
                  className="chat-welcome-card"
                  onClick={() => onSendMessage("Explain small business set-asides")}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                  <span>Small business set-asides</span>
                </button>
                <button
                  className="chat-welcome-card"
                  onClick={() => onSendMessage("What are the contract modification rules?")}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" />
                  </svg>
                  <span>Contract modifications</span>
                </button>
                <button
                  className="chat-welcome-card"
                  onClick={() => onSendMessage("What are socioeconomic programs?")}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
                  </svg>
                  <span>Socioeconomic programs</span>
                </button>
              </div>
            </div>

            <p className="chat-welcome-tip">
              💡 Tip: Ask specific questions about FAR sections, regulations, or requirements
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isStreaming={message.id === streamingMessageId}
                onRegenerate={
                  message.role === 'assistant'
                    ? () => onRegenerateMessage(message.id)
                    : undefined
                }
              />
            ))}
            {isLoading && (
              <div className="chat-loading">
                <div className="chat-loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </>
        )}
        {error && (
          <div className="chat-error">
            <strong>Error:</strong> {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about FAR..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="chat-send-btn"
          disabled={!inputValue.trim() || isLoading}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </form>
    </div>
  );
};
