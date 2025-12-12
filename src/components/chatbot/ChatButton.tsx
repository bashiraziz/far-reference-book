/**
 * ChatButton - Floating action button to open/close chat.
 */

import React from 'react';
import './ChatButton.css';

interface ChatButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export const ChatButton: React.FC<ChatButtonProps> = ({ onClick, isOpen }) => {
  return (
    <div className="chat-button-container">
      <button
        className={`chat-button ${isOpen ? 'chat-button--open' : ''}`}
        onClick={onClick}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
        title={isOpen ? 'Close chat' : 'Ask questions about FAR'}
      >
        {isOpen ? (
          // Close icon
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          // Sparkles icon
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 3v3" />
            <path d="M12 18v3" />
            <path d="M3 12h3" />
            <path d="M18 12h3" />
            <path d="m19 19-2.5-2.5" />
            <path d="m5 5 2.5 2.5" />
            <path d="M19 5l-2.5 2.5" />
            <path d="M5 19l2.5-2.5" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        )}
      </button>
      {!isOpen && <div className="chat-button-label">Ask Rowshni about FAR</div>}
    </div>
  );
};
