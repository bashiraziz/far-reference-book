/**
 * ChatMessage - Individual message component.
 */

import React from 'react';
import { type Message } from '../../services/chatApi';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`chat-message ${isUser ? 'chat-message--user' : 'chat-message--assistant'}`}>
      <div className="chat-message-content">
        <div className="chat-message-text">{message.content}</div>

        {/* Show sources for assistant messages */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="chat-message-sources">
            <p className="chat-sources-title">Sources:</p>
            <ul className="chat-sources-list">
              {message.sources.map((source, index) => (
                <li key={index} className="chat-source-item">
                  <strong>FAR {source.section}</strong>
                  {source.page && ` (Page ${source.page})`}
                  <span className="chat-source-score">
                    {Math.round(source.relevance_score * 100)}% match
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Show metadata for assistant messages */}
        {!isUser && message.token_count && (
          <div className="chat-message-meta">
            {message.processing_time_ms && (
              <span>{(message.processing_time_ms / 1000).toFixed(1)}s</span>
            )}
            {message.token_count && <span>{message.token_count} tokens</span>}
          </div>
        )}
      </div>
    </div>
  );
};
