/**
 * ChatWindow - Main chat interface UI with voice capabilities.
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
  isMinimized: boolean;
  onSendMessage: (content: string) => void;
  onRegenerateMessage: (messageId: string) => void;
  onClearConversation: () => void;
  onMinimize: () => void;
  onClose: () => void;
}

// Check browser support for voice features
const isSpeechRecognitionSupported = typeof window !== 'undefined' &&
  ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

const isSpeechSynthesisSupported = typeof window !== 'undefined' &&
  'speechSynthesis' in window;

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  error,
  streamingMessageId,
  isMinimized,
  onSendMessage,
  onRegenerateMessage,
  onClearConversation,
  onMinimize,
  onClose,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceOutputEnabled, setVoiceOutputEnabled] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const previousMessageCountRef = useRef(messages.length);
  const recognitionRef = useRef<any>(null);
  const lastSpokenMessageIdRef = useRef<string | null>(null);

  // Auto-scroll to bottom ONLY when new messages are added (not on mount)
  useEffect(() => {
    // Only scroll if messages were actually added (not on initial load)
    if (messages.length > previousMessageCountRef.current && messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
    previousMessageCountRef.current = messages.length;
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  // Normalize FAR section numbers from speech recognition
  const normalizeFARSectionNumbers = (text: string): string => {
    let normalized = text;

    // Fix section numbers like "32. 006" or "32 .006" → "32.006"
    normalized = normalized.replace(/(\d+)\s*\.\s*(\d+)/g, '$1.$2');

    // Fix subsection dashes like "6 - 5" or "6- 5" → "6-5"
    normalized = normalized.replace(/(\d+)\s*-\s*(\d+)/g, '$1-$2');

    // Fix "section 32. 006- 5" type patterns (combination of above)
    normalized = normalized.replace(/section\s+(\d+)\s*\.\s*(\d+)\s*-\s*(\d+)/gi, 'section $1.$2-$3');

    // Fix "part 32. 0" → "part 32.0"
    normalized = normalized.replace(/part\s+(\d+)\s*\.\s*(\d+)/gi, 'part $1.$2');

    // Fix standalone patterns like "32.00 6" → "32.006" (digit followed by space and more digits after decimal)
    normalized = normalized.replace(/(\d+\.\d+)\s+(\d+)/g, '$1$2');

    return normalized;
  };

  // Voice Input: Speech Recognition
  const startListening = () => {
    if (!isSpeechRecognitionSupported) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      const normalizedText = normalizeFARSectionNumbers(transcript);
      setInputValue(normalizedText);
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        alert(`Voice input error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  // Voice Output: Read assistant responses aloud
  useEffect(() => {
    if (!voiceOutputEnabled || !isSpeechSynthesisSupported) return;

    // Find the latest assistant message
    const assistantMessages = messages.filter(m => m.role === 'assistant');
    const latestAssistantMessage = assistantMessages[assistantMessages.length - 1];

    // Only speak if it's a new message we haven't spoken yet
    if (latestAssistantMessage &&
        latestAssistantMessage.id !== lastSpokenMessageIdRef.current &&
        !streamingMessageId) { // Don't speak while streaming

      lastSpokenMessageIdRef.current = latestAssistantMessage.id;

      // Stop any ongoing speech
      window.speechSynthesis.cancel();

      // Speak the new message
      const utterance = new SpeechSynthesisUtterance(latestAssistantMessage.content);
      utterance.rate = 1.0;
      utterance.pitch = 1;
      utterance.volume = 1;

      window.speechSynthesis.speak(utterance);
    }
  }, [messages, voiceOutputEnabled, streamingMessageId]);

  // Cleanup speech on unmount
  useEffect(() => {
    return () => {
      if (isSpeechSynthesisSupported) {
        window.speechSynthesis.cancel();
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  return (
    <div className={`chat-window ${isMinimized ? 'chat-window-minimized' : ''}`}>
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <h3>FAR Assistant</h3>
          {!isMinimized && (
            <p className="chat-subtitle">Ask Rowshni questions about Federal Acquisition Regulations and other FAR related topics</p>
          )}
        </div>
        <div className="chat-header-actions">
          {isSpeechSynthesisSupported && (
            <button
              className={`chat-header-btn ${voiceOutputEnabled ? 'voice-active' : ''}`}
              onClick={() => {
                setVoiceOutputEnabled(!voiceOutputEnabled);
                if (voiceOutputEnabled) {
                  window.speechSynthesis.cancel();
                }
              }}
              title={voiceOutputEnabled ? "Disable voice responses" : "Enable voice responses"}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                {voiceOutputEnabled ? (
                  <>
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                  </>
                ) : (
                  <>
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                    <line x1="23" y1="9" x2="17" y2="15" />
                    <line x1="17" y1="9" x2="23" y2="15" />
                  </>
                )}
              </svg>
            </button>
          )}
          <button
            className="chat-header-btn"
            onClick={onClearConversation}
            title="Clear conversation"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
            </svg>
          </button>
          <button
            className="chat-header-btn"
            onClick={onMinimize}
            title={isMinimized ? "Expand chat" : "Minimize chat"}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {isMinimized ? (
                <path d="M18 15l-6-6-6 6" />
              ) : (
                <path d="M6 9l6 6 6-6" />
              )}
            </svg>
          </button>
          <button className="chat-header-btn" onClick={onClose} title="Close chat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages - hide when minimized */}
      {!isMinimized && (
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
      )}

      {/* Input - hide when minimized */}
      {!isMinimized && (
        <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder={isListening ? "Listening..." : "Ask a question about FAR..."}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading || isListening}
        />
        {isSpeechRecognitionSupported && (
          <button
            type="button"
            className={`chat-voice-btn ${isListening ? 'listening' : ''}`}
            onClick={isListening ? stopListening : startListening}
            disabled={isLoading}
            title={isListening ? "Stop listening" : "Voice input"}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
          </button>
        )}
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
      )}
    </div>
  );
};
