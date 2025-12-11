/**
 * ChatMessage - Individual message component with streaming effect.
 */

import React, { useState, useEffect } from 'react';
import { type Message } from '../../services/chatApi';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
  onRegenerate?: () => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isStreaming = false,
  onRegenerate
}) => {
  const isUser = message.role === 'user';
  const [displayedText, setDisplayedText] = useState('');
  const [isStreamingActive, setIsStreamingActive] = useState(isStreaming);
  const [areSourcesExpanded, setAreSourcesExpanded] = useState(false);
  const [expandedSourceIndex, setExpandedSourceIndex] = useState<number | null>(null);
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied'>('idle');

  // Copy text to clipboard
  const handleCopy = async (includeSourcesText: boolean = false) => {
    let textToCopy = message.content;

    if (includeSourcesText && message.sources && message.sources.length > 0) {
      textToCopy += '\n\nSources:\n';
      message.sources.forEach((source, index) => {
        textToCopy += `${index + 1}. FAR ${source.section}`;
        if (source.page) textToCopy += ` (Page ${source.page})`;
        textToCopy += ` - ${Math.round(source.relevance_score * 100)}% match\n`;
      });
    }

    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopyStatus('copied');
      setTimeout(() => setCopyStatus('idle'), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Streaming effect for assistant messages
  useEffect(() => {
    if (isStreaming && !isUser && message.content) {
      setIsStreamingActive(true);
      let currentIndex = 0;
      const fullText = message.content;

      // Show text character by character
      const intervalId = setInterval(() => {
        if (currentIndex < fullText.length) {
          setDisplayedText(fullText.slice(0, currentIndex + 1));
          currentIndex++;
        } else {
          setIsStreamingActive(false);
          clearInterval(intervalId);
        }
      }, 15); // 15ms per character = ~67 chars/second (natural reading speed)

      return () => clearInterval(intervalId);
    } else {
      // Show full text immediately for user messages or non-streaming messages
      setDisplayedText(message.content);
      setIsStreamingActive(false);
    }
  }, [message.content, isStreaming, isUser]);

  return (
    <div className={`chat-message ${isUser ? 'chat-message--user' : 'chat-message--assistant'}`}>
      <div className="chat-message-content">
        <div className="chat-message-text">
          {displayedText}
          {isStreamingActive && <span className="streaming-cursor">▋</span>}
        </div>

        {/* Show sources for assistant messages */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="chat-message-sources">
            <button
              className="chat-sources-toggle"
              onClick={() => setAreSourcesExpanded(!areSourcesExpanded)}
              aria-expanded={areSourcesExpanded}
            >
              <span className="chat-sources-toggle-icon">
                {areSourcesExpanded ? '▼' : '▶'}
              </span>
              <span className="chat-sources-toggle-text">
                {message.sources.length} Source{message.sources.length > 1 ? 's' : ''}
              </span>
            </button>

            {areSourcesExpanded && (
              <div className="chat-sources-list">
                {message.sources.map((source, index) => {
                  const isTopSource = index === 0;
                  const isExpanded = expandedSourceIndex === index;

                  return (
                    <div
                      key={index}
                      className={`chat-source-card ${isTopSource ? 'chat-source-card--top' : ''}`}
                    >
                      <div className="chat-source-header">
                        <div className="chat-source-info">
                          <strong className="chat-source-section">
                            FAR {source.section}
                          </strong>
                          {source.page && (
                            <span className="chat-source-page">Page {source.page}</span>
                          )}
                        </div>
                        {isTopSource && (
                          <span className="chat-source-badge">Best Match</span>
                        )}
                      </div>

                      <div className="chat-source-score-container">
                        <div className="chat-source-score-bar-bg">
                          <div
                            className="chat-source-score-bar"
                            style={{ width: `${source.relevance_score * 100}%` }}
                          />
                        </div>
                        <span className="chat-source-score-text">
                          {Math.round(source.relevance_score * 100)}%
                        </span>
                      </div>

                      {source.excerpt && (
                        <div className="chat-source-excerpt-container">
                          <button
                            className="chat-source-excerpt-toggle"
                            onClick={() => setExpandedSourceIndex(isExpanded ? null : index)}
                          >
                            {isExpanded ? 'Hide' : 'Show'} excerpt
                          </button>
                          {isExpanded && (
                            <p className="chat-source-excerpt">
                              {source.excerpt}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
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

        {/* Message actions */}
        <div className="chat-message-actions">
          <button
            className="chat-message-action-btn"
            onClick={() => handleCopy(false)}
            title="Copy message"
            disabled={copyStatus === 'copied'}
          >
            {copyStatus === 'copied' ? (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
                <span>Copied</span>
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                </svg>
                <span>Copy</span>
              </>
            )}
          </button>

          {!isUser && message.sources && message.sources.length > 0 && (
            <button
              className="chat-message-action-btn"
              onClick={() => handleCopy(true)}
              title="Copy with sources"
              disabled={copyStatus === 'copied'}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" />
              </svg>
              <span>Copy w/ sources</span>
            </button>
          )}

          {!isUser && onRegenerate && !isStreamingActive && (
            <button
              className="chat-message-action-btn"
              onClick={onRegenerate}
              title="Regenerate response"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0118.8-4.3M22 12.5a10 10 0 01-18.8 4.2" />
              </svg>
              <span>Regenerate</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
