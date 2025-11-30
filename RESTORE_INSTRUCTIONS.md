# Code Restoration Guide

This file contains all the code changes from our session. Use this to restore any lost work.

## 1. src/services/chatApi.ts
**Line 7** - Change from:
```typescript
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8080';
```
To:
```typescript
const API_BASE_URL = typeof window !== 'undefined' && (window as any).env?.REACT_APP_BACKEND_URL
  || 'http://localhost:8080';
```

## 2. src/components/chatbot/ChatButton.css
**Replace entire file with:**
```css
/**
 * ChatButton styles - Floating action button with label
 */

.chat-button-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
  position: relative;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.7), 0 0 0 8px rgba(102, 126, 234, 0.2);
  }
}

.chat-button:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
  animation: none;
}

.chat-button:active {
  transform: scale(0.95);
}

.chat-button--open {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  animation: none;
}

.chat-button svg {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.chat-button-label {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  opacity: 0;
  transform: translateX(10px);
  animation: slideIn 0.5s ease-out 1s forwards;
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.chat-button--open + .chat-button-label {
  display: none;
}

@media (max-width: 768px) {
  .chat-button {
    width: 56px;
    height: 56px;
  }

  .chat-button-label {
    font-size: 12px;
    padding: 6px 12px;
  }
}
```

## 3. src/components/chatbot/ChatButton.tsx
**Replace the return statement (lines 14-58) with:**
```typescript
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
          // Chat icon
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
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>
      {!isOpen && <div className="chat-button-label">Ask Rowshni about FAR</div>}
    </div>
  );
};
```

## 4. docs/intro.md
**After line 10 (after "Welcome to the FAR Reference Book..."), add:**
```markdown

:::tip 💬 Try the AI-Powered FAR Assistant

**Have a question about federal acquisition regulations?** Our intelligent chatbot can instantly search through all FAR Parts 1-3 to provide answers with precise citations.

**Click the pulsing purple button in the bottom-right corner to start chatting!**

Example questions you can ask:
- "What are the general contracting requirements?"
- "Explain the policy on contract modifications"
- "What are the rules for small business set-asides?"

:::
```

**In "How to Use This Reference" section, change first bullet to:**
```markdown
- **AI Assistant**: Click the pulsing button in the bottom-right to ask questions and get instant answers with citations
```

**Remove the old "## Interactive Chatbot" section (lines 52-59 in original)**

## 5. backend/api/routes/chat.py
**Add import at top (after line 12):**
```python
from backend.api.middleware.rate_limiter import rate_limiter
```

**Add rate limiting check in send_message_simple function (after line 26):**
```python
        # Check rate limit (20 messages per hour)
        rate_limiter.check_rate_limit(
            conversation_id=str(conversation_id),
            max_requests=20,
            window_minutes=60
        )
```

**Update docstring for send_message_simple (after line 20):**
```python
    """
    Simplified endpoint that returns plain dicts instead of Pydantic models.
    Workaround for serialization issue.

    Rate limit: 20 messages per hour per conversation.
    """
```

## New Files Created:
1. `backend/api/middleware/rate_limiter.py` - Rate limiting implementation
2. `backend/api/middleware/__init__.py` - Middleware module init

All files have been documented above. Apply these changes to restore your work!
