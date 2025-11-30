/**
 * Chat API client for FAR Reference Book chatbot.
 *
 * Handles all HTTP communication with the FastAPI backend.
 */

// Get backend URL from Docusaurus siteConfig
const getBackendUrl = (): string => {
  if (typeof window !== 'undefined') {
    // Access Docusaurus siteConfig
    const siteConfig = (window as any).docusaurus?.siteConfig;
    if (siteConfig?.customFields?.backendUrl) {
      return siteConfig.customFields.backendUrl as string;
    }
  }
  // Fallback to localhost for development
  return 'http://localhost:8000';
};

const API_BASE_URL = getBackendUrl();

export interface Source {
  chunk_id: string;
  chapter: number;
  section: string;
  page?: number;
  relevance_score: number;
  excerpt: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  selected_text?: string | null;
  sources?: Source[] | null;
  token_count?: number | null;
  processing_time_ms?: number | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface CreateConversationRequest {
  source?: string;
  metadata?: Record<string, any>;
}

export interface SendMessageRequest {
  content: string;
  selected_text?: string;
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
}

class ChatAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async createConversation(
    request: CreateConversationRequest = {}
  ): Promise<Conversation> {
    const response = await fetch(`${this.baseUrl}/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to create conversation: ${response.statusText}`);
    }

    return response.json();
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await fetch(
      `${this.baseUrl}/conversations/${conversationId}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get conversation: ${response.statusText}`);
    }

    return response.json();
  }

  async getMessages(conversationId: string): Promise<Message[]> {
    const response = await fetch(
      `${this.baseUrl}/conversations/${conversationId}/messages`
    );

    if (!response.ok) {
      throw new Error(`Failed to get messages: ${response.statusText}`);
    }

    return response.json();
  }

  async sendMessage(
    conversationId: string,
    request: SendMessageRequest
  ): Promise<ChatResponse> {
    // Use simplified endpoint as workaround
    const response = await fetch(`${this.baseUrl}/chat/${conversationId}/messages/simple`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Failed to send message: ${response.statusText}`
      );
    }

    return response.json();
  }
}

export const chatApi = new ChatAPI();
