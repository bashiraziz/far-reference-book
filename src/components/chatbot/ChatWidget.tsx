/**
 * ChatWidget - Main chat component for FAR chatbot.
 *
 * Manages conversation state, message history, and UI visibility.
 */

import React, { useState, useEffect } from 'react';
import { ChatButton } from './ChatButton';
import { ChatWindow } from './ChatWindow';
import { chatApi, type Message } from '../../services/chatApi';
import './ChatWidget.css';

export const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize conversation only when chat is opened for the first time
  useEffect(() => {
    if (isOpen && !conversationId) {
      initializeConversation();
    }
  }, [isOpen]);

  // Load conversation from localStorage or create new one
  const initializeConversation = async () => {
    try {
      // Check for existing conversation in localStorage
      const savedConvId = localStorage.getItem('far_conversation_id');

      if (savedConvId) {
        // Try to load existing conversation
        try {
          const conversation = await chatApi.getConversation(savedConvId);
          setConversationId(conversation.id);

          // Load message history
          const history = await chatApi.getMessages(conversation.id);
          setMessages(history);
          return;
        } catch (err) {
          // Conversation doesn't exist, create new one
          console.log('Saved conversation not found, creating new one');
        }
      }

      // Create new conversation
      const conversation = await chatApi.createConversation({
        source: 'docusaurus_chat_widget',
      });

      setConversationId(conversation.id);
      localStorage.setItem('far_conversation_id', conversation.id);
    } catch (err) {
      console.error('Failed to initialize conversation:', err);
      setError('Failed to initialize chat. Please refresh the page.');
    }
  };

  // Send a message
  const handleSendMessage = async (content: string, selectedText?: string) => {
    if (!conversationId || !content.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await chatApi.sendMessage(conversationId, {
        content: content.trim(),
        selected_text: selectedText,
      });

      // Add both messages to state
      setMessages((prev) => [...prev, response.user_message, response.assistant_message]);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  // Clear conversation and start fresh
  const handleClearConversation = async () => {
    try {
      // Create new conversation
      const conversation = await chatApi.createConversation({
        source: 'docusaurus_chat_widget',
      });

      setConversationId(conversation.id);
      setMessages([]);
      setError(null);
      localStorage.setItem('far_conversation_id', conversation.id);
    } catch (err) {
      console.error('Failed to clear conversation:', err);
      setError('Failed to clear conversation');
    }
  };

  return (
    <div className="chat-widget">
      <ChatButton onClick={() => setIsOpen(!isOpen)} isOpen={isOpen} />
      {isOpen && (
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSendMessage={handleSendMessage}
          onClearConversation={handleClearConversation}
          onClose={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};
