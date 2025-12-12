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
          // Modern AI Sparkles icon
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M12 0.5L13.5 6.5L19.5 8L13.5 9.5L12 15.5L10.5 9.5L4.5 8L10.5 6.5L12 0.5Z" />
            <path d="M19 14L19.75 16.25L22 17L19.75 17.75L19 20L18.25 17.75L16 17L18.25 16.25L19 14Z" />
            <path d="M7 17L7.5 18.5L9 19L7.5 19.5L7 21L6.5 19.5L5 19L6.5 18.5L7 17Z" />
          </svg>
        )}
      </button>
      {!isOpen && <div className="chat-button-label">Ask Rowshni about FAR</div>}
    </div>
  );
};
